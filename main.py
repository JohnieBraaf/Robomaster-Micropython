from robo import RoboMaster
import pyb

robo = RoboMaster()

while 1:
    # this should be fired every 10ms
    # for the sake of simplicity firing continously
    robo.cb10ms()
