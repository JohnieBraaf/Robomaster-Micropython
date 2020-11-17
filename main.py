import uasyncio
import time
import network
from robo import RoboMaster
from srv import Server
from beat import heartbeat

##########################
# Config
##########################

DHCP    = False
IP      = '192.168.137.10'
MASK    = '255.255.255.0'
GATEWAY = '192.168.137.1'
DNS     = '192.168.137.1'


##########################
# Network connection
##########################

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
# uasyncio inside a thread
##########################


import _thread # unsupported module
robo = RoboMaster()
def robo_thread( threadName, robo):
    
    loop = uasyncio.get_event_loop()
    loop.create_task(heartbeat(robo))
    server = Server(robo)
    try:
        loop.run_until_complete(server.run(loop))
    except KeyboardInterrupt:
        print('Interrupted')
    finally:
        server.close()

# use a thread to keep REPL available for debugging
thread1=_thread.start_new_thread( robo_thread, ("thread1", robo, ) )