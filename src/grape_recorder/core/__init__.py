"""
GRAPE Recorder Core Modules

Phase 3 data products pipeline:
- Decimation (20 kHz → 10 Hz)
- Spectrograms and power graphs
- Digital RF packaging
- PSWS upload preparation
"""

from .decimation import StatefulDecimator, DecimationPipeline
from .decimated_buffer import DecimatedBuffer, MinuteMetadata, DayMetadata
from .carrier_spectrogram import CarrierSpectrogramGenerator, SpectrogramConfig
from .phase3_product_engine import Phase3ProductEngine
from .phase3_products_service import Phase3ProductsService
from .daily_drf_packager import DailyDRFPackager, StationConfig
from .drf_batch_writer import DRFBatchWriter
from .solar_zenith_calculator import calculate_solar_zenith_for_day

__all__ = [
    'StatefulDecimator',
    'DecimationPipeline',
    'DecimatedBuffer',
    'MinuteMetadata',
    'DayMetadata',
    'CarrierSpectrogramGenerator',
    'SpectrogramConfig',
    'Phase3ProductEngine',
    'Phase3ProductsService',
    'DailyDRFPackager',
    'StationConfig',
    'DRFBatchWriter',
    'calculate_solar_zenith_for_day',
]
