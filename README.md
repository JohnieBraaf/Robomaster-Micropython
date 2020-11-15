# Robomaster-Micropython
Robomaster S1 - Micropython CAN BUS controller

Currently the project is in a proof of concept phase.
It is a micropython port of this project: [obomaster_s1_can_hack](https://github.com/RoboMasterS1Challenge/robomaster_s1_can_hack)

There seems to be a bug in the micropython code preventing the non-extended frame CAN BUS addresses (used by the Robomaster) to be seen.
Therefore I have included a patched version of the micropython code, which can be flashed to the board with [STM32CubeProgrammer](https://www.st.com/en/development-tools/stm32cubeprog.html)
You can also patch a version of the micropython code yourself see: [miropython-bug](https://github.com/micropython/micropython/issues/5508)

Current patched micropython boards (others can be build):
- bin/firmware_NUCLEO_F767ZI.hex (2020-11-15)