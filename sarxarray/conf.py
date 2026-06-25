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
    "wavelength": r"Radar_wavelength \(m\):\s+([\d\.Ee\+\-]+)",
    "pulse_repetition_frequency": (
        r"Pulse_Repetition_Frequency \(computed, Hz\):\s+([\d\.Ee\+\-]+)"
    ),
    "total_azimuth_bandwidth": r"Total_azimuth_band_width \(Hz\):\s+([\d\.Ee\+\-]+)",
    "first_range_time": (
        r"Range_time_to_first_pixel \(2way\) \(ms\):\s+([\d\.Ee\+\-]+)"
    ),
    "range_sampling_rate": r"Range_sampling_rate \(computed, MHz\):\s+([\d\.Ee\+\-]+)",
    "total_range_bandwidth": r"Total_range_band_width \(MHz\):\s+([\d\.Ee\+\-]+)",
    "weighting_azimuth": r"Weighting_azimuth:\s+(.+)",
    "weighting_range": r"Weighting_range:\s+(.+)",
    "first_azimuth_time": r"First_pixel_azimuth_time \(UTC\):\s+(.+)",
}
# Regular expressions for reading metadata from DORIS5 files
RE_PATTERNS_DORIS5 = {
    "sar_processor": r"SAR_PROCESSOR:\s+(.+)",
    "product_type": r"Product type specifier:\s+(.+)",
    "pass_direction": r"PASS:\s+(.+)",
    "swath": r"SWATH:\s+(.+)",
    "image_mode": r"IMAGE_MODE:\s+(.+)",
    "polarisation": r"polarisation:\s+(.+)",
    "range_pixel_spacing": r"rangePixelSpacing:\s+([\d\.Ee\+\-]+)",
    "azimuth_pixel_spacing": r"azimuthPixelSpacing:\s+([\d\.Ee\+\-]+)",
    "radar_frequency": r"RADAR_FREQUENCY \(HZ\):\s+([\d\.Ee\+\-]+)",
    "sensor_platform": r"Sensor platform mission identifer:\s+(.+)",
    "wavelength": r"Radar_wavelength \(m\):\s+([\d\.Ee\+\-]+)",
    "pulse_repetition_frequency_raw": (
        r"Pulse_Repetition_Frequency_raw_data\(TOPSAR\):\s+([\d\.Ee\+\-]+)"
    ),
    "pulse_repetition_frequency": (
        r"Pulse_Repetition_Frequency \(computed, Hz\):\s+([\d\.Ee\+\-]+)"
    ),
    "first_azimuth_time": r"First_pixel_azimuth_time \(UTC\):\s+(.+)",
    "azimuth_time_interval": r"Azimuth_time_interval \(s\):\s+([\d\.Ee\+\-]+)",
    "total_azimuth_bandwidth": r"Total_azimuth_band_width \(Hz\):\s+([\d\.Ee\+\-]+)",
    "weighting_azimuth": r"Weighting_azimuth:\s+(.+)",
    "first_range_time": (
        r"Range_time_to_first_pixel \(2way\) \(ms\):\s+([\d\.Ee\+\-]+)"
    ),
    "range_sampling_rate": r"Range_sampling_rate \(computed, MHz\):\s+([\d\.Ee\+\-]+)",
    "total_range_bandwidth": r"Total_range_band_width \(MHz\):\s+([\d\.Ee\+\-]+)",
    "weighting_range": r"Weighting_range:\s+(.+)",
    "dataformat": r"Dataformat:\s+(.+)",
    "deramp": r"deramp:\s+([\d\.Ee\+\-]+)",
    "reramp": r"reramp:\s+([\d\.Ee\+\-]+)",
    "esd_correct": r"ESD_correct:\s+([\d\.Ee\+\-]+)",
    "orbit_txyz": (
        r"(\d+)\s+([-+]?\d+\.\d+(?:\.\d+)?)\s+([-+]?\d+"
        r"\.\d+(?:\.\d+)?)\s+([-+]?\d+\.\d+(?:\.\d+)?)"
    ),
    "scene_centre_latitude": (
        r"Scene_centre_latitude:"
        r"\s+([-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)"
    ),
    "scene_centre_longitude": (
        r"Scene_centre_longitude:"
        r"\s+([-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)"
    )
}
# Regular expressions for reading metadata from DORIS5 interferogram files
RE_PATTERNS_DORIS5_IFG = {
    "number_of_lines": r"Number of lines \(multilooked\):\s+(\d+)",
    "number_of_pixels": r"Number of pixels \(multilooked\):\s+(\d+)",
}
# Regular expressions for reading metadata from SNAP
RE_PATTERNS_SNAP = {
    "sar_processor": (
        r"[\d]+.Abstracted_Metadata.attributes.[\d]+.Processing_system_identifier"
    ),
    "product_type": r"[\d]+.Abstracted_Metadata.attributes.[\d]+.PRODUCT_TYPE",
    "orbit": r"[\d]+.Abstracted_Metadata.attributes.[\d]+.REL_ORBIT",
    "pass_direction": r"[\d]+.Abstracted_Metadata.attributes.[\d]+.PASS",
    "swath": r"[\d]+.Abstracted_Metadata.attributes.[\d]+.SWATH",
    "image_mode": r"[\d]+.Abstracted_Metadata.attributes.[\d]+.ACQUISITION_MODE",
    "polarisations": (
        r"[\d]+.Abstracted_Metadata.attributes.[\d]+.mds[\d]+_tx_rx_polar"
    ),
    "range_pixel_spacing": r"[\d]+.Abstracted_Metadata.attributes.[\d]+.range_spacing",
    "azimuth_pixel_spacing": (
        r"[\d]+.Abstracted_Metadata.attributes.[\d]+.azimuth_spacing"
    ),
    "radar_frequency": r"[\d]+.Abstracted_Metadata.attributes.[\d]+.radar_frequency",
    "sensor_platform": r"[\d]+.Abstracted_Metadata.attributes.[\d]+.MISSION",
    "pulse_repetition_frequency": (
        r"[\d]+.Abstracted_Metadata.attributes.[\d]+.pulse_repetition_frequency"
    ),
    "first_azimuth_time": (
        r"[\d]+.Abstracted_Metadata.attributes.[\d]+.first_line_time"
    ),
    "azimuth_time_interval": (
        r"[\d]+.Abstracted_Metadata.attributes.[\d]+.line_time_interval"
    ),
    "total_azimuth_bandwidth": (
        r"[\d]+.Abstracted_Metadata.attributes.[\d]+.azimuth_bandwidth"
    ),
    "weighting_azimuth": r"[\d]+.Abstracted_Metadata.attributes.[\d]+.azimuth_looks",
    "first_range_time": (
        r"[\d]+.Abstracted_Metadata.attributes.[\d]+.slrTimeToFirstValidPixel"
    ),
    "range_sampling_rate": (
        r"[\d]+.Abstracted_Metadata.attributes.[\d]+.range_sampling_rate"
    ),
    "total_range_bandwidth": (
        r"[\d]+.Abstracted_Metadata.attributes.[\d]+.range_bandwidth"
    ),
    "orbit_time": (
        r"[\d]+.Abstracted_Metadata.elements.[\d]+.Orbit_State_Vectors.elements."
        r"[\d]+.orbit_vector[\d]+.attributes.[\d]+.time"
    ),
    "orbit_position": (
        r"[\d]+.Abstracted_Metadata.elements.[\d]+.Orbit_State_Vectors.elements."
        r"[\d]+.orbit_vector[\d]+.attributes.[\d]+.[xyz]_pos"
    ),
    "orbit_velocity": (
        r"[\d]+.Abstracted_Metadata.elements.[\d]+.Orbit_State_Vectors.elements."
        r"[\d]+.orbit_vector[\d]+.attributes.[\d]+.[xyz]_vel"
    ),
    "scene_centre_latitude": r"[\d]+.Abstracted_Metadata.attributes.[\d]+.centre_lat",
    "scene_centre_longitude": r"[\d]+.Abstracted_Metadata.attributes.[\d]+.centre_lon",
    "number_of_lines": r"[\d]+.Abstracted_Metadata.attributes.[\d]+.num_output_lines",
    "number_of_pixels": (
        r"[\d]+.Abstracted_Metadata.attributes.[\d]+.num_samples_per_line"
    ),
    "first_pixel_number": (
        r"[\d]+.Abstracted_Metadata.attributes.[\d]+.subset_offset_x"
    ),
    "first_line_number": r"[\d]+.Abstracted_Metadata.attributes.[\d]+.subset_offset_y",
}
# Float keys in metadata. They are used to regulate the metadata read as strings
# Some of these are from DORIS5 only
META_FLOAT_KEYS = [
    "wavelength",
    "pulse_repetition_frequency",
    "total_azimuth_bandwidth",
    "first_range_time",
    "range_sampling_rate",
    "total_range_bandwidth",
    "range_pixel_spacing",  # from here DORIS5 only
    "azimuth_pixel_spacing",
    "radar_frequency",
    "pulse_repetition_frequency_raw",
    "azimuth_time_interval",
    "scene_centre_latitude",
    "scene_centre_longitude"
]
# Integer keys in metadata. They are used to regulate the metadata read as strings
META_INT_KEYS = [
    "deramp",  # from here DORIS5 only
    "reramp",
    "number_of_lines",
    "number_of_pixels",
    "esd_correct",
    "first_pixel_number",  # from here SNAP
    "first_line_number",
]
# Array keys in metadata and their format. Requires re.findall instead of re.match
# Expects 2D arrays, and a callable variable type as value associated with each key
META_ARRAY_KEYS = {
    "orbit_txyz": float,  # DORIS5 only
    "orbit_time": float,  # from here SNAP only
    "orbit_position": float,
    "orbit_velocity": float,
    "polarisations": str,
}
# SNAP returns flattened 1D arrays, so we need to tell it the shapes. The auto
# dimension gets expanded to the total number of inputs, and is required
META_ARRAY_SHAPES_SNAP = {
    "orbit_time": ("auto", 1),
    "orbit_position": ("auto", 3),
    "orbit_velocity": ("auto", 3),
    "polarisations": ("auto", 1),
}
# Some keys are not read in in SI units. The following dictionary specifies those
# keys, and the factor they should be multiplied by to restore them to SI units
META_UNIT_CONVERSION_MULTIPLICATION_KEYS_DORIS4 = {
    "range_sampling_rate": 1_000_000,  # originally MHz
    "total_range_bandwidth": 1_000_000,  # originally MHz
    "first_range_time": 0.001,  # originally ms
}

META_UNIT_CONVERSION_MULTIPLICATION_KEYS_DORIS5 = {
    "range_sampling_rate": 1_000_000,  # originally MHz
    "total_range_bandwidth": 1_000_000,  # originally MHz
    "first_range_time": 0.001,  # originally ms
}

META_UNIT_CONVERSION_MULTIPLICATION_KEYS_SNAP = {
    "radar_frequency": 1_000_000, # originally MHz
}

# Time formats for DORIS metadata
TIME_FORMAT_DORIS4 = "%d-%b-%Y %H:%M:%S.%f"
TIME_FORMAT_DORIS5 = "%Y-%b-%d %H:%M:%S.%f"
TIME_FORMAT_SNAP = "timestamp"
# Time stamp key
TIME_STAMP_KEY = "first_azimuth_time"
