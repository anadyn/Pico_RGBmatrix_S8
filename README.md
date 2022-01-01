# Pico_RGBmatrix_S8
Raspberry Pi Pico controlling a LED matrix RGB display with 1/8 refresh rate (S8) using MicroPython.

![RGB Matrix display.](https://github.com/anadyn/Pico_RGBmatrix_S8/blob/main/RGBdisplay_front.jpg)

This repository contains MicroPython scripts for a Raspberry Pi Pico to display numbers on a LED Matrix RGB display. The scripts are written for two 24x48 displays put together with markings P5-48x24-2121RGB-8S-V1.0, i.e. in total 96 columns and 24 rows.

For an introduction on RGB Matrix panels I recommend this introduction (although you can skip the discussion of BCM and image planes, they are not applicable in this case):

[Sparkfun: Everything You Didn't Want to Know About RGB Matrix Panels](https://www.sparkfun.com/news/2650)

The protocol in this case is **not** hub75, but it works in a similar manner. Where hub75 writes and displays data for 1/16 or 1/32 of the rows at a time, here 1/8 of the rows are handled at the same time. This means that only three bits are needed to specify where the data is going. Furthermore, only one data channel is used instead of two that is used in hub75. 

A complication is that the pixels are defined in a wonky order. Since the display has 24 rows this means that 3 rows are handled at the same time by the shift registers, see the row indices 0 to 7 in the figure below.


![Ordering of pixels.](https://github.com/anadyn/Pico_RGBmatrix_S8/blob/main/example_ordering_of_pixels.png)


## Acknowledgements

The state machines controlling the display are based on the work by benevpi for hub75: [PicoPythonHub75](https://github.com/benevpi/PicoPythonHub75)

