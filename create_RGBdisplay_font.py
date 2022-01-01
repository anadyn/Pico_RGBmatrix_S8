# -*- coding: utf-8 -*-
"""
Helper function to create number fonts for RGB LED Matrix display.

See the spreadsheet RGB display mapping.xlsx
The numbers below define the active (turned on) pixels.

Copyright (c) 2021 Lars-Ove Jönsson
The work is licensed under GNU General Public License v3.0

"""

import numpy as np


no_of_data_rows=8
char_per_row=48


# define symbol in HEX for LED on
LED_on='1'  # red
#LED_on='2'  # blue
#LED_on='4'  # green
#LED_on='F'  # white


pixels_no_0=[[0,1,16,17,20,21,24,25],
             [0,6,11,17,20,21,24,25],
             [0,6,7,11,17,20,21,24,25],
             [6,7,8,9,10,11,20,21,24,25,36,37,38,47],
             [7,8,9,10,20,21,24,25,36,37,38,39,46,47],
             [20,21,24,25,38,39,40,45,46,47],
             [20,21,24,25,39,40,44,45],
             [20,21,24,25,40,41,44,45]]

pixels_no_1=[[8,9,28,29],
             [8,9,28,29],
             [6,7,8,9,17,28,29],
             [6,7,8,9,17,28,29,36,37,38,39,40,45,46,47],
             [7,8,9,28,29,36,37,38,39,40,45,46,47],
             [28,29,36,37],
             [28,29,36,37],
             [28,29,36,37]]

pixels_no_2=[[0,1,11,16,17,26,27,28],
             [0,1,11,6,16,17,27,28,29],
             [0,6,7,10,11,16,17,28,29],
             [6,7,8,9,10,11,17,18,28,29,36,37,38,39,40,41,44,45,46,47],
             [6,7,8,9,10,18,19,29,36,37,38,39,40,41,44,45,46,47],
             [18,19,20,40,41,45,46,47],
             [18,19,20,45,46,47],
             [19,20,21,36,46,47]]

pixels_no_3=[[0,11,20,21],
             [0,11,20,21],
             [0,6,10,11,16,17,19,20,21,36,37,38,39,46,47],
             [6,7,8,9,10,11,16,17,18,19,20,29,36,37,37,38,39,40,44,45,46,47],
             [6,7,8,9,10,18,19,27,28,29,36,37,38,39,40,44,45,46,47],
             [18,27,28,29,38,39,40,41,44,45,46],
             [18,19,29,39,40,41],
             [19,20,40,41]]

pixels_no_4=[[7,8,10,11,18,19,20,21,24,25,26,27,28,29],
             [8,9,10,11,18,19,24,25],
             [8,9,10,11,18,19,24,25],
             [9,10,11,18,19,25,26,36,37,38,39,40,41,47],
             [9,10,11,18,19,25,26,36,37,38,39,40,41,47],
             [18,19,25,26,27,38,39],
             [18,19,26,27,38,39],
             [18,19,27,28,36,37,38,39,40,41,44,45,46,47]]

pixels_no_5=[[6,17,20,21],
             [6,17,20,21],
             [6,17,20,21],
             [0,6,7,8,9,10,11,17,19,20,21,36,37,38,39,46,47],
             [0,6,7,8,9,10,11,17,19,20,25,26,36,37,38,39,40,45,46,47],
             [18,19,20,25,26,27,38,39,41,44,45,46],
             [18,19,25,26,27,28,29,39,40,41,44,45,46],
             [18,25,26,27,28,29,40,41]]

pixels_no_6=[[6,7,17,20,21,24,25],
             [6,7,20,21,24,25],
             [6,7,8,20,21,24,25],
             [0,7,8,9,10,11,19,20,21,24,25,26,36,37,38,47],
             [0,8,9,10,11,18,19,20,24,25,26,27,36,37,38,39,45,46,47],
             [18,19,24,25,26,27,28,29,38,39,40,45,46,47],
             [18,25,26,27,28,29,39,40,45,46],
             [25,26,40,41,44,45]]

pixels_no_7=[[0,11,18,29],
             [0,1,11,18,29],
             [0,1,11,16,17,18,19,29],
             [0,1,11,16,17,18,19,36,37],
             [0,1,6,7,8,9,10,11,16,17,18,19,36,37],
             [18,19,20,36,37],
             [18,19,20,36,37],
             [19,20,36,37,38]]

pixels_no_8=[[0,6,11,17,20,21,24,25],
             [0,6,11,17,20,21,24,25],
             [0,6,7,10,11,17,20,21,24,25],
             [6,7,8,9,10,11,19,20,25,26,36,37,38,47],
             [7,8,9,10,18,19,26,27,28,29,36,37,38,39,40,45,46,47],
             [18,19,26,27,28,29,38,39,40,41,44,45,46,47],
             [18,19,20,25,26,27,40,41,44,45],
             [19,20,25,26,40,41,44,45]]

pixels_no_9=[[0,1,16,17,19,20],
             [0,1,6,11,16,17,18,19,20,27,28,29],
             [0,6,7,10,11,17,18,19,20,26,27,28,29],
             [6,7,8,9,10,11,18,19,20,21,25,26,27,36,37,45,46,47],
             [7,8,9,10,19,20,21,25,26,36,37,38,45,46,47],
             [20,21,24,25,37,38,39],
             [20,21,24,25,38,39,40],
             [20,21,24,25,38,39,40]]


#input_data=pixels_no_0
#input_data=pixels_no_1
#input_data=pixels_no_2
#input_data=pixels_no_3
#input_data=pixels_no_4
#input_data=pixels_no_5
#input_data=pixels_no_6
#input_data=pixels_no_7
#input_data=pixels_no_8
input_data=pixels_no_9


for data_row in np.arange(no_of_data_rows):
    #print('row index = {}'.format(data_row))
    LED_data=np.array(list('0'*char_per_row))
    LED_string=''

    for element in input_data[data_row]:
        LED_data[element]=LED_on

    for i in np.arange(0,char_per_row,6):
        LED_string+='0x{}{}{}{}{}{},'.format(LED_data[i],LED_data[i+1],LED_data[i+2],
                                         LED_data[i+3],LED_data[i+4],LED_data[i+5])
        
    print(LED_string)
    print
