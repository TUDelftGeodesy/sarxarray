=====================================================
 SLAVE RESULTFILE:         slave.res

Created by:             
InSAR Processor:        Doris (Delft o-o Radar Interferometric Software)
Version:                version  4.13.1 (02-11-2021)
		     build 	Tue Nov  2 13:30:14 2021 (optimal)
FFTW library:           used
VECLIB library:         not used
LAPACK library:         not used
Compiled at:            Apr 26 2022 16:54:44
By GNU gcc:             4.8.4
File creation at:       Mon Mar  3 10:01:00 2025

 -------------------------------------------------------
| Delft Institute of Earth Observation & Space Systems  |
|          Delft University of Technology               |
|              http://doris.tudelft.nl                  |
|                                                       |
| Author: (c) TUDelft - DEOS Radar Group                |
 -------------------------------------------------------


Start_process_control
readfiles:		1
precise_orbits:		0
modify_orbits:		0
crop:			1
sim_amplitude:		0
master_timing:		0
oversample:		0
resample:		1
filt_azi:		0
filt_range:		0
NOT_USED:		0
End_process_control

tsx_dump_header2doris.py v1.0, doris software, 2009

*******************************************************************
*_Start_readfiles:
*******************************************************************
Volume file: 					TDX1_SAR__SSC______SM_S_SRA_20180323T171910_20180323T171918.xml
Volume_ID: 					Level 1B Product
Volume_identifier: 				TX-GS-DD-3302 Basic Product Specification 1.5
Volume_set_identifier: 				DUMMY
(Check)Number of records in ref. file: 		27445
SAR_PROCESSOR:                                  TX-GS-DD-3302
Product type specifier: 	                TDX-1
Logical volume generating facility: 		TS-X PGS NZ
Logical volume creation date: 			2017-10-17T17:52:19.154000Z
Location and date/time of product creation: 	2018-04-05T12:44:23.000000
Scene identification: 				Orbit: 43005 ASCENDING Mode: SM
Scene location: 		                lat: 52.5384 lon: 4.9083
Leader file:                                 	TDX1_SAR__SSC______SM_S_SRA_20180323T171910_20180323T171918.xml
Sensor platform mission identifer:         	TDX-1
Scene_centre_latitude:                     	5.25383813878825450E+01
Scene_centre_longitude:                    	4.90833789657157205E+00
Radar_wavelength (m):                      	0.031066581527999
First_pixel_azimuth_time (UTC):			23-Mar-2018 17:19:10.163000
Pulse_Repetition_Frequency (computed, Hz): 	3.43051038544788526E+03
Total_azimuth_band_width (Hz):             	2.76500000000000000E+03
Weighting_azimuth:                         	HAMMING
Xtrack_f_DC_constant (Hz, early edge):     	7.35163894414404240E+00
Xtrack_f_DC_linear (Hz/s, early edge):     	2.66469527097116224E+03
Xtrack_f_DC_quadratic (Hz/s/s, early edge): 	-9.74163531999429017E+07
Range_time_to_first_pixel (2way) (ms):     	3.909066443017814
Range_sampling_rate (computed, MHz):       	164.829163
Total_range_band_width (MHz):               	150.0
Weighting_range:                            	HAMMING

*******************************************************************
Datafile: 					IMAGE_HH_SRA_strip_007.cos
Dataformat: 				TSX_COSAR
Number_of_lines_original: 			27445
Number_of_pixels_original: 	                18238
*******************************************************************
* End_readfiles:_NORMAL
*******************************************************************


*******************************************************************
*_Start_leader_datapoints
*******************************************************************
 t(s)		X(m)		Y(m)		Z(m)
NUMBER_OF_DATAPOINTS: 			12

 62302 4.55138023245847039E+06 1.68847219525020686E+05 5.15821432953289896E+06
 62312 4.49578825149360951E+06 1.48582258846287295E+05 5.20722662838171516E+06
 62322 4.43962056752117071E+06 1.28380738035776449E+05 5.25560175427675154E+06
 62332 4.38288411567671411E+06 1.08245946313936234E+05 5.30333380724152923E+06
 62342 4.32558590581135452E+06 8.81811544674235047E+04 5.35041697027833201E+06
 62352 4.26773302213821374E+06 6.81896147654791566E+04 5.39684550134228356E+06
 62362 4.20933261549810600E+06 4.82745570197665729E+04 5.44261374348139018E+06
 62372 4.15039191390411137E+06 2.84391962239863678E+04 5.48771611666850932E+06
 62382 4.09091820940158376E+06 8.68672246261205146E+03 5.53214712592506316E+06
 62392 4.03091886495618662E+06 -1.09796933206117865E+04 5.57590135724357050E+06
 62402 3.97040131460008211E+06 -3.05569010730569607E+04 5.61897348063007742E+06
 62412 3.90937305325837154E+06 -5.00417739181764337E+04 5.66135824706325214E+06

*******************************************************************
* End_leader_datapoints:_NORMAL
*******************************************************************

   Current time: Mon Mar  3 10:01:00 2025


   *====================================================================*
   |                                                                    |
       Following part is appended at: Mon Mar  3 10:04:25 2025
                 Using Doris version  4.13.1 (02-11-2021)
		     build 	Tue Nov  2 13:30:14 2021          
   |                                                                    |
   *--------------------------------------------------------------------*



*******************************************************************
*_Start_crop:			slave step01
*******************************************************************
Data_output_file: 				image_crop.raw
Data_output_format: 				complex_short
First_line (w.r.t. original_image): 		3825
Last_line (w.r.t. original_image): 		6074
First_pixel (w.r.t. original_image): 		5345
Last_pixel (w.r.t. original_image): 		7596
Number of lines (non-multilooked): 		2250
Number of pixels (non-multilooked): 		2252
*******************************************************************
* End_crop:_NORMAL
*******************************************************************

   Current time: Mon Mar  3 10:04:26 2025


   *====================================================================*
   |                                                                    |
       Following part is appended at: Tue Mar  4 18:17:40 2025
                 Using Doris version  4.13.1 (02-11-2021)
		     build 	Tue Nov  2 13:30:14 2021          
   |                                                                    |
   *--------------------------------------------------------------------*



*******************************************************************
*_Start_resample:
*******************************************************************
Normalization_Lines:   	1 27445
Normalization_Pixels:  	1 18238
Shifted azimuth spectrum:             		1
Data_output_file:                     		slave_rsmp.raw
Data_output_format:                   		complex_real4
Interpolation kernel:                 		16 point truncated sinc
Output resampled coordinates:         		0
First_line (w.r.t. original_master):  		3793
Last_line (w.r.t. original_master):   		5542
First_pixel (w.r.t. original_master): 		5525
Last_pixel (w.r.t. original_master):  		7276
*******************************************************************
* End_resample:_NORMAL
*******************************************************************

   Current time: Tue Mar  4 18:18:10 2025
