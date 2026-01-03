#!/usr/bin/env python3
"""
GRAPE Recorder CLI - Command-line interface for data products

Commands:
---------
grape-recorder      Main entry point
grape-decimate      Decimate IQ (20/24 kHz) → 10 Hz
grape-spectrogram   Generate spectrograms
grape-package-drf   Package Digital RF for upload
grape-upload        Upload to PSWS repository
"""

import argparse
import logging
from pathlib import Path
from datetime import datetime, date, timedelta
import sys
import shutil

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def main():
    """Main entry point for grape-recorder."""
    parser = argparse.ArgumentParser(
        description='GRAPE Recorder - HF Time Signal Data Products'
    )
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose logging')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Decimate command
    dec_parser = subparsers.add_parser('decimate', help='Decimate IQ (20/24 kHz) → 10 Hz')
    dec_parser.add_argument('--data-root', required=True, help='Data root directory')
    dec_parser.add_argument('--channel', help='Channel name (e.g., "WWV 10 MHz")')
    dec_parser.add_argument('--date', help='Date to process (YYYY-MM-DD or YYYYMMDD)')
    dec_parser.add_argument('--all-channels', action='store_true',
                            help='Process all channels')
    
    # Spectrogram command
    spec_parser = subparsers.add_parser('spectrogram', help='Generate spectrograms')
    spec_parser.add_argument('--data-root', required=True, help='Data root directory')
    spec_parser.add_argument('--channel', help='Channel name')
    spec_parser.add_argument('--date', help='Date (YYYY-MM-DD or YYYYMMDD)')
    spec_parser.add_argument('--rolling', type=int, choices=[6, 12, 24],
                             help='Generate rolling spectrogram (hours)')
    spec_parser.add_argument('--grid', help='Receiver grid square for solar zenith')
    
    # Package DRF command
    drf_parser = subparsers.add_parser('package-drf', help='Package Digital RF')
    drf_parser.add_argument('--data-root', required=True, help='Data root directory')
    drf_parser.add_argument('--date', required=True, help='Date to package')
    drf_parser.add_argument('--callsign', required=True, help='Station callsign')
    drf_parser.add_argument('--grid', required=True, help='Grid square')
    drf_parser.add_argument('--station-id', help='PSWS station ID')
    
    # Upload command
    upload_parser = subparsers.add_parser('upload', help='Upload to PSWS')
    upload_parser.add_argument('--data-root', required=True, help='Data root directory')
    upload_parser.add_argument('--date', help='Date to upload (default: yesterday)')
    upload_parser.add_argument('--dry-run', action='store_true',
                               help='Show what would be uploaded')
    
    args = parser.parse_args()
    setup_logging(args.verbose)
    
    if args.command == 'decimate':
        return decimate_cmd(args)
    elif args.command == 'spectrogram':
        return spectrogram_cmd(args)
    elif args.command == 'package-drf':
        return package_drf_cmd(args)
    elif args.command == 'upload':
        return upload_cmd(args)
    else:
        parser.print_help()
        return 0


def decimate(args=None):
    """Entry point for grape-decimate command."""
    parser = argparse.ArgumentParser(
        description='Decimate 20/24 kHz IQ to 10 Hz'
    )
    parser.add_argument('--data-root', required=True, help='Data root directory')
    parser.add_argument('--channel', help='Channel name')
    parser.add_argument('--date', help='Date (YYYY-MM-DD or YYYYMMDD)')
    parser.add_argument('--all-channels', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    
    args = parser.parse_args(args)
    setup_logging(args.verbose)
    return decimate_cmd(args)


def decimate_cmd(args):
    """Execute decimation."""
    from .core.decimation_pipeline import DecimationPipeline
    
    data_root = Path(args.data_root)
    # Handle both input formats
    date_str = args.date or datetime.now().strftime('%Y-%m-%d')
    
    # Normalize date format for processing
    if len(date_str) == 8:
        date_str = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    
    logger.info(f"Decimating data for {date_str}")
    
    try:
        pipeline = DecimationPipeline(data_root)
        pipeline.process_day(date_str, channel=args.channel)
        logger.info("Decimation complete")
        return 0
    except Exception as e:
        logger.error(f"Decimation failed: {e}", exc_info=True)
        return 1


def spectrogram(args=None):
    """Entry point for grape-spectrogram command."""
    parser = argparse.ArgumentParser(
        description='Generate carrier spectrograms'
    )
    parser.add_argument('--data-root', required=True, help='Data root directory')
    parser.add_argument('--channel', required=True, help='Channel name')
    parser.add_argument('--date', help='Date (YYYY-MM-DD or YYYYMMDD)')
    parser.add_argument('--rolling', type=int, choices=[6, 12, 24])
    parser.add_argument('--grid', help='Receiver grid square')
    parser.add_argument('-v', '--verbose', action='store_true')
    
    args = parser.parse_args(args)
    setup_logging(args.verbose)
    return spectrogram_cmd(args)


def spectrogram_cmd(args):
    """Execute spectrogram generation."""
    from .core.carrier_spectrogram import CarrierSpectrogramGenerator
    
    data_root = Path(args.data_root)
    
    gen = CarrierSpectrogramGenerator(
        data_root=str(data_root),
        channel_name=args.channel,
        receiver_grid=args.grid or 'EM28'
    )
    
    if args.rolling:
        logger.info(f"Generating {args.rolling}h rolling spectrogram")
        gen.generate_rolling(hours=args.rolling)
    else:
        date_str = args.date or datetime.now().strftime('%Y%m%d')
        if '-' in date_str:
            date_str = date_str.replace('-', '')
        logger.info(f"Generating daily spectrogram for {date_str}")
        gen.generate_daily(date_str)
    
    logger.info("Spectrogram generation complete")
    return 0


def package_drf(args=None):
    """Entry point for grape-package-drf command."""
    parser = argparse.ArgumentParser(
        description='Package Digital RF for PSWS upload'
    )
    parser.add_argument('--data-root', required=True, help='Data root directory')
    parser.add_argument('--date', required=True, help='Date to package')
    parser.add_argument('--callsign', required=True, help='Station callsign')
    parser.add_argument('--grid', required=True, help='Grid square')
    parser.add_argument('--station-id', help='PSWS station ID')
    parser.add_argument('-v', '--verbose', action='store_true')
    
    args = parser.parse_args(args)
    setup_logging(args.verbose)
    return package_drf_cmd(args)


def package_drf_cmd(args):
    """Execute DRF packaging."""
    from .core.daily_drf_packager import DailyDRFPackager, StationConfig
    
    data_root = Path(args.data_root)
    date_str = args.date
    if '-' in date_str:
        date_str = date_str.replace('-', '')
    
    station_config = StationConfig(
        callsign=args.callsign,
        grid_square=args.grid,
        psws_station_id=args.station_id or f"{args.callsign}_1"
    )
    
    packager = DailyDRFPackager(
        data_root=str(data_root),
        station_config=station_config
    )
    
    logger.info(f"Packaging DRF for {date_str}")
    packager.package_day(date_str)
    
    logger.info("DRF packaging complete")
    return 0


def upload(args=None):
    """Entry point for grape-upload command."""
    parser = argparse.ArgumentParser(
        description='Upload to PSWS repository'
    )
    parser.add_argument('--data-root', required=True, help='Data root directory')
    parser.add_argument('--date', help='Date to upload (default: yesterday)')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    
    args = parser.parse_args(args)
    setup_logging(args.verbose)
    return upload_cmd(args)



def cleanup_handler(task):
    """
    Cleanup handler called after successful upload.
    Deletes Digital RF data (except token) and decimated binary files.
    """
    try:
        dataset_path = Path(task.dataset_path)
        logger.info(f"Cleanup: Processing {dataset_path}")
        
        # 1. Digital RF cleanup
        # Delete everything inside the OBS directory EXCEPT .upload_complete
        if dataset_path.exists() and dataset_path.is_dir():
            for item in dataset_path.iterdir():
                if item.name == '.upload_complete':
                    continue
                try:
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
                except Exception as e:
                    logger.warning(f"Failed to delete {item}: {e}")
            logger.info(f"Cleanup: Digital RF data removed from {dataset_path.name}")
            
        # 2. Decimated binary cleanup
        # Need date from metadata to find binary files
        # task.metadata['date'] -> YYYY-MM-DD
        if 'date' in task.metadata:
            date_str = task.metadata['date'].replace('-', '')
            # Scan products directory for this date
            # data_root is not directly available in task, but dataset_path is in upload/YYYYMMDD/...
            # So products is likely ../../../../../products
            
            # Robust way: navigate up from dataset_path to find 'upload', then switch to 'products'
            # upload_dir/DATE/STATION/RECEIVER/OBS/
            # So dataset_path.parent.parent.parent.parent is likely 'upload' parent (data_root)
            
            # Or assume standard structure if we can't infer
            # Best effort: look for 'products' sibling to 'upload'
            upload_root = None
            p = dataset_path
            for _ in range(5):
                if p.name == 'upload':
                    upload_root = p
                    break
                p = p.parent
            
            if upload_root:
                data_root = upload_root.parent
                products_dir = data_root / 'products'
                
                if products_dir.exists():
                    cleaned_channels = 0
                    for channel_dir in products_dir.iterdir():
                        if not channel_dir.is_dir(): continue
                        decimated_dir = channel_dir / 'decimated'
                        if not decimated_dir.exists(): continue
                        
                        # Look for {DATE}.bin and {DATE}.json
                        bin_file = decimated_dir / f"{date_str}.bin"
                        json_file = decimated_dir / f"{date_str}.json"
                        
                        if bin_file.exists():
                            bin_file.unlink()
                            cleaned_channels += 1
                        if json_file.exists():
                            json_file.unlink()
                            
                    logger.info(f"Cleanup: Removed decimated files for {cleaned_channels} channels")
                else:
                    logger.warning(f"Cleanup: Could not find products directory at {products_dir}")
            else:
                 logger.warning("Cleanup: Could not locate data root from dataset path")
                 
    except Exception as e:
        logger.error(f"Cleanup handler failed: {e}", exc_info=True)


def upload_cmd(args):
    """Execute upload."""
    import shutil # For cleanup handler
    from .uploader import UploadManager, load_upload_config_from_toml
    
    data_root = Path(args.data_root)
    
    # Default to yesterday
    if args.date:
        date_str = args.date
    else:
        yesterday = date.today() - timedelta(days=1)
        date_str = yesterday.strftime('%Y-%m-%d')
    
    logger.info(f"Uploading data for {date_str}")
    
    if args.dry_run:
        logger.info("DRY RUN - no files will be uploaded")
        # TODO: Show what would be uploaded
        return 0
    
    # Load configuration
    # Try to load from standard locations or use defaults
    config_path = Path('/etc/hf-timestd/timestd-config.toml')
    toml_config = {}
    if config_path.exists():
        import toml
        try:
            toml_config = toml.load(config_path)
            logger.info(f"Loaded config from {config_path}")
        except Exception as e:
            logger.warning(f"Failed to load config: {e}")
    
    # Initialize implementation
    try:
        
        # Override data root if provided strings
        if 'recorder' not in toml_config:
            toml_config['recorder'] = {}
            
        # Manually construct config for UploadManager
        upload_config = load_upload_config_from_toml(toml_config)
        
        # Pass cleanup handler
        manager = UploadManager(
            upload_config, 
            storage_manager=None,
            on_success_callback=cleanup_handler
        )
        
        # Package for upload first? Or assume it's done?
        # The logic here assumes data is already packaged in products/{CHANNEL}/drf
        # We need to find those directories and enqueue them.
        
        upload_dir = data_root / 'upload' / date_str
        if not upload_dir.exists():
             logger.warning(f"No upload directory found at {upload_dir}")
             # Check for legacy or alternative paths if needed
             return 0
             
        # Find all channel directories
        # Expected: upload/{YYYYMMDD}/{CALLSIGN}_{GRID}/{RECEIVER}@{ID}/OBS.../ch0/
        # Enqueue the OBSERVATION directory (OBS...)
        
        enqueued_count = 0
        for station_dir in upload_dir.iterdir():
            if not station_dir.is_dir(): continue
            for receiver_dir in station_dir.iterdir():
                if not receiver_dir.is_dir(): continue
                for obs_dir in receiver_dir.iterdir():
                    if obs_dir.is_dir() and obs_dir.name.startswith('OBS'):
                        # Found an observation directory
                        
                        # Metadata construction
                        meta = {
                            'date': date_str,
                            'callsign': station_dir.name.split('_')[0],
                            'grid_square': station_dir.name.split('_')[1] if '_' in station_dir.name else '',
                            'station_id': receiver_dir.name.split('@')[1].split('_')[0] if '@' in receiver_dir.name else '',
                            'instrument_id': receiver_dir.name.split('_')[-1] if '_' in receiver_dir.name else '1'
                        }
                        
                        manager.enqueue(obs_dir, meta)
                        enqueued_count += 1
        
        if enqueued_count > 0:
            logger.info(f"Enqueued {enqueued_count} datasets for upload")
            manager.process_queue()
        else:
            logger.warning("No datasets found to enqueue")

    except Exception as e:
        logger.error(f"Upload failed: {e}", exc_info=True)
        return 1
    
    logger.info("Upload complete")
    return 0


if __name__ == '__main__':
    sys.exit(main())
