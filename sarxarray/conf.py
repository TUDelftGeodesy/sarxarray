import numpy as np

# Standard data types in sarxarray:
_dtypes = dict(int=np.int32, float=np.float32, complex=np.complex64)

# Optimal memory size of a chunk, in MB
_memsize_chunk_mb = 100
