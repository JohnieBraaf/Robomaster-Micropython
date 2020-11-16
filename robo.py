from crc import Crc
from can import CanInterface
from com import Command
import pyb, time

class RoboMaster():
    def __init__(self):

        self.crc = Crc()
        self.can1 = CanInterface(1)
        self.com = Command(self)

        self.linear = Linear()
        self.angular = Angular()

        self.timcount  = 0

        self.tim2 = pyb.Timer(2)
        self.tim2.init(freq=100)
        self.tim2.callback(self.cb)

    def cb(self, t):
        self.linear.reset()
        self.angular.reset()

    def cb10ms(self):
        self.timcount += 1

        self.com.add_10ms()

        if self.timcount % 10 == 0:
            self.com.add_100ms()

        if self.timcount % 100 == 0:
            self.com.add_1sec()

        if self.timcount % 1000 == 0:
            self.com.add_10sec()

        if self.timcount == 1001:
            self.timecount = 1
        
        while self.com.buf.any():
            #pyb.LED(3).on()
            while (self.can1.can.info()[5] == 3):
                pass # wait till TX buffer is free
            self.can1.can.send(self.com.get()[3], 0x201)
            #pyb.LED(3).off()
    
    def process_tcp(self, data):
        print(data)
        if len(data) > 4:
            # check header
            if data[0] == 0x55 and data[1] == len(data) and data[2] == 0x04 and self.crc.check_crc8(data, 4):

                x  = data[6] << 8 | data[7]
                y  = data[8] << 8 | data[9]
                rx = data[10] << 8 | data[11]
                ry = data[12] << 8 | data[13]
                z  = data[14] << 8 | data[15]
                rz = data[16] << 8 | data[17]
                self.linear.set(-(1000 - y) / 1000, (1000 - x) / 1000, 0)
                self.angular.set(-(1000 - ry) / 1000, (1000 - rx) / 1000, 0)
                #print(self.angular.x)
            else:
                print("invalid package")
                print(data)
        else:
            print("package too short")
            print(data)


class Linear():
    def __init__(self):
        self.t0 = time.ticks_ms()
        self.x = 0
        self.y = 0
        self.z = 0

    def reset(self):
        if time.ticks_diff(time.ticks_ms(), self.t0) > 200:
            self.x = 0
            self.y = 0
            self.z = 0
        #    print("reset")
        #else:
        #    print("fine")


    def set(self, x, y, z):
        self.t0 = time.ticks_ms()
        self.x = self.check_value(x)
        self.y = self.check_value(y)
        self.z = self.check_value(z)

    def check_value(self, value):
        if value > 1 or value < -1:
            value = 0

        if value == 1:
            value = 0.9998
        elif value == -1:
            value = -0.9998

        return value

class Angular():
    def __init__(self):
        self.t0 = time.ticks_ms()
        self.x = 0
        self.y = 0
        self.z = 0

    def reset(self):
        if time.ticks_diff(time.ticks_ms(), self.t0) > 200:
            self.x = 0
            self.y = 0
            self.z = 0
        #    print("reset")
        #else:
        #    print("fine")


    def set(self, x, y, z):
        self.t0 = time.ticks_ms()
        self.x = self.check_value(x)
        self.y = self.check_value(y)
        self.z = self.check_value(z)

    def check_value(self, value):
        if value > 1 or value < -1:
            value = 0

        if value == 1:
            value = 0.9998
        elif value == -1:
            value = -0.9998

        return value

