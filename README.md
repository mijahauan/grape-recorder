# DEPRECATED: Integrated into hf-timestd

**This repository has been integrated into [hf-timestd](https://github.com/mijahauan/hf-timestd) as the `grape` module.**

## Migration

All grape-recorder functionality is now available via `hf-timestd grape` commands:

```bash
# Decimation
hf-timestd grape decimate --channel "WWV 10 MHz" --date 2026-01-02

# Spectrograms
hf-timestd grape spectrogram --channel "WWV 10 MHz" --date 2026-01-02

# Digital RF Packaging
hf-timestd grape package --date 2026-01-02 --callsign AC0G --grid EM28

# Upload to PSWS
hf-timestd grape upload --date 2026-01-02
```

## Why the Change?

- **Simpler deployment**: One package instead of two
- **No dependency conflicts**: Single installation
- **Unified configuration**: One config file
- **Better integration**: Direct access to hf-timestd internals
- **Consistent paths**: Follows timestd directory conventions

## Data Locations

- **Logs**: `/var/log/timestd/grape/`
- **Products**: `/var/lib/timestd/grape/`

---

For the original grape-recorder documentation, see the commit history or tags.
