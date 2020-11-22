# Robomaster-Micropython
Robomaster S1 - Micropython CAN BUS controller

This project allows the use of STM32 microcontrollers running [micropython](https://github.com/micropython/micropython) to control the Robomaster S1 or EDU.
It is meant as a replacement of the main control unit, which should be unplugged. This saves a considerable amount of the total power consumption.

The NUCLEO board supports a ethernet connection to receive network commands.
The [PYBD-SF6W](https://store.micropython.org/product/PYBD-SF6-W4F2) supports a WiFi connection and is much smaller.

The boards are (over)clocked at 216Mhz. And the CAN BUS runs @1Mbit.

Only CAN BUS High / Low wires need to be connecting to the robot gimbal, replacing the cable leading to the control unit (with the antennas).

## Micropython firmware
The code relies on a patched version of Micropython:
- Hack for non-extended CAN BUS addresses being filtered. See [miropython-bug](https://github.com/micropython/micropython/issues/5508).
- Enabled _thread module to allow for REPL debugging while running a uasyncio control loop to switch between CAN RX/TX and network traffic. See [enable _thread](https://forum.micropython.org/viewtopic.php?t=8502).

Current firmwares (feel free to request a build a [board](https://github.com/micropython/micropython/tree/master/ports/stm32/boards)):
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

The client.py file can be used on a PC to connect to the board. Commands are still a work in progress as a little refactoring is needed.

For a serial prompt:
 - Windows: you need to go to 'Device manager', right click on the unknown device,
   then update the driver software, using the 'pybcdc.inf' file found on this drive.
   Then use a terminal program like Hyperterminal or putty (Serial connection 115200 baudrate).
 - Mac OS X: use the command: screen /dev/tty.usbmodem*
 - Linux: use the command: screen /dev/ttyACM0
 
 ## Clients (for control)
 
 A socket server is setup see main.py for the configuration parameters.
 
 The client.py script can be used to send commands from a PC using the arrows on the keyboard. 
 
 ## TODO
 
 - Implement complete protocol (see already parsable commands in proc.py)
 - ROS bridge
 
 
  Credits to [robomaster_s1_can_hack](https://github.com/RoboMasterS1Challenge/robomaster_s1_can_hack) project, for inspiring me to create this project
 