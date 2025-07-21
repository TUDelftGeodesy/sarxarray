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
Volume file: 					TDX1_SAR__SSC______SM_S_SRA_20180312T171909_20180312T171917.xml
Volume_ID: 					Level 1B Product
Volume_identifier: 				TX-GS-DD-3302 Basic Product Specification 1.5
Volume_set_identifier: 				DUMMY
(Check)Number of records in ref. file: 		27445
SAR_PROCESSOR:                                  TX-GS-DD-3302
Product type specifier: 	                TDX-1
Logical volume generating facility: 		TS-X PGS NZ
Logical volume creation date: 			2017-10-17T17:52:19.154000Z
Location and date/time of product creation: 	2018-04-05T12:44:46.000000
Scene identification: 				Orbit: 42838 ASCENDING Mode: SM
Scene location: 		                lat: 52.5414 lon: 4.9094
Leader file:                                 	TDX1_SAR__SSC______SM_S_SRA_20180312T171909_20180312T171917.xml
Sensor platform mission identifer:         	TDX-1
Scene_centre_latitude:                     	5.25414272686397155E+01
Scene_centre_longitude:                    	4.90938175220494166E+00
Radar_wavelength (m):                      	0.031066581527999
First_pixel_azimuth_time (UTC):			12-Mar-2018 17:19:09.666000
Pulse_Repetition_Frequency (computed, Hz): 	3.43051038544788526E+03
Total_azimuth_band_width (Hz):             	2.76500000000000000E+03
Weighting_azimuth:                         	HAMMING
Xtrack_f_DC_constant (Hz, early edge):     	-2.61721143395984370E+01
Xtrack_f_DC_linear (Hz/s, early edge):     	-1.98853435990695871E+04
Xtrack_f_DC_quadratic (Hz/s/s, early edge): 	1.00498759383147601E+07
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

 62302 4.54834578276609443E+06 1.67850824700430705E+05 5.16088702519024536E+06
 62312 4.49272239074848033E+06 1.47589193938262586E+05 5.20986494404477999E+06
 62322 4.43652366878719721E+06 1.27391169159817538E+05 5.25820536196853500E+06
 62332 4.37975655693261791E+06 1.07260039404232433E+05 5.30590238391997572E+06
 62342 4.32242806813949533E+06 8.71990736449459073E+04 5.35295019594627246E+06
 62352 4.26454528942280356E+06 6.72115218699963298E+04 5.39934306200963818E+06
 62362 4.20611537875391357E+06 4.73006170795963044E+04 5.44507532715540007E+06
 62372 4.14714556413956545E+06 2.74695672680120369E+04 5.49014141836422402E+06
 62382 4.08764314463884337E+06 7.72156550262799010E+03 5.53453584362180531E+06
 62392 4.02761548620162252E+06 -1.19402182816642380E+04 5.57825319293438736E+06
 62402 3.96707002486912813E+06 -3.15126380155319639E+04 5.62128814131556265E+06
 62412 3.90601426152670244E+06 -5.09925648529593091E+04 5.66363544576604478E+06

*******************************************************************
* End_leader_datapoints:_NORMAL
*******************************************************************

   Current time: Mon Mar  3 10:01:00 2025


   *====================================================================*
   |                                                                    |
       Following part is appended at: Mon Mar  3 10:04:24 2025
                 Using Doris version  4.13.1 (02-11-2021)
		     build 	Tue Nov  2 13:30:14 2021          
   |                                                                    |
   *--------------------------------------------------------------------*



*******************************************************************
*_Start_crop:			slave step01
*******************************************************************
Data_output_file: 				image_crop.raw
Data_output_format: 				complex_short
First_line (w.r.t. original_image): 		3670
Last_line (w.r.t. original_image): 		5919
First_pixel (w.r.t. original_image): 		5268
Last_pixel (w.r.t. original_image): 		7519
Number of lines (non-multilooked): 		2250
Number of pixels (non-multilooked): 		2252
*******************************************************************
* End_crop:_NORMAL
*******************************************************************

   Current time: Mon Mar  3 10:04:25 2025


   *====================================================================*
   |                                                                    |
       Following part is appended at: Tue Mar  4 18:17:08 2025
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

   Current time: Tue Mar  4 18:17:40 2025
