import uasyncio as asyncio
from sys import platform
from pyb import LED

import time

async def heartbeat(robo):
    led = LED(1)
    t0 = time.ticks_us()

    while True:
        led.toggle()

        robo.cb10ms()

        t1 = time.ticks_us()
        dt = time.ticks_diff(t1, t0)
        n=1
        c1=1
        c2=2
        fmt = '{:5.3} sec, {:6.3f} usec/cyle: {:8.2f} kcycle/sec ,can1 {:5.3} ,can2 {:5.3}'
        #print(fmt.format(dt * 1e-6, dt / n, n / dt * 1e3, c1, c2))
        t0 = time.ticks_us()

        await asyncio.sleep_ms(4)

class CanId():
     x200 =  0 # self
     x201 =  1 # main control unit
     x202 =  2 # motion control unit
     x203 =  3 # gimal
     x204 =  4 # blaster
     x211 =  5 # armor back
     x212 =  6
     x213 =  7
     x214 =  8
     x215 =  9
     x216 = 10