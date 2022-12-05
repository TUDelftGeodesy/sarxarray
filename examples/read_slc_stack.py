import numpy as np
from pathlib import Path

import sys
sys.path.append('..')
import sarxarray
import sarxarray.stack

if __name__ == "__main__":
    # Load SLCs
    path = Path('/mnt/c/Users/OuKu/Developments/MobyLe/data/nl_veenweiden_s1_asc_t088/')
    shape=(9914, 41174)
    f_slc = 'slc_srd_nl_veenweiden.raw' 
    dtype = np.dtype([('re', np.float32), ('im', np.float32)]) # rippl image_data.py, dtype_disk, complex_short
    # dtype = np.complex64
    list_slcs = [p/f_slc for p in path.rglob("????????")]
    
    stack = sarxarray.from_binary(list_slcs, shape, vlabel="complex", dtype=dtype)
    mrm = stack.slcstack.mrm()

    mrm_subset = mrm[5000:5500, 10000:10500]
    mrm_subset = mrm_subset.compute()

    from matplotlib import pyplot as plt
    fig, ax = plt.subplots()
    ax.imshow(mrm_subset)
    mrm_subset.plot(robust=True, ax=ax)
    fig.savefig('mrm.png')

    fig = plt.figure()
    plt.hist(mrm_subset.values.reshape(-1), bins=50)
    fig.savefig('mrm_hist.png')



    

