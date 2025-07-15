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
Volume file: 					TDX1_SAR__SSC______SM_S_SRA_20180301T171909_20180301T171917.xml
Volume_ID: 					Level 1B Product
Volume_identifier: 				TX-GS-DD-3302 Basic Product Specification 1.5
Volume_set_identifier: 				DUMMY
(Check)Number of records in ref. file: 		27445
SAR_PROCESSOR:                                  TX-GS-DD-3302
Product type specifier: 	                TDX-1
Logical volume generating facility: 		TS-X PGS NZ
Logical volume creation date: 			2017-10-17T17:52:19.154000Z
Location and date/time of product creation: 	2018-03-06T00:28:02.000000
Scene identification: 				Orbit: 42671 ASCENDING Mode: SM
Scene location: 		                lat: 52.5404 lon: 4.9117
Leader file:                                 	TDX1_SAR__SSC______SM_S_SRA_20180301T171909_20180301T171917.xml
Sensor platform mission identifer:         	TDX-1
Scene_centre_latitude:                     	5.25403896702452542E+01
Scene_centre_longitude:                    	4.91169807836006989E+00
Radar_wavelength (m):                      	0.031066581527999
First_pixel_azimuth_time (UTC):			01-Mar-2018 17:19:09.165000
Pulse_Repetition_Frequency (computed, Hz): 	3.43051038544788526E+03
Total_azimuth_band_width (Hz):             	2.76500000000000000E+03
Weighting_azimuth:                         	HAMMING
Xtrack_f_DC_constant (Hz, early edge):     	2.41981845346137447E+00
Xtrack_f_DC_linear (Hz/s, early edge):     	4.46245543458796601E+03
Xtrack_f_DC_quadratic (Hz/s/s, early edge): 	7.19985851891526859E+06
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

 62302 4.54565390398763027E+06 1.66999169776339724E+05 5.16327041988710873E+06
 62312 4.49000264294599462E+06 1.46741097980407678E+05 5.21221808975257352E+06
 62322 4.43377638706242945E+06 1.26546776289888294E+05 5.26052797065256443E+06
 62332 4.37698207913920376E+06 1.06419492451102196E+05 5.30819417063295189E+06
 62342 4.31962673732661083E+06 8.63625126599538489E+04 5.35521087966348976E+06
 62352 4.26171745061304327E+06 6.63790888915200194E+04 5.40157236473582126E+06
 62362 4.20326138097821828E+06 4.64724491459744822E+04 5.44727297688436788E+06
 62372 4.14426575942598144E+06 2.66458053971202098E+04 5.49230714407412708E+06
 62382 4.08473788887937600E+06 6.90234557394622334E+03 5.53666938034718670E+06
 62392 4.02468513945240527E+06 -1.27547612052560489E+04 5.58035427965794131E+06
 62402 3.96411494810806867E+06 -3.23223669644259026E+04 5.62335652003552299E+06
 62412 3.90303482084166678E+06 -5.17973467027826409E+04 5.66567086149285175E+06

*******************************************************************
* End_leader_datapoints:_NORMAL
*******************************************************************

   Current time: Mon Mar  3 10:01:00 2025


   *====================================================================*
   |                                                                    |
       Following part is appended at: Mon Mar  3 10:04:23 2025
                 Using Doris version  4.13.1 (02-11-2021)
		     build 	Tue Nov  2 13:30:14 2021          
   |                                                                    |
   *--------------------------------------------------------------------*



*******************************************************************
*_Start_crop:			slave step01
*******************************************************************
Data_output_file: 				image_crop.raw
Data_output_format: 				complex_short
First_line (w.r.t. original_image): 		3740
Last_line (w.r.t. original_image): 		5989
First_pixel (w.r.t. original_image): 		5195
Last_pixel (w.r.t. original_image): 		7446
Number of lines (non-multilooked): 		2250
Number of pixels (non-multilooked): 		2252
*******************************************************************
* End_crop:_NORMAL
*******************************************************************

   Current time: Mon Mar  3 10:04:24 2025


   *====================================================================*
   |                                                                    |
       Following part is appended at: Tue Mar  4 18:16:38 2025
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

   Current time: Tue Mar  4 18:17:08 2025
