from buf import RingBuffer
from msg import Message
from crc import Crc
from proc import Processor

class CommandId():
    
    x0D =   [ 0,   10, bytearray(b'\x55\x0D\x04\xFF\x0A\xFF\xFF\xFF\x40\x00\x01\xFF\xFF')]
    x0E =   [ 1,   10, bytearray(b'\x55\x0E\x04\xFF\x09\x03\xFF\xFF\xA0\x48\x08\x01\xFF\xFF')]
    x0F =   [ 2,   10, bytearray(b'\x55\x0F\x04\xFF\xF1\xC3\xFF\xFF\x00\x0A\x53\x32\x00\xFF\xFF')]  
    x12 =   [ 3,  100, bytearray(b'\x55\x12\x04\xFF\xF1\xC3\xFF\xFF\x40\x00\x58\x03\x92\x06\x02\x00\xFF\xFF')]
    x14 =   [ 4,    1, bytearray(b'\x55\x14\x04\xFF\x09\x04\xFF\xFF\x00\x04\x69\x08\x05\x00\x00\x00\x00\x6D\xFF\xFF')]
    x1B =   [ 5,    1, bytearray(b'\x55\x1B\x04\xFF\x09\xC3\xFF\xFF\x00\x3F\x60\x00\x04\x20\x00\x01\x08\x40\x00\x02\x10\x04\x03\x00\x04\xFF\xFF')]
    x49 =   [ 6,  100, bytearray(b'\x49\x04\xFF\x49\x03\xFF\xFF\x00\x3F\x70\xB4\x11\x34\x03\x00\x00\xF7\x05\x42\x08\x10\x00\x08\x00\x08\x00\x08\x00\x08\x00\x08\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x7E\x0E\xF3\x0B\xD9\x07\x0E\x07\x3D\x07\x6A\x08\x62\x0A\x05\x0B\xD6\x0B\xFF\xFF')]
    BOOT1 = [ 7,    0, bytearray(b'\x55\x1B\x04\xFF\x09\xC3\x00\x00\x00\x3F\x60\x00\x04\x20\x00\x01\x00\x40\x00\x02\x10\x00\x03\x00\x00\xFF\xFF')]
    BOOT2 = [ 8,    0, bytearray(b'\x55\x14\x04\xFF\x09\x04\x00\x00\x00\x04\x69\x08\x05\x00\x00\x00\x00\x01\xFF\xFF')]
    BOOT3 = [ 9,    0, bytearray(b'\x55\x0F\x04\xFF\x09\x04\x02\x00\x40\x04\x4C\x02\x00\xFF\xFF')]
    BOOT4 = [10,    0, bytearray(b'\x55\x0E\x04\xFF\x09\x03\x00\x00\x00\x3F\x3F\x02\xFF\xFF')]
    BOOT5 = [11,    0, bytearray(b'\x55\x15\x04\xFF\xF1\xC3\x00\x00\x00\x03\xD7\x01\x07\x00\x02\x00\x00\x00\x00\xFF\xFF')]
    BOOT6 = [12,    0, bytearray(b'\x55\x12\x04\xFF\x09\x03\x01\x00\x40\x48\x01\x09\x00\x00\x00\x03\xFF\xFF')]
    BOOT7 = [13,    0, bytearray(b'\x55\x1C\x04\xFF\x09\x03\x02\x00\x40\x48\x03\x09\x00\x03\x00\x01\xFB\xDC\xF5\xD7\x03\x00\x02\x00\x01\x00\xFF\xFF')]
    BOOT8 = [14,    0, bytearray(b'\x55\x12\x04\xFF\x09\x03\x03\x00\x40\x48\x01\x09\x00\x00\x00\x03\xFF\xFF')]
    BOOT9 = [15,    0, bytearray(b'\x55\x24\x04\xFF\x09\x03\x04\x00\x40\x48\x03\x09\x01\x03\x00\x02\xA7\x02\x29\x88\x03\x00\x02\x00\x66\x3E\x3E\x4C\x03\x00\x02\x00\x32\x00\xFF\xFF')]

class Command(object):
    def __init__(self, robo):
        self.robo = robo
        self.buf = RingBuffer(2048)
        self.crc = Crc()
        #self.proc = Processor()

        # load template messages
        self.messages_size_max = 128 
        self.messages = []
        self.message_count = 0

        with open('command_list.csv','r') as file:
            header = 0
            row = 0 # translates into message nbr
            for line in file:
                if header == 0:
                    header = 1 # ignore
                else:
                    line = line.rstrip('\n').rstrip('\r')
                    self.messages.append(Message(self.crc, self.messages_size_max))
                    self.messages[row].mode = 1 # overwrite crc
                            
                    col = 0 
                    for val in line.split(','):
                        if col == 1:
                            self.messages[row].boot = int(val)
                        elif col == 2:
                            self.messages[row].freq = int(val)
                        elif col > 2 and val != '0':
                            self.messages[row].put(int(val, 16))
                        col += 1
                    row += 1
            self.message_count = row

        # allocate byte arrays for frame buffer
        self.data = []
        for i in range(9):
            self.data.append(bytearray(i))

        # allocate frames with references to the byte arrays
        self.frame = []
        for i in range(9):
            self.frame.append([0x201, 0, 0, memoryview(self.data[i])])

        self.add(self.messages[11]) #LED ON

    # add boot sequence commands
    @micropython.viper
    def add_boot(self):
        self.add(self.messages[26]) #BOOT1
        self.add(self.messages[27]) #BOOT2
        self.add(self.messages[28]) #BOOT3
        self.add(self.messages[29]) #BOOT4
        self.add(self.messages[30]) #BOOT5
        self.add(self.messages[31]) #BOOT6
        self.add(self.messages[32]) #BOOT7
        self.add(self.messages[33]) #BOOT8
        self.add(self.messages[34]) #BOOT9

        self.add(self.messages[11]) #LED ON
        self.add(self.messages[37]) #GIMBAL OFF

    @micropython.viper   
    def add_10ms(self):
        #self.add(self.messages[5]) #1B
        self.add_1b()
        self.add(self.messages[4]) #14

    @micropython.viper
    def add_100ms(self):
        self.add(self.messages[0]) #0D
        self.add(self.messages[1]) #0E
        self.add(self.messages[2]) #0F

    @micropython.viper
    def add_1sec(self):
        self.add(self.messages[3]) #12
        self.add(self.messages[20]) #0F
        self.add(self.messages[6]) #49

    @micropython.viper
    def add_10sec(self):
        pass

    def add_1b(self, move=False):
        msg = self.messages[5]

        # x, y = 1024 = stationary
        if self.robo.linear.x == 0:
            self.robo.linear.x = 1
        if self.robo.linear.y == 0:
            self.robo.linear.y = 1
        x = int(self.robo.linear.x * 1024.0)
        y = int(self.robo.linear.y * 1024.0)

        msg.bytes_ref[11] = y & 0xFF
        msg.bytes_ref[12] = ((x << 3) | (y >> 8)) & 0x07
        msg.bytes_ref[13] = (x >> 5) & 0x3F

        msg.prepare()
        #self.crc.add_crc16(msg, self.messages[5].index)
        self.add(msg) #1B
        

    # add message to command buffer
    @micropython.viper
    def add(self, message):
        #message.prepare() # add time bits, not nescessary?
        if message.crc8 and message.crc16:
            r = range(message.length)
            for i in r:
                self.buf.put(message.bytes_ref[i])
        else:
            print("error invalid message")

    # return CAN frame from command buffer
    @micropython.viper
    def get(self):
        if self.buf.any():
            r = 8
            if int(self.buf.count) < 8:
                r = int(self.buf.count)
            ran = range(r)
            for i in ran:
                self.frame[r][3][i] = self.buf.get()
                #self.proc.add_byte(self.frame[r][3][i])
            return self.frame[r]
        else:
            return None # empty buffer
