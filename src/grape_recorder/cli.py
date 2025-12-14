#!/usr/bin/env python3
"""
GRAPE Recorder CLI - Command-line interface for data products

Commands:
---------
grape-recorder      Main entry point
grape-decimate      Decimate 20 kHz → 10 Hz
grape-spectrogram   Generate spectrograms
grape-package-drf   Package Digital RF for upload
grape-upload        Upload to PSWS repository
"""

import argparse
import logging
import sys
from datetime import datetime, date, timedelta
from pathlib import Path

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
    dec_parser = subparsers.add_parser('decimate', help='Decimate 20 kHz → 10 Hz')
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
        description='Decimate 20 kHz IQ to 10 Hz'
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
    from .core.decimation import DecimationPipeline
    
    data_root = Path(args.data_root)
    date_str = args.date or datetime.now().strftime('%Y-%m-%d')
    
    # Normalize date format
    if len(date_str) == 8:
        date_str = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    
    logger.info(f"Decimating data for {date_str}")
    
    # TODO: Implement full decimation pipeline
    # pipeline = DecimationPipeline(data_root)
    # pipeline.process_day(date_str, channel=args.channel)
    
    logger.info("Decimation complete")
    return 0


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


def upload_cmd(args):
    """Execute upload."""
    from .uploader import UploadManager
    
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
    
    # TODO: Implement upload
    # manager = UploadManager(config)
    # manager.upload_day(date_str)
    
    logger.info("Upload complete")
    return 0


if __name__ == '__main__':
    sys.exit(main())
