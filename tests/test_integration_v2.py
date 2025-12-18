#!/usr/bin/env python3
"""
Integration test for grape-recorder V2 pipeline
"""
import sys
import shutil
import logging
import numpy as np
from pathlib import Path
from datetime import datetime
import subprocess

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from grape_recorder.core.raw_reader import RawBinaryReader
from grape_recorder.core.decimation_pipeline import DecimationPipeline
from grape_recorder.core.daily_drf_packager import StationConfig, DailyDRFPackager

def setup_test_data(root: Path, date_str: str, channel: str):
    """Create dummy raw data."""
    # Create raw_archive/CHANNEL/YYYYMMDD
    channel_dir = channel.replace(' ', '_')
    day_dir = root / 'raw_archive' / channel_dir / date_str
    day_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate 10 minutes of data
    # 20 kHz complex64
    sample_rate = 20000
    samples_per_min = sample_rate * 60
    
    t = np.arange(samples_per_min) / sample_rate
    # 10 Hz tone + 500 Hz tone
    signal = 0.5 * np.exp(1j * 2 * np.pi * 10 * t) + \
             0.5 * np.exp(1j * 2 * np.pi * 500 * t)
    
    signal = signal.astype(np.complex64)
    
    # Write files
    start_ts = int(datetime.strptime(date_str, '%Y%m%d').timestamp())
    for i in range(10):
        ts = start_ts + i * 60
        bin_path = day_dir / f"{ts}.bin"
        with open(bin_path, 'wb') as f:
            f.write(signal.tobytes())
            
    print(f"Created dummy data in {day_dir}")

def test_integration():
    root = Path('/tmp/grape_integration_test')
    if root.exists():
        shutil.rmtree(root)
    root.mkdir()
    
    date_str = '20251214'
    channel = 'WWV 10 MHz'
    
    print("1. Setting up test data...")
    setup_test_data(root, date_str, channel)
    
    print("\n2. Testing DecimationPipeline...")
    pipeline = DecimationPipeline(root)
    pipeline.process_day(date_str, channel)
    
    # Verify DecimatedBuffer
    decimated_dir = root / 'products' / 'WWV_10_MHz' / 'decimated'
    if not (decimated_dir / f"{date_str}.bin").exists():
        print("FAIL: Decimated file not found")
        return
    
    # Check size
    size = (decimated_dir / f"{date_str}.bin").stat().st_size
    print(f"Decimated file size: {size} bytes")
    # Expected: 10 minutes * 600 samples * 8 bytes = 48000 bytes (plus padding for full day potentially)
    # The buffer creates a full day file, so it should be large
    
    print("\n3. Testing DRF Packaging...")
    station = StationConfig(callsign='TEST', grid_square='EM28', psws_station_id='TEST_1')
    packager = DailyDRFPackager(
        data_root=root, 
        station_config=station,
        channels=[(channel, 10e6)]
    )
    packager.package_day(date_str)
    
    # Verify DRF
    upload_dir = root / 'upload' / date_str
    if not upload_dir.exists():
        print("FAIL: Upload directory not found")
        return
    
    files = list(upload_dir.rglob('*.h5'))
    print(f"Found {len(files)} DRF files")
    
    if len(files) > 0:
        print("\nSUCCESS: Integration test passed!")
    else:
        print("\nFAIL: No DRF files generated")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    test_integration()
