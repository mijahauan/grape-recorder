"""
GRAPE Recorder - HF Time Signal Data Products

Decimation, spectrograms, power graphs, Digital RF packaging, and PSWS upload
for WWV/WWVH/CHU time signal recordings.

This package depends on hf-timestd for:
- Raw IQ recording (Phase 1)
- Timing analysis and D_clock extraction (Phase 2)

GRAPE Recorder provides Phase 3 functionality:
- 20 kHz → 10 Hz decimation with phase preservation
- Carrier spectrograms with solar zenith overlays
- Power graphs for propagation analysis
- Digital RF packaging for PSWS/HamSCI upload
- Automated upload to GRAPE data repository
"""

__version__ = "0.1.0"
__author__ = "Michael James Hauan (AC0G)"

from .core.decimation import StatefulDecimator
from .core.decimation_pipeline import DecimationPipeline
from .core.decimated_buffer import DecimatedBuffer
from .core.carrier_spectrogram import CarrierSpectrogramGenerator
from .core.phase3_product_engine import Phase3ProductEngine
from .core.daily_drf_packager import DailyDRFPackager
from .uploader import UploadManager
from .upload_tracker import UploadTracker

__all__ = [
    'StatefulDecimator',
    'DecimationPipeline', 
    'DecimatedBuffer',
    'CarrierSpectrogramGenerator',
    'Phase3ProductEngine',
    'DailyDRFPackager',
    'UploadManager',
    'UploadTracker',
]
