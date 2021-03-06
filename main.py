import uasyncio
import pyb, time
import network
from robo import RoboMaster
import _thread # unsupported module

##########################
# Network connection
##########################

DHCP    = False # DHCP True/False
IP      = '192.168.137.10'
MASK    = '255.255.255.0'
GATEWAY = '192.168.137.1'
DNS     = '192.168.137.1'

lan = network.LAN()
lan.active(1)

if DHCP:
    print("Getting IP address...")
    while not lan.isconnected():
        time.sleep(.1)
else:
    lan.ifconfig((IP, MASK, GATEWAY, DNS))

print("IP address: " + lan.ifconfig()[0])


##########################
# Main loop
##########################

robo = RoboMaster()


async def heartbeat(robo):
    interval = 10 # miliseconds
    last = time.ticks_ms()
    while True:
        next = last + interval
        sleep = next - time.ticks_ms()
        if sleep > 0:
            #print(sleep)
            await uasyncio.sleep_ms(sleep)
            last = next
        else:
            print('ROBO: running late')
            last = time.ticks_ms()
        
        robo.cb10ms()

async def can_send(robo):
    interval = 10 # miliseconds
    last = time.ticks_ms()
    while True:
        next = last + interval
        sleep = next - time.ticks_ms()
        if sleep > 0:
            #print(sleep)
            await uasyncio.sleep_ms(sleep)
            last = next
        else:
            print('CAN: running late')
            last = time.ticks_ms()
        
        while robo.com.buf.any():
            pyb.LED(2).on()
            while (robo.can1.can.info()[5] == 3):
                print('passing')
                pass # wait till TX buffer is free
            robo.can1.can.send(robo.com.get()[3], 0x201)
            pyb.LED(2).off()

async def tcp_callback(reader, writer):
    print('TCP client connected')
    while True:
        try:
            # reading the TCP stream can sometimes take up to 250ms
            # therefore we need to repeat the CAN BUS commands for 300ms
            # in that way the stream of commands is never interrupted
            pyb.LED(1).off()
            start = time.ticks_ms()
            res = await reader.readline()
            robo.process_tcp(res.rstrip())
            pyb.LED(1).on()
            end = time.ticks_ms()
            if end -start > 10:
                print('TCP: running late ' + str(end - start))
        except Exception as e:
            print(e)
            break

def main(robo):
    
    loop = uasyncio.get_event_loop()
    loop.create_task(heartbeat(robo))
    loop.create_task(can_send(robo))
    loop.create_task(uasyncio.start_server(tcp_callback, "192.168.137.10", 8123, backlog=1))
    loop.run_forever()
    loop.close()

debug = False
if debug:
    # use a thread to keep REPL available for debugging
    # the _thread module is not supposed to be used directly
    thread=_thread.start_new_thread( robo_thread, (robo, ) )
else:
    main(robo)


##########################
# Notes
##########################

# observed CAN BUS addresses
x200 =  0 # self assigned
x201 =  1 # main control unit <-- we use this one
x202 =  2 # motion control unit
x203 =  3 # gimal
x204 =  4 # blaster
x211 =  5 # armor back
x212 =  6
x213 =  7
x214 =  8
x215 =  9
x216 = 10