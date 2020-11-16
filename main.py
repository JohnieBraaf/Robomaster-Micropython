import uasyncio
import time
import network
from robo import RoboMaster
from srv import Server
from beat import heartbeat

print("Getting IP address")
lan = network.LAN()
lan.active(1)
while not lan.isconnected():
    time.sleep(.1)
print("IP address: " + lan.ifconfig()[0])

print("Starting RoboMaster")
robo = RoboMaster()
loop = uasyncio.get_event_loop()
loop.create_task(heartbeat(robo))
server = Server(robo)
try:
    loop.run_until_complete(server.run(loop))
except KeyboardInterrupt:
    print('Interrupted')
finally:
    server.close()
