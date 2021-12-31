"""

Script for Raspberry Pi Pico to control a RGB LED Matrix 96x24 S8 display.

An internal timer shows timestamps on the RGB LED display on the format "MM:SS.UU",
where MM=minutes, SS=seconds and UU is 1/100 second. For example 01:03.45

The protocol is not hub75, but it is similar. S8 means that 1/8 of the rows are written to and displayed at a time,
i.e. are controlled by three bits, HA,HB and HC. Only one data line is used to put data into the shift registers that
controls whether a pixel is on or off. By contrast, hub75 uses four or five bits to control which rows to write, and
uses two data lines at the same time.

Data must be provided for the shift registers for 24/8=3 rows at a time. Since my display is 96 pixels wide, this means
that 3x96=288 pixels needs to be shifted into the shift registers each time.

Finally, the pixels are defined in a wonky order. The display is divided into six 16 pixel wide sections, that is then repeated.
This means that my display has six identical segments, which suits me well since I want to display six numbers.
The figure below illustrates the 16x24 pixels of a section. Given a row index from 0 to 7, each section is written starting
from the upper row first, then the middle, and finally the lowest row. The arrows indicates which rows are written for index=1.
The pixels are then filled in the order from 0 to 47 as indicated in the figure. 

            --------------------------------------------------------------
index  7	|14	15	16	17	6	7	8	9	10	11	0	1	2	3	4	5 |
index  6	|14	15	16	17	6	7	8	9	10	11	0	1	2	3	4	5 |
index  5	|14	15	16	17	6	7	8	9	10	11	0	1	2	3	4	5 |
index  4	|14	15	16	17	6	7	8	9	10	11	0	1	2	3	4	5 |
index  3	|14	15	16	17	6	7	8	9	10	11	0	1	2	3	4	5 |
index  2	|14	15	16	17	6	7	8	9	10	11	0	1	2	3	4	5 |
index  1	|14	15	16	17	6	7	8	9	10	11	0	1	2	3	4	5 |  <- start here
index  0	|14	15	16	17	6	7	8	9	10	11	0	1	2	3	4	5 |
            --------------------------------------------------------------
index  7	|34	35	24	25	26	27	28	29	18	19	20	21	22	23	12	13|
index  6	|34	35	24	25	26	27	28	29	18	19	20	21	22	23	12	13|
index  5	|34	35	24	25	26	27	28	29	18	19	20	21	22	23	12	13|
index  4	|34	35	24	25	26	27	28	29	18	19	20	21	22	23	12	13|
index  3	|34	35	24	25	26	27	28	29	18	19	20	21	22	23	12	13|
index  2	|34	35	24	25	26	27	28	29	18	19	20	21	22	23	12	13|
index  1	|34	35	24	25	26	27	28	29	18	19	20	21	22	23	12	13|  <- then here
index  0	|34	35	24	25	26	27	28	29	18	19	20	21	22	23	12	13|
            --------------------------------------------------------------
index  7	|42	43	44	45	46	47	36	37	38	39	40	41	30	31	32	33|
index  6	|42	43	44	45	46	47	36	37	38	39	40	41	30	31	32	33|
index  5	|42	43	44	45	46	47	36	37	38	39	40	41	30	31	32	33|
index  4	|42	43	44	45	46	47	36	37	38	39	40	41	30	31	32	33|
index  3	|42	43	44	45	46	47	36	37	38	39	40	41	30	31	32	33|
index  2	|42	43	44	45	46	47	36	37	38	39	40	41	30	31	32	33|
index  1	|42	43	44	45	46	47	36	37	38	39	40	41	30	31	32	33|  <- finally here
index  0	|42	43	44	45	46	47	36	37	38	39	40	41	30	31	32	33|
         --------------------------------------------------------------


Copyright (c) 2021 Lars-Ove Jönsson
The work is available under GNU General Public License v3.0

"""

import rp2
from machine import Pin
from machine import Timer
from machine import UART
import _thread
import utime
import array



# pin layout

# pin for clock pulse of shift register
pin_clock=8

# Data pins (colour R,G,B) are 2,3,4. In addition pin 5 is used, but only to get 1 byte per pixel 
pin_data_start=2

# OE = Output enable. Light LEDs when pulled low. Here pin 17
# ST = strobe. Read to shift registers when low.  Here pin 18
pin_OE_ST_start=17

# pins for row select. This display writes 1/8 of total number of rows, i.e. 3 bits
# HA=10 (least significant bit) HB=11, HC=12
row_pin_start=10

# serial communication through UART0, TX=0, RX=1  <- not used

# define function for state machine to shift data to display
@rp2.asm_pio(out_shiftdir=1, autopull=True, pull_thresh=24,
             out_init=(rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW,rp2.PIO.OUT_LOW),
             sideset_init=(rp2.PIO.OUT_LOW),fifo_join=rp2.PIO.JOIN_TX)
def send_data_to_display():
    # use autopull, send one byte at a time to shift registers
    out(pins, 4)
    nop()        .side(1)
    nop()        .side(0)


# define function for state machine to choose active row
@rp2.asm_pio(out_shiftdir=1, autopull=False,out_init=(rp2.PIO.OUT_LOW,rp2.PIO.OUT_LOW,rp2.PIO.OUT_LOW),sideset_init=(rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW))
def choose_row():
    wrap_target()
    pull()              # get row number
    nop()     .side(1) 
    out(pins, 5)   [2]
    nop()      .side(3)
    nop()      .side(1)
    nop()      .side(0) 


# define state machines
sm_send_data_to_display=rp2.StateMachine(0,send_data_to_display, out_base=Pin(pin_data_start), sideset_base=Pin(pin_clock), freq=10000000)
sm_choose_row = rp2.StateMachine(1, choose_row, out_base=Pin(row_pin_start),sideset_base=Pin(pin_OE_ST_start), freq=1000000)

# setup serial communication <- not used
#uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))

# Font definition
# Define font of numbers 0 to 9
# The numbers are 16 pixels wide
# 0x110000 defines six pixels, 0 means off, 1 means red pixel. For blue: exchange all "1" to "2", for green to "4", for white to "F" 
numbers_font=[
     [  [0x110000,0x000000,0x000011,0x001100,0x110000,0x000000,0x000000,0x000000],   # character "0"
        [0x100000,0x100001,0x000001,0x001100,0x110000,0x000000,0x000000,0x000000],
        [0x100000,0x110001,0x000001,0x001100,0x110000,0x000000,0x000000,0x000000],
        [0x000000,0x111111,0x000000,0x001100,0x110000,0x000000,0x111000,0x000001],
        [0x000000,0x011110,0x000000,0x001100,0x110000,0x000000,0x111100,0x000011],
        [0x000000,0x000000,0x000000,0x001100,0x110000,0x000000,0x001110,0x000111],
        [0x000000,0x000000,0x000000,0x001100,0x110000,0x000000,0x000110,0x001100],
        [0x000000,0x000000,0x000000,0x001100,0x110000,0x000000,0x000011,0x001100]  ],

     [  [0x000000,0x001100,0x000000,0x000000,0x000011,0x000000,0x000000,0x000000],   # character "1"
        [0x000000,0x001100,0x000000,0x000000,0x000011,0x000000,0x000000,0x000000],
        [0x000000,0x111100,0x000001,0x000000,0x000011,0x000000,0x000000,0x000000],
        [0x000000,0x111100,0x000001,0x000000,0x000011,0x000000,0x111110,0x000111],
        [0x000000,0x011100,0x000000,0x000000,0x000011,0x000000,0x111110,0x000111],
        [0x000000,0x000000,0x000000,0x000000,0x000011,0x000000,0x110000,0x000000],
        [0x000000,0x000000,0x000000,0x000000,0x000011,0x000000,0x110000,0x000000],
        [0x000000,0x000000,0x000000,0x000000,0x000011,0x000000,0x110000,0x000000]  ],

     [  [0x110000,0x000001,0x000011,0x000000,0x001110,0x000000,0x000000,0x000000],   # character "2"
        [0x110000,0x100001,0x000011,0x000000,0x000111,0x000000,0x000000,0x000000],
        [0x100000,0x110011,0x000011,0x000000,0x000011,0x000000,0x000000,0x000000],
        [0x000000,0x111111,0x000001,0x100000,0x000011,0x000000,0x111111,0x001111],
        [0x000000,0x111110,0x000000,0x110000,0x000001,0x000000,0x111111,0x001111],
        [0x000000,0x000000,0x000000,0x111000,0x000000,0x000000,0x000011,0x000111],
        [0x000000,0x000000,0x000000,0x111000,0x000000,0x000000,0x000000,0x000111],
        [0x000000,0x000000,0x000000,0x011100,0x000000,0x000000,0x100000,0x000011]  ],

     [  [0x100000,0x000001,0x000000,0x001100,0x000000,0x000000,0x000000,0x000000],   # character "3"
        [0x100000,0x000001,0x000000,0x001100,0x000000,0x000000,0x000000,0x000000],
        [0x100000,0x100011,0x000011,0x011100,0x000000,0x000000,0x000000,0x000000],
        [0x000000,0x111111,0x000011,0x111000,0x000001,0x000000,0x111100,0x000111],
        [0x000000,0x111110,0x000000,0x110000,0x000111,0x000000,0x111110,0x001111],
        [0x000000,0x000000,0x000000,0x100000,0x000111,0x000000,0x001111,0x001110],
        [0x000000,0x000000,0x000000,0x110000,0x000001,0x000000,0x000111,0x000000],
        [0x000000,0x000000,0x000000,0x011000,0x000000,0x000000,0x000011,0x000000]  ],

     [  [0x000000,0x011011,0x000000,0x111100,0x111111,0x000000,0x000000,0x000000],   # character "4"
        [0x000000,0x001111,0x000000,0x110000,0x110000,0x000000,0x000000,0x000000],
        [0x000000,0x001111,0x000000,0x110000,0x110000,0x000000,0x000000,0x000000],
        [0x000000,0x000111,0x000000,0x110000,0x011000,0x000000,0x111111,0x000001],
        [0x000000,0x000111,0x000000,0x110000,0x011000,0x000000,0x111111,0x000001],
        [0x000000,0x000000,0x000000,0x110000,0x011100,0x000000,0x001100,0x000000],
        [0x000000,0x000000,0x000000,0x110000,0x001100,0x000000,0x001100,0x000000],
        [0x000000,0x000000,0x000000,0x110000,0x000110,0x000000,0x111111,0x001111]  ],

     [  [0x000000,0x100000,0x000001,0x001100,0x000000,0x000000,0x000000,0x000000],   # character "5"
        [0x000000,0x100000,0x000001,0x001100,0x000000,0x000000,0x000000,0x000000],
        [0x000000,0x100000,0x000001,0x001100,0x000000,0x000000,0x000000,0x000000],
        [0x100000,0x111111,0x000001,0x011100,0x000000,0x000000,0x111100,0x000011],
        [0x100000,0x111111,0x000001,0x011000,0x011000,0x000000,0x111110,0x000111],
        [0x000000,0x000000,0x000000,0x111000,0x011100,0x000000,0x001111,0x001110],
        [0x000000,0x000000,0x000000,0x110000,0x011111,0x000000,0x000111,0x001110],
        [0x000000,0x000000,0x000000,0x100000,0x011111,0x000000,0x000011,0x000000]  ],

     [  [0x000000,0x110000,0x000001,0x001100,0x110000,0x000000,0x000000,0x000000],   # character "6"
        [0x000000,0x110000,0x000000,0x001100,0x110000,0x000000,0x000000,0x000000],
        [0x000000,0x111000,0x000000,0x001100,0x110000,0x000000,0x000000,0x000000],
        [0x100000,0x011111,0x000000,0x011100,0x111000,0x000000,0x111000,0x000001],
        [0x100000,0x001111,0x000000,0x111000,0x111100,0x000000,0x111100,0x000111],
        [0x000000,0x000000,0x000000,0x110000,0x111111,0x000000,0x001110,0x000111],
        [0x000000,0x000000,0x000000,0x100000,0x011111,0x000000,0x000110,0x000110],
        [0x000000,0x000000,0x000000,0x000000,0x011000,0x000000,0x000011,0x001100]  ],

     [  [0x100000,0x000001,0x000000,0x100000,0x000001,0x000000,0x000000,0x000000],   # character "7"
        [0x110000,0x000001,0x000000,0x100000,0x000001,0x000000,0x000000,0x000000],
        [0x110000,0x000001,0x000011,0x110000,0x000001,0x000000,0x000000,0x000000],
        [0x110000,0x111111,0x000011,0x110000,0x000000,0x000000,0x110000,0x000000],
        [0x110000,0x111111,0x000011,0x110000,0x000000,0x000000,0x110000,0x000000],
        [0x000000,0x000000,0x000000,0x111000,0x000000,0x000000,0x110000,0x000000],
        [0x000000,0x000000,0x000000,0x111000,0x000000,0x000000,0x110000,0x000000],
        [0x000000,0x000000,0x000000,0x011000,0x000000,0x000000,0x111000,0x000000]  ],

     [  [0x100000,0x100001,0x000001,0x001100,0x110000,0x000000,0x000000,0x000000],   # character "8"
        [0x100000,0x100001,0x000001,0x001100,0x110000,0x000000,0x000000,0x000000],
        [0x100000,0x110011,0x000001,0x001100,0x110000,0x000000,0x000000,0x000000],
        [0x000000,0x111111,0x000000,0x011000,0x011000,0x000000,0x111000,0x000001],
        [0x000000,0x011110,0x000000,0x110000,0x001111,0x000000,0x111110,0x000111],
        [0x000000,0x000000,0x000000,0x110000,0x001111,0x000000,0x001111,0x001111],
        [0x000000,0x000000,0x000000,0x111000,0x011100,0x000000,0x000011,0x001100],
        [0x000000,0x000000,0x000000,0x011000,0x011000,0x000000,0x000011,0x001100]  ],

     [  [0x110000,0x000000,0x000011,0x011000,0x000000,0x000000,0x000000,0x000000],   # character "9"
        [0x110000,0x100001,0x000011,0x111000,0x000111,0x000000,0x000000,0x000000],
        [0x100000,0x110011,0x000001,0x111100,0x001111,0x000000,0x000000,0x000000],
        [0x000000,0x111111,0x000000,0x111100,0x011100,0x000000,0x110000,0x000111],
        [0x000000,0x011110,0x000000,0x011100,0x011000,0x000000,0x111000,0x000111],
        [0x000000,0x000000,0x000000,0x001100,0x110000,0x000000,0x011100,0x000000],
        [0x000000,0x000000,0x000000,0x001100,0x110000,0x000000,0x001110,0x000000],
        [0x000000,0x000000,0x000000,0x001100,0x110000,0x000000,0x001110,0x000000]  ]
]


def pixel_data_from_string(display_string):

    pixels_data=[ [],[],[],[],[],[],[],[] ]

    for char in reversed(display_string):
        display_no=int(char)
        print(display_no)
        for index in range(8):
            pixels_data[index]+=numbers_font[display_no][index]

    # number format 00:00.00
    # add colon
    pixels_data[0][4*8+2]=pixels_data[0][4*8+2]|0x110000
    pixels_data[1][4*8+2]=pixels_data[1][4*8+2]|0x110000
    pixels_data[6][4*8+2]=pixels_data[6][4*8+2]|0x110000
    pixels_data[7][4*8+2]=pixels_data[7][4*8+2]|0x110000
    # add decimal point
    pixels_data[3][2*8+5]=pixels_data[3][2*8+5]|0x001100
    pixels_data[4][2*8+5]=pixels_data[4][2*8+5]|0x001100

    return pixels_data


def timer_callback(t):
    # updates display if internal timer is used
    global total_seconds
    global pixels_out

    minutes=total_seconds//60
    seconds=total_seconds%60
    
    time_string='{:02}{:02}00'.format(minutes,seconds)
    pixels_out=pixel_data_from_string(time_string)
    print(time_string)
    total_seconds+=1


def read_timestamp_from_uart():
    # reads timestamps from serial and updates display.
    # timestamp format: b"MMSSUU"
    # MM - minutes
    # SS - seconds
    # UU - hundreds of second

    global pixels_out

    while True:
        if uart.any():
            data=uart.read()
            if len(data)>5:
                try:
                    data_string=data[:6].decode()
                    pixels_out=pixel_data_from_string(data_string)
                except:
                    pass

        utime.sleep(0.01)


# activate state machines
sm_send_data_to_display.active(1)
sm_choose_row.active(1)


# initiate timer, used if no serial input
total_seconds=0
tim=Timer()
tim.init(period=1000, callback=timer_callback)

# initial string to display
display_string='000000'
pixels_out=pixel_data_from_string(display_string)

# setup second core to read serial data and update display, i.e. pixels_out NOT USED
#_thread.start_new_thread(read_timestamp_from_uart, ())


while True:
    
    # loop through all 8 rows of data
    for row_index in range(8):

        # send data to shift registers, 3 bytes at a time
        for data in pixels_out[row_index]:
            sm_send_data_to_display.put(data)

        # trigger current row 
        sm_choose_row.put(row_index)


# finish script by turning off all LEDs
#for row_index in range(8):
#    sm_choose_row.put(row_index)
#    for i in range(48):
#        sm_send_data_to_display.put(0x000000)  # off
