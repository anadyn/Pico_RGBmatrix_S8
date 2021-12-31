# Pico_RGBmatrix_S8
Raspberry Pi Pico controlling a LED matrix RGB display with 1/8 refresh rate (S8) using MicroPython.

![RGB Matrix display.](https://github.com/anadyn/Pico_RGBmatrix_S8/blob/main/RGBdisplay_front.jpg)

This repository contains MicroPython scripts for a Raspberry Pi Pico to display numbers on a LED Matrix RGB display. The scripts are written for two 24x48 displays put together with markings P5-48x24-2121RGB-8S-V1.0, i.e. in total 96 columns and 24 rows.

For an introduction on RGB Matrix panels I recommend this introduction:

[Sparkfun: Everything You Didn't Want to Know About RGB Matrix Panels](https://www.sparkfun.com/news/2650)

The protocol for the current displays is not hub75, but it works in a simular manner. 1/8 of the rows are written and displayed at the same time. Three bits are needed to choose the current row. Since the display has 24 rows, this means that data for 24/8=3 rows needs to be put into the shift registers each time, i.e. in total 96x3=288 pixels.



[PicoPythonHub75](https://github.com/benevpi/PicoPythonHub75) by benevpi.




![Ordering of pixels.](https://github.com/anadyn/Pico_RGBmatrix_S8/blob/main/example_ordering_of_pixels.png)



