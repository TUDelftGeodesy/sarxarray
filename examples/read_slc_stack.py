import numpy as np
from pathlib import Path
import sarxarray

if __name__ == "__main__":
    path = Path('/mnt/c/Users/OuKu/Developments/MobyLe/data/nl_veenweiden_s1_asc_t088/')
    f_slc = path/'20210407'/'slc_srd_nl_veenweiden.raw' 

    f_h2ph = path/'20210407'/'h2ph_nl_veenweiden.raw'

    shape=(9914, 41174)
    dtype = np.dtype([('re', np.float16), ('im', np.float16)]) # rippl image_data.py, dtype_disk, complex_short

    
    list_slcs = [p/'slc_srd_nl_veenweiden.raw' for p in path.rglob("????????")]

    stack = sarxarray.read_stack(list_slcs, shape, vlabel="complex", dtype=dtype)

    

