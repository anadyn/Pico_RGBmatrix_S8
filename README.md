# Pico_RGBmatrix_S8
Raspberry Pi Pico controlling a LED matrix RGB display with 1/8 refresh rate (S8) using MicroPython.

Script for Raspberry Pi Pico to control a RGB LED Matrix 96x24 S8 display.
The protocol is not hub75, but it is similar. The display shows a timer in format MM:SS.UU
where MM is minutes, SS is seconds, and UU is 1/100 second.

S8 means that 1/8 of the rows are written to and displayed at a time, i.e. are controlled by three bits, HA,HB and HC.
Only one data line is used to put data into the shift registers that controls whether a pixel is on or off.
By contrast, hub75 uses four or five bits to control which rows to write, and uses two data lines at the same time.

Data must be provided for the shift registers for 24/8=3 rows at a time. Since my display is 96 pixels wide, this means
that 3x96=288 pixels needs to be shifted into the shift registers each time.

Finally, the pixels are defined in a wonky order. The display is divided into six 16 pixel wide sections, that is then repeated.
This means that my display has six identical segments, which suits me well since I want to display six numbers.
The figure below illustrates the 16x24 pixels of a section. Given a row index from 0 to 7, each section is written starting
from the upper row first, then the middle, and finally the lowest row. The arrows indicates which rows are written for index=1.
The pixels are then filled in the order from 0 to 47 as indicated in the figure. 

            --------------------------------------------------------------
index  7	|14	15	16	17	 6	7	8	9	10	11	0	1	2	3	4	5 |
index  6	|14	15	16	17	 6	7	8	9	10	11	0	1	2	3	4	5 |
index  5	|14	15	16	17	 6	7	8	9	10	11	0	1	2	3	4	5 |
index  4	|14	15	16	17	 6	7	8	9	10	11	0	1	2	3	4	5 |
index  3	|14	15	16	17	 6	7	8	9	10	11	0	1	2	3	4	5 |
index  2	|14	15	16	17	 6	7	8	9	10	11	0	1	2	3	4	5 |
index  1	|14	15	16	17	 6	7	8	9	10	11	0	1	2	3	4	5 |  <- start here
index  0	|14	15	16	17	 6	7	8	9	10	11	0	1	2	3	4	5 |
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
