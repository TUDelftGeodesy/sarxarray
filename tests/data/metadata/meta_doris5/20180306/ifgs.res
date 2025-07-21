=====================================================
INTERFEROGRAM RESULTFILE:               ifgs.res
Created by:                             
InSAR Processor:                        Doris (Delft o-o Radar Interferometric Software)
Version:                                version  4.0.8 (04-09-2014)
		     build 	Tue Aug 25 11:04:54 2015 (optimal)
FFTW library:                           used
VECLIB library:                         not used
LAPACK library:                         not used
Compiled at:                            Dec  1 2015 15
By GNU gcc:                             4.8.4
File creation at:                       Tue Oct  1 18
 -------------------------------------------------------
| Delft Institute of Earth Observation & Space Systems  |
|          Delft University of Technology               |
|              http://doris.tudelft.nl                  |
|                                                       |
| Author: (c) TUDelft - DEOS Radar Group                |
 -------------------------------------------------------



Start_process_control
coarse_orbits:		1
coarse_correl:		0
fine_coreg:		0
timing_error:		0
dem_assist:		0
comp_coregpm:		0
interfero:		1
coherence:		1
comp_refphase:		0
subtr_refphase:		0
comp_refdem:		1
subtr_refdem:		1
filtphase:		0
unwrap:		0
est_orbits:		0
slant2h:		0
geocoding:		0
dinsar:		0
NOT_USED2:		0
End_process_control



******************************************************************* 
*_Start_coarse_orbits:
******************************************************************* 
Some info for pixel:                         3441, 12433 (not used)
Btemp:         [days]:   -2147483648    // Temporal baseline
Bperp          [m]:      -60.2          // Perpendicular baseline
Bpar           [m]:      -61.6          // Parallel baseline
Bh             [m]:      -85.5          // Horizontal baseline
Bv             [m]:      10.9           // Vertical baseline
B              [m]:      86.3           // Baseline (distance between sensors)
alpha          [deg]:    172.7          // Baseline orientation
theta          [deg]:    38.3           // look angle
inc_angle      [deg]:    43.6           // incidence angle
orbitconv      [deg]:    0.00133952     // angle between orbits
Height_amb     [m]:      294.8          // height = h_amb*phase/2pi (approximately)
Control point master (line,pixel,hei) =      (3441, 12433, 0)
Control point slave  (line,pixel,hei) =      (3442.97, 12721.7, 0)
Estimated translation slave w.r.t. master (slave-master):
Positive offsetL:                            slave image is to the bottom
Positive offsetP:                            slave image is to the right
Coarse_orbits_translation_lines:             2
Coarse_orbits_translation_pixels:            289
******************************************************************* 
* End_coarse_orbits:_NORMAL
******************************************************************* 



******************************************************************* 
*_Start_interfero:
******************************************************************* 
Data_output_file:                           cint.raw
Data_output_format:                         complex_real4
First_line (w.r.t. original_master):        1
Last_line (w.r.t. original_master):         6881
First_pixel (w.r.t. original_master):       1
Last_pixel (w.r.t. original_master):        24865
Multilookfactor_azimuth_direction:          1
Multilookfactor_range_direction:            1
Number of lines (multilooked):              6881
Number of pixels (multilooked):             24865
******************************************************************* 
* End_interfero:_NORMAL
******************************************************************* 



******************************************************************* 
*_Start_comp_refdem:
******************************************************************* 
Include_flatearth:                          No
DEM source file:                            /project/caroline/Share/dem/netherlands_srtm/netherlands_SRTM.raw
Min. of input DEM:                          -45.5321
Max. of input DEM:                          81.3304
Data_output_file:                           master_slave.crd
Data_output_format:                         real4
First_line (w.r.t. original_master):        1
Last_line (w.r.t. original_master):         6881
First_pixel (w.r.t. original_master):       1
Last_pixel (w.r.t. original_master):        24865
Multilookfactor_azimuth_direction:          1
Multilookfactor_range_direction:            1
Number of lines (multilooked):              6881
Number of pixels (multilooked):             24865
******************************************************************* 
* End_comp_refdem:_NORMAL
******************************************************************* 



******************************************************************* 
*_Start_subtr_refdem:
******************************************************************* 
Method:                                     NOT_USED
Additional_azimuth_shift:                   1
Additional_range_shift:                     1
Data_output_file:                           cint_srd.raw
Data_output_format:                         complex_real4
First_line (w.r.t. original_master):        1
Last_line (w.r.t. original_master):         6881
First_pixel (w.r.t. original_master):       1
Last_pixel (w.r.t. original_master):        24865
Multilookfactor_azimuth_direction:          1
Multilookfactor_range_direction:            1
Number of lines (multilooked):              6881
Number of pixels (multilooked):             24865
******************************************************************* 
* End_subtr_refdem:_NORMAL
******************************************************************* 



******************************************************************* 
*_Start_coherence:
******************************************************************* 
Method:                                     INCLUDE_REFDEM
Data_output_file:                           coherence.raw
Data_output_format:                         real4
First_line (w.r.t. original_master):        1
Last_line (w.r.t. original_master):         6881
First_pixel (w.r.t. original_master):       1
Last_pixel (w.r.t. original_master):        24865
Multilookfactor_azimuth_direction:          1
Multilookfactor_range_direction:            1
Number of lines (multilooked):              6881
Number of pixels (multilooked):             24865
******************************************************************* 
* End_coherence:_NORMAL
******************************************************************* 
