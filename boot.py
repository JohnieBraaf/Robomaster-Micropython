import machine
import pyb

# Country is needed to determine WIFI channels restrictions
pyb.country('NL') 

# Pyboard-D runs at 144Mhz by default
machine.freq(216000000)