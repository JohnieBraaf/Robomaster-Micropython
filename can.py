import pyb, micropython
from buf import FrameBuffer

class CanInterface(pyb.CAN):
    def __init__(self, itf):
        self.itf = itf
        self.can = pyb.CAN(itf)

        self.buf = FrameBuffer(64)

        self.send_caller = self.sendcb
        self.init()

    def init(self):
        can = self.can
        can.init(mode=pyb.CAN.NORMAL, extframe=False, prescaler=3, sjw=1, bs1=15, bs2=2, auto_restart=True) # 1mbps @216Mhz
        #can.init(mode=pyb.CAN.NORMAL, extframe=False, prescaler=3, sjw=1, bs1=15, bs2=2, auto_restart=True) # 1mbps @216Mhz
        #can.init(mode=pyb.CAN.NORMAL, extframe=False, prescaler=4, sjw=1, bs1=7, bs2=1, auto_restart=True) # 1mbps @144Mhz
        can.setfilter(bank=self.itf-1, mode=pyb.CAN.MASK32, fifo=self.itf-1, params=(0x0, 0x0))
        can.rxcallback(self.itf-1, self.receive)
        print ("CAN " + str(self.itf) + " initialized")

    def close(self):
        self.can.rxcallback(self.itf-1, None)
        self.can.deinit()

    def send(self, message):
        micropython.schedule(self.send_caller, message)

    def sendcb(self, message):
        print(message)
        if self.can.info()[5] < 3:
            self.can.send(message[3], message[0])
        else:
            print("cannot send packet on CAN" + str(self.itf) + ", TX queue is full")

    def receive(self, bus, reason):
        self.can.recv(self.itf-1, self.buf.put())      