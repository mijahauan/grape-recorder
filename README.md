# GRAPE Recorder

**HF Time Signal Data Products for PSWS/HamSCI**

GRAPE Recorder processes WWV/WWVH/CHU time signal recordings to produce:

- **10 Hz decimated data** from 24 kHz IQ samples (phase-preserving)
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
│  ├─ 24 kHz IQ archival in Digital RF format                         │
│  └─ GPSDO-disciplined timestamps                                    │
│                                                                     │
│  Phase 2: Timing Analysis (hf-timestd)                              │
│  ├─ WWV/WWVH/CHU tone detection                                     │
│  ├─ Station discrimination                                          │
│  ├─ D_clock extraction (UTC offset)                                 │
│  └─ Multi-broadcast fusion                                          │
│                                                                     │
│  Phase 3: Data Products (grape-recorder) ← THIS PACKAGE             │
│  ├─ 24 kHz → 10 Hz decimation                                       │
│  ├─ Carrier spectrograms + power graphs                             │
│  ├─ Digital RF packaging with timing annotations                    │
│  └─ PSWS/GRAPE repository upload                                    │
└─────────────────────────────────────────────────────────────────────┘
```

## Installation

### Prerequisites

- Python 3.9 or newer
- `hf-timestd` core package (Phase 1 & 2)

### Quick Install (Recommended)

Use the provided installation script:

```bash
cd /path/to/grape-recorder
./install.sh
```

The script will:

- Create `/opt/grape-recorder` with a virtual environment
- Install dependencies (including `hf-timestd` if available at `/opt/hf-timestd`)
- Create `/var/log/grape-recorder` for logs
- Create `/var/lib/grape-recorder` for data products
- Optionally create symlinks in `/usr/local/bin`

### Manual Installation

If you prefer manual installation:

```bash
# 1. Create directory and virtual environment
sudo mkdir -p /opt/grape-recorder
sudo python3 -m venv /opt/grape-recorder/venv

# 2. Install dependencies
# Note: hf-timestd is currently a local package and must be installed first
# Assuming hf-timestd is at /opt/hf-timestd
sudo /opt/grape-recorder/venv/bin/pip install -e /opt/hf-timestd

# 3. Install grape-recorder (from source)
cd /path/to/grape-recorder
sudo /opt/grape-recorder/venv/bin/pip install -e .[drf]

# 4. Create directories
sudo mkdir -p /var/log/grape-recorder /var/lib/grape-recorder
sudo chown $USER:$USER /var/log/grape-recorder /var/lib/grape-recorder
```

### Uninstall

To remove the installation:

```bash
cd /path/to/grape-recorder
./uninstall.sh
```

## Quick Start

### Generate Daily Spectrogram

```bash
/opt/grape-recorder/venv/bin/grape-spectrogram --channel "WWV 10 MHz" --date 2025-12-14
```

### Decimate and Package for Upload

```bash
# Decimate 24 kHz → 10 Hz
/opt/grape-recorder/venv/bin/grape-decimate --date 2025-12-14

# Package as Digital RF
/opt/grape-recorder/venv/bin/grape-package-drf --date 2025-12-14 \
    --callsign AC0G --grid EM28

# Upload to PSWS
/opt/grape-recorder/venv/bin/grape-upload --date 2025-12-14
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
    data_root='/var/lib/timestd',
    channel_name='WWV 10 MHz',
    receiver_grid='EM28ww'
)
gen.generate_daily('20251214')

# Package for PSWS upload
packager = DailyDRFPackager(
    data_root='/var/lib/timestd',
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

## Logging and Data Locations

### Logs
Logs are written to `/var/log/grape-recorder/grape-recorder.log` if the directory exists and is writable. Otherwise, logs are printed to standard output (stderr).

To create the log directory:
```bash
sudo mkdir -p /var/log/grape-recorder
sudo chown $USER:$USER /var/log/grape-recorder
```

If running as a systemd service, logs are also captured by journald:

- **View service logs**: `journalctl -u grape-recorder`
- **View live logs**: `journalctl -u grape-recorder -f`

### Data Products

All data products are stored in `/var/lib/grape-recorder`, organized by channel:

- **Decimated IQ**: `/var/lib/grape-recorder/products/{CHANNEL}/decimated/`
- **Spectrograms**: `/var/lib/grape-recorder/products/{CHANNEL}/spectrograms/`
- **Digital RF**: `/var/lib/grape-recorder/products/{CHANNEL}/drf/`

To create the data directory:

```bash
sudo mkdir -p /var/lib/grape-recorder
sudo chown $USER:$USER /var/lib/grape-recorder
```

```

## Configuration

GRAPE Recorder looks for `grape-config.toml` in the following locations (in order):

1. Current working directory
2. `~/.config/grape-recorder/grape-config.toml`
3. `/etc/grape-recorder/grape-config.toml`
4. `/etc/hf-timestd/timestd-config.toml` (Legacy)

Example configuration:

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
