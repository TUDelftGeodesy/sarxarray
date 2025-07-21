import numpy as np

# Standard data types in sarxarray:
_dtypes = dict(int=np.int32, float=np.float32, complex=np.complex64)

# Optimal memory size of a chunk, in MB
_memsize_chunk_mb = 100

# Configuration for reading metadata from DORIS .res files
# Regular expressions for reading metadata from DORIS4 files
RE_PATTERNS_DORIS4 = {
    "sar_processor": r"SAR_PROCESSOR:\s+(.+)",
    "product_type": r"Product type specifier:\s+(.+)",
    "pass_direction": r"Scene identification:.*?(ASCENDING|DESCENDING)",
    "wavelength": r"Radar_wavelength \(m\):\s+([\d\.E\+\-]+)",
    "pulse_repetition_frequency": (
        r"Pulse_Repetition_Frequency \(computed, Hz\):\s+([\d\.E\+\-]+)"
    ),
    "total_azimuth_bandwidth": r"Total_azimuth_band_width \(Hz\):\s+([\d\.E\+\-]+)",
    "range_time_first_pixel": (
        r"Range_time_to_first_pixel \(2way\) \(ms\):\s+([\d\.E\+\-]+)"
    ),
    "range_sampling_rate": r"Range_sampling_rate \(computed, MHz\):\s+([\d\.E\+\-]+)",
    "total_range_bandwidth": r"Total_range_band_width \(MHz\):\s+([\d\.E\+\-]+)",
    "weighting_azimuth": r"Weighting_azimuth:\s+(.+)",
    "weighting_range": r"Weighting_range:\s+(.+)",
    "first_pixel_azimuth_time": r"First_pixel_azimuth_time \(UTC\):\s+(.+)",
}
# Regular expressions for reading metadata from DORIS4 files
RE_PATTERNS_DORIS5 = {
    "sar_processor": r"SAR_PROCESSOR:\s+(.+)",
    "product_type": r"Product type specifier:\s+(.+)",
    "pass_direction": r"PASS:\s+(.+)",
    "swath": r"SWATH:\s+(.+)",
    "image_mode": r"IMAGE_MODE:\s+(.+)",
    "polarisation": r"polarisation:\s+(.+)",
    "range_pixel_spacing": r"rangePixelSpacing:\s+([\d\.E\+\-]+)",
    "azimuth_pixel_spacing": r"azimuthPixelSpacing:\s+([\d\.E\+\-]+)",
    "radar_frequency": r"RADAR_FREQUENCY \(HZ\):\s+([\d\.E\+\-]+)",
    "sensor_platform": r"Sensor platform mission identifer:\s+(.+)",
    "wavelength": r"Radar_wavelength \(m\):\s+([\d\.E\+\-]+)",
    "pulse_repetition_frequency_raw": (
        r"Pulse_Repetition_Frequency_raw_data\(TOPSAR\):\s+([\d\.E\+\-]+)"
    ),
    "pulse_repetition_frequency": (
        r"Pulse_Repetition_Frequency \(computed, Hz\):\s+([\d\.E\+\-]+)"
    ),
    "first_pixel_azimuth_time": r"First_pixel_azimuth_time \(UTC\):\s+(.+)",
    "azimuth_time_interval": r"Azimuth_time_interval \(s\):\s+([\d\.E\+\-]+)",
    "total_azimuth_bandwidth": r"Total_azimuth_band_width \(Hz\):\s+([\d\.E\+\-]+)",
    "weighting_azimuth": r"Weighting_azimuth:\s+(.+)",
    "range_time_first_pixel": (
        r"Range_time_to_first_pixel \(2way\) \(ms\):\s+([\d\.E\+\-]+)"
    ),
    "range_sampling_rate": r"Range_sampling_rate \(computed, MHz\):\s+([\d\.E\+\-]+)",
    "total_range_bandwidth": r"Total_range_band_width \(MHz\):\s+([\d\.E\+\-]+)",
    "weighting_range": r"Weighting_range:\s+(.+)",
    "dataformat": r"Dataformat:\s+(.+)",
    "deramp": r"deramp:\s+([\d\.E\+\-]+)",
    "reramp": r"reramp:\s+([\d\.E\+\-]+)",
    "esd_correct": r"ESD_correct:\s+([\d\.E\+\-]+)",
}
# Regular expressions for reading metadata from DORIS5 interferogram files
RE_PATTERNS_DORIS5_IFG = {
    "number_of_lines": r"Number of lines \(multilooked\):\s+(\d+)",
    "number_of_pixels": r"Number of pixels \(multilooked\):\s+(\d+)",
}
# Float keys in metadata. They are used to regulate the metadata read as strings
# Some of these are from DORIS5 only
META_FLOAT_KEYS = [
    "wavelength",
    "pulse_repetition_frequency",
    "total_azimuth_bandwidth",
    "range_time_first_pixel",
    "range_sampling_rate",
    "total_range_bandwidth",
    "range_pixel_spacing",  # from here DORIS5 only
    "azimuth_pixel_spacing",
    "radar_frequency",
    "pulse_repetition_frequency_raw",
    "azimuth_time_interval",
]
# Integer keys in metadata. They are used to regulate the metadata read as strings
META_INT_KEYS = [
    "deramp",  # from here DORIS5 only
    "reramp",
    "number_of_lines",
    "number_of_pixels",
    "esd_correct",
]
# Time formats for DORIS metadata
TIME_FORMAT_DORIS4 = "%d-%b-%Y %H:%M:%S.%f"
TIME_FORMAT_DORIS5 = "%Y-%b-%d %H:%M:%S.%f"
# Time stamp key
TIME_STAMP_KEY = "first_pixel_azimuth_time"
