# DJI Robomaster CAN BUS Controller

This project allows the use of STM32 microcontrollers running [micropython](https://github.com/micropython/micropython) to control the Robomaster S1 or EDU.

Only CAN BUS High / Low wires need to be connected to the robot gimbal, replacing the cable leading to the control unit (with the antennas).

Use A STM32 NUCLEO board (ethernet) or [PYBD-SF6W](https://store.micropython.org/product/PYBD-SF6-W4F2) (WiFi).

## Micropython firmware
The code relies on a patched version of Micropython:
- Hack for non-extended CAN BUS addresses being filtered. See [miropython-bug](https://github.com/micropython/micropython/issues/5508).
- Enabled _thread module to allow for REPL debugging while running a uasyncio control loop to switch between CAN RX/TX and network traffic. See [enable _thread](https://forum.micropython.org/viewtopic.php?t=8502).

Current firmwares (feel free to request, see [boards](https://github.com/micropython/micropython/tree/master/ports/stm32/boards)):
- bin/firmware_NUCLEO_F767ZI.hex (2020-11-17)
- bin/firmware_PYBD_SF6.dfu (2020-11-15)

### Flashing firmware

For NUCLEO boards:
- Firmwares can be flashed to the board with [STM32CubeProgrammer](https://www.st.com/en/development-tools/stm32cubeprog.html)
- Use ST-Link usb connection to flash the firmware
- Use board USB connection to access PYBFLASH 

For PYBD boards:

Enter DFU bootloader mode by holding down the USR button, pressing and releasing the RST button, and continuing to hold down USR until the LED is white (4th in the cycle), then let go of USR while the LED is white. The LED will then flash red once per second to indicate it is in USB DFU mode. You can then program the firmware using a DFU programmer, eg [dfu-util](http://dfu-util.sourceforge.net/) or [pydfu.py](https://github.com/micropython/micropython/blob/master/tools/pydfu.py).

## PYBFLASH

All files except the bin directory to your micro controller FLASH memory. Micropython boards are configured as a USB storage device, so just plug and copy.

## Serial connection (for monitoring)
For a serial monitoring:
 - Windows:  putty (baudrate 115200)
 - Mac OS X: screen /dev/tty.usbmodem*
 - Linux:    screen /dev/ttyACM0
 
## Clients (for control)
 
A TCP socket server is setup configure IP parameters in main.py.
The client.py script can be used from a PC to send commands using the arrows on the keyboard. 
 
## TODO
 
- Implement complete protocol (see already parsable commands in proc.py)
- ROS bridge
 
 
 Credits to [robomaster_s1_can_hack](https://github.com/RoboMasterS1Challenge/robomaster_s1_can_hack) project, for inspiring me to create this project
 