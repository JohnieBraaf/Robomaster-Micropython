from crc import Crc

class Message(Crc):
    def __init__(self, crc, size):
        self.bytes_cnt = size
        self.bytes = bytearray(self.bytes_cnt)
        self.bytes_ref = memoryview(self.bytes)
        self.crc = crc

        self.mode = 0  # 0: verify crc, 1: overwrite crc
        self.freq = 0  # used for transmission
        self.count = 0 # used for transmission
        self.boot = 0  # indicate bootmessage

        self.flush()

    @micropython.native
    def flush(self):
        self.index = 0
        self.length = 0
        self.crc8 = False
        self.crc16 = False
        self.valid = True


    @micropython.native
    def put(self, byte):
        if self.valid:
            if self.index < self.length or self.length == 0:
                if self.index < self.bytes_cnt:
                    self.bytes_ref[self.index] = byte
                    self.index += 1
                else:
                    self.valid = False # buffer overflow

            if self.index == 2:
                self.length = int(byte)

            elif self.index == 4:
                if self.mode == 1:
                    self.crc.add_crc8(self.bytes_ref, self.index)
                
                if self.crc.check_crc8(self.bytes_ref, self.index):
                    self.crc8 = True
                else:
                    self.valid = False # crc8 check failed

            elif self.index == self.length and self.index != 0 and self.valid:
                if self.mode == 1:
                   self.crc.add_crc16(self.bytes_ref, self.index) 
                if self.crc.check_crc16(self.bytes_ref, self.index):
                    self.crc16 = True
                else:
                    self.valid = False # crc 16 check failed

                    # debug (requires heap allocation) 
                    #text = "crc failed: "
                    #for i in range(self.index):
                    #    text += " " + str(self.bytes[i])
                    #print(text)
    
    # add time bits and crc16       
    def prepare(self):
        if self.index > 7:
            if self.boot == 0:
                self.bytes_ref[6] = self.count & 0xFF
                self.bytes_ref[7] = (self.count >> 8) & 0xFF

            self.crc.add_crc8(self.bytes_ref, 4)
            self.crc.add_crc16(self.bytes_ref, self.index) 
            self.count += 1
