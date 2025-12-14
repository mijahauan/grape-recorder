# GRAPE Recorder

**HF Time Signal Data Products for PSWS/HamSCI**

GRAPE Recorder processes WWV/WWVH/CHU time signal recordings to produce:
- **10 Hz decimated data** from 20 kHz IQ samples (phase-preserving)
- **Carrier spectrograms** with solar zenith overlays
- **Power graphs** for propagation analysis
- **Digital RF packages** for PSWS upload
- **Automated upload** to the GRAPE data repository

## Architecture

GRAPE Recorder is **Phase 3** of the three-phase HF time standard pipeline:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    HF TIME STANDARD PIPELINE                        │
├─────────────────────────────────────────────────────────────────────┤
│  Phase 1: Recording (hf-timestd)                                    │
│  ├─ RTP stream capture from ka9q-radio                              │
│  ├─ 20 kHz IQ archival in Digital RF format                         │
│  └─ GPSDO-disciplined timestamps                                    │
│                                                                     │
│  Phase 2: Timing Analysis (hf-timestd)                              │
│  ├─ WWV/WWVH/CHU tone detection                                     │
│  ├─ Station discrimination                                          │
│  ├─ D_clock extraction (UTC offset)                                 │
│  └─ Multi-broadcast fusion                                          │
│                                                                     │
│  Phase 3: Data Products (grape-recorder) ← THIS PACKAGE             │
│  ├─ 20 kHz → 10 Hz decimation                                       │
│  ├─ Carrier spectrograms + power graphs                             │
│  ├─ Digital RF packaging with timing annotations                    │
│  └─ PSWS/GRAPE repository upload                                    │
└─────────────────────────────────────────────────────────────────────┘
```

## Installation

```bash
# Install hf-timestd first (provides Phase 1 & 2)
pip install -e /path/to/hf-timestd

# Install grape-recorder
pip install -e /path/to/grape-recorder

# Or with Digital RF support
pip install -e /path/to/grape-recorder[drf]
```

## Quick Start

### Generate Daily Spectrogram

```bash
grape-spectrogram --data-root /var/lib/grape --channel "WWV 10 MHz" --date 2025-12-14
```

### Decimate and Package for Upload

```bash
# Decimate 20 kHz → 10 Hz
grape-decimate --data-root /var/lib/grape --date 2025-12-14

# Package as Digital RF
grape-package-drf --data-root /var/lib/grape --date 2025-12-14 \
    --callsign AC0G --grid EM28

# Upload to PSWS
grape-upload --data-root /var/lib/grape --date 2025-12-14
```

### Python API

```python
from grape_recorder import (
    DecimationPipeline,
    CarrierSpectrogramGenerator,
    DailyDRFPackager,
    UploadManager
)

# Generate spectrogram with solar zenith overlay
gen = CarrierSpectrogramGenerator(
    data_root='/var/lib/grape',
    channel_name='WWV 10 MHz',
    receiver_grid='EM28ww'
)
gen.generate_daily('20251214')

# Package for PSWS upload
packager = DailyDRFPackager(
    data_root='/var/lib/grape',
    station_config={
        'callsign': 'AC0G',
        'grid_square': 'EM28',
        'psws_station_id': 'S000171'
    }
)
packager.package_day('2025-12-14')
```

## Output Structure

```
products/{CHANNEL}/
├── decimated/
│   └── {YYYYMMDD}.bin          # 10 Hz IQ (864,000 samples/day)
│   └── {YYYYMMDD}_meta.json    # Per-minute timing metadata
├── spectrograms/
│   └── {YYYYMMDD}_daily.png    # 24h spectrogram + power + solar
│   └── rolling_6h.png          # Rolling 6-hour view
└── drf/
    └── {YYYYMMDD}/             # Digital RF for upload
        └── {CALLSIGN}_{GRID}/
            └── ch0/
                └── rf@*.h5
```

## Configuration

GRAPE Recorder reads configuration from `grape-config.toml`:

```toml
[station]
callsign = "AC0G"
grid_square = "EM28ww"
psws_station_id = "S000171"

[uploader]
protocol = "sftp"
host = "pswsnetwork.eng.ua.edu"

[uploader.sftp]
ssh_key = "~/.ssh/psws_key"
bandwidth_limit_kbps = 500
```

## Dependencies

- **hf-timestd** - Core recording and timing analysis
- **numpy**, **scipy** - Signal processing
- **matplotlib** - Visualization
- **digital_rf** - HDF5-based RF data format
- **paramiko** - SFTP upload

## License

MIT License - See LICENSE file

## Author

Michael James Hauan (AC0G)
