import time
import math
from crc import Crc
from can import CanInterface
from msg import Message

class Processor(object):
    def __init__(self):
        self.crc = Crc()

        self.can1 = CanInterface(1)
        #self.can2 = CanInterface(2)

        # allocate message buffer
        self.messages_max = 25
        self.messages_size_max = 128 
        self.messages = []
        for i in range(self.messages_max):
            self.messages.append(Message(self.crc, self.messages_size_max))
        self.message_count = 0


    def add_byte(self, b):
        # register a new message start, or flush if buffer is full
        if b == 0x55:
            if self.message_count < self.messages_max:
                self.message_count += 1
            else:
                print("buffer overflow")
                self.flush() # flush buffer
                self.message_count += 1

        for i in range(self.message_count):
            self.messages[i].put(b)

            # process and flush when a valid message is found
            if self.messages[i].crc16:

                # control message for chassis and gimbal
                if self.messages[i].bytes[1] == 0x1b: # 27
                
                    term = ""

                    # check for chassis command flag 0x04
                    if self.messages[i].bytes[22] == 0x04 or self.messages[i].bytes[22] == 0x0C:
                        x = ((self.messages[i].bytes[13] << 5) | (self.messages[i].bytes[12] >> 3)) - 1024
                        y = (((self.messages[i].bytes[12] & 0x07) << 8) | (self.messages[i].bytes[11])) - 1024
                        if x != 0 or y != 0:
                            term += "x:" + str(x) + " y:" + str(y) + " "

                    # check for gimbal command flag 0x08
                    if self.messages[i].bytes[22] == 0x08 or self.messages[i].bytes[22] == 0x0C:
                        pitch = ((self.messages[i].bytes[17] << 4) | (self.messages[i].bytes[16] >> 4)) - 1024
                        if pitch < 0: # apply correction
                            pitch += 1

                        yaw = ((self.messages[i].bytes[20] << 6) | (self.messages[i].bytes[19] >> 2)) - 1024
                        if yaw < 0: # apply correction
                            yaw += 1

                        if pitch != 0 or yaw != 0:
                            term += "pitch: " + str(pitch) + " ,yaw: "  + str(yaw) + " "

                    if term != "":
                        print("0x1B: " + term)

                # control message for gimbal   
                elif self.messages[i].bytes[1] == 0x14:
                    pitch = 0
                    if self.messages[i].bytes[14] < 5: # up
                        pitch = (self.messages[i].bytes[14] << 8) | self.messages[i].bytes[13]
                    elif self.messages[i].bytes[14] > 250: # down
                        pitch = -(((self.messages[i].bytes[14] ^ 0xFF) << 8) | (self.messages[i].bytes[13] ^ 0xFF))
                    else:
                        print("huh")

                    yaw = 0
                    if self.messages[i].bytes[16] < 5: # right
                        yaw = (self.messages[i].bytes[16] << 8) | self.messages[i].bytes[15]
                    elif self.messages[i].bytes[16] > 250: # left
                        yaw = -(((self.messages[i].bytes[16] ^ 0xFF) << 8) | (self.messages[i].bytes[15] ^ 0xFF))
                    else:
                        print("huh")
                    
                    if pitch != 0 or yaw != 0:
                        print("0x14: pitch: " + str(pitch) + " ,yaw: "  + str(yaw))

                # control message for blaster
                elif self.messages[i].bytes[1] == 0x0E: 
                    if self.messages[i].bytes[5] > 3:
                        #85 14 9  3 160 72  8 1   # idle
                        #85 14 9 23   0 63 81 1   # gel beads
                        #85 14 9 23   0 63 81 17  # infrared beam
                        
                        
                        

                        print("0xOE: fired " +
                              str(self.messages[i].bytes[0])+ " " + 
                              str(self.messages[i].bytes[1]) + ' ' + 
                              str(self.messages[i].bytes[4])+ " " + 
                              str(self.messages[i].bytes[5]) + " " + 
                              str(self.messages[i].bytes[8]) + " " + 
                              str(self.messages[i].bytes[9]) + ' ' + 
                              str(self.messages[i].bytes[10])+ " " + 
                              str(self.messages[i].bytes[11]))

                # control message for blaster
                elif self.messages[i].bytes[1] == 0x0F: 
                    if self.messages[i].bytes[11] != 50 and self.messages[i].bytes[5] != 0xC3:
                        #0xOF: 85 15   9   4 64  4 76  0 0 # infrared beam      
                        #0xOF: 85 15 241 195  0 10 83 50 0 # Idle
                        #0xOF: 85 15   9   4 64  4 76  0 0 
                       '''' print("0xOF: fired " +
                                                                                                                          str(self.messages[i].bytes[0])+ " " + 
                                                                                                                          str(self.messages[i].bytes[1]) + ' ' + 
                                                                                                                          str(self.messages[i].bytes[4])+ " " + 
                                                                                                                          str(self.messages[i].bytes[5]) + " " + 
                                                                                                                          str(self.messages[i].bytes[8]) + " " + 
                                                                                                                          str(self.messages[i].bytes[9]) + ' ' + 
                                                                                                                          str(self.messages[i].bytes[10])+ " " +
                                                                                                                          str(self.messages[i].bytes[11])+ " " +
                                                                                                                          str(self.messages[i].bytes[12]))'''

                # individual wheel control
                elif self.messages[i].bytes[1] == 0x15: # 21
                    
                    # this filters out the strange frame which sporadically occurs after the last frame
                    if self.messages[i].bytes[5] == 0xC3:
                        rr = 0 # rear right
                        if self.messages[i].bytes[18] < 5: # rr forward
                            rr = (self.messages[i].bytes[18] << 8) | self.messages[i].bytes[17]
                        elif self.messages[i].bytes[18] > 250: # rr reverse
                            rr = -1 - (((self.messages[i].bytes[18] ^ 0xFF) << 8) | (self.messages[i].bytes[17] ^ 0xFF))
                        else:
                            print("huh")
                            print(str(self.messages[i].bytes[0])+ " " + str(self.messages[i].bytes[1]) + ' ' + str(self.messages[i].bytes[4])+ " " + str(self.messages[i].bytes[5]) + " " + str(self.messages[i].bytes[8]) + " " + str(self.messages[i].bytes[9]) + ' ' + str(self.messages[i].bytes[10])+ " " + str(self.messages[i].bytes[11]) + " " + str(self.messages[i].bytes[12]) + " " + str(self.messages[i].bytes[13]) + ' ' +str(self.messages[i].bytes[14])+ " " + str(self.messages[i].bytes[15]) + " " + str(self.messages[i].bytes[16]) + " " + str(self.messages[i].bytes[17])+ " " + str(self.messages[i].bytes[18]))

                        rl = 0 # rear left
                        if self.messages[i].bytes[16] < 5: # rl reverse
                            rl = -((self.messages[i].bytes[16] << 8) | self.messages[i].bytes[15])
                        elif self.messages[i].bytes[16] > 250: # rl forward
                            rl = 1 + (((self.messages[i].bytes[16] ^ 0xFF) << 8) | (self.messages[i].bytes[15] ^ 0xFF))
                        else:
                            print("huh")
                            print(str(self.messages[i].bytes[0])+ " " + str(self.messages[i].bytes[1]) + ' ' + str(self.messages[i].bytes[4])+ " " + str(self.messages[i].bytes[5]) + " " + str(self.messages[i].bytes[8]) + " " + str(self.messages[i].bytes[9]) + ' ' + str(self.messages[i].bytes[10])+ " " + str(self.messages[i].bytes[11]) + " " + str(self.messages[i].bytes[12]) + " " + str(self.messages[i].bytes[13]) + ' ' +str(self.messages[i].bytes[14])+ " " + str(self.messages[i].bytes[15]) + " " + str(self.messages[i].bytes[16]) + " " + str(self.messages[i].bytes[17])+ " " + str(self.messages[i].bytes[18]))

                        fr = 0 # forward right
                        if self.messages[i].bytes[12] < 5: # fr forward
                            fr = (self.messages[i].bytes[12] << 8) | self.messages[i].bytes[11]
                        elif self.messages[i].bytes[12] > 250: # fr reverse
                            fr = -1 - (((self.messages[i].bytes[12] ^ 0xFF) << 8) | (self.messages[i].bytes[11] ^ 0xFF))
                        else:
                            print("huh")
                            print(str(self.messages[i].bytes[0])+ " " + str(self.messages[i].bytes[1]) + ' ' + str(self.messages[i].bytes[4])+ " " + str(self.messages[i].bytes[5]) + " " + str(self.messages[i].bytes[8]) + " " + str(self.messages[i].bytes[9]) + ' ' + str(self.messages[i].bytes[10])+ " " + str(self.messages[i].bytes[11]) + " " + str(self.messages[i].bytes[12]) + " " + str(self.messages[i].bytes[13]) + ' ' +str(self.messages[i].bytes[14])+ " " + str(self.messages[i].bytes[15]) + " " + str(self.messages[i].bytes[16]) + " " + str(self.messages[i].bytes[17])+ " " + str(self.messages[i].bytes[18]))

                        fl = 0 # forward left
                        if self.messages[i].bytes[14] < 5: # fl reverse
                            fl = -((self.messages[i].bytes[14] << 8) | self.messages[i].bytes[13])
                        elif self.messages[i].bytes[14] > 250: # fl forward
                            fl = 1 + (((self.messages[i].bytes[14] ^ 0xFF) << 8) | (self.messages[i].bytes[13] ^ 0xFF))
                        else:
                            print("huh")
                            print(str(self.messages[i].bytes[0])+ " " + str(self.messages[i].bytes[1]) + ' ' + str(self.messages[i].bytes[4])+ " " + str(self.messages[i].bytes[5]) + " " + str(self.messages[i].bytes[8]) + " " + str(self.messages[i].bytes[9]) + ' ' + str(self.messages[i].bytes[10])+ " " + str(self.messages[i].bytes[11]) + " " + str(self.messages[i].bytes[12]) + " " + str(self.messages[i].bytes[13]) + ' ' +str(self.messages[i].bytes[14])+ " " + str(self.messages[i].bytes[15]) + " " + str(self.messages[i].bytes[16]) + " " + str(self.messages[i].bytes[17])+ " " + str(self.messages[i].bytes[18]))

                        #if fl != 0 or fr != 0 or rr !=0 or rl != 0:
                        #    print("FL: " + str(fl) + "  FR: " + str(fr) + "  RR: " + str(rr) + "  RL: " + str(rl))
                    else:
                       print("heh 0x15")
                       '''print(str(self.messages[i].bytes[11])+ " " + 
                              str(self.messages[i].bytes[12])+ " " + 
                              str(self.messages[i].bytes[13])+ " " + 
                              str(self.messages[i].bytes[14])+ " " + 
                              str(self.messages[i].bytes[15]) + " " + 
                              str(self.messages[i].bytes[16]) + " " +
                              str(self.messages[i].bytes[17]) + " " +
                              str(self.messages[i].bytes[18]))'''

                # gimbal precision control message
                elif self.messages[i].bytes[1] == 30: 
                    term = ""
                    gimbal_speed = (self.messages[i].bytes[23] << 8) | self.messages[i].bytes[22]
                    term += "gimbal speed: " + str(gimbal_speed)

                    gimbal_rotate_jaw = 0
                    if self.messages[i].bytes[15] < 10: # right
                        gimbal_rotate_jaw = (self.messages[i].bytes[15] << 8) | self.messages[i].bytes[14]
                    elif self.messages[i].bytes[15] > 245: # left
                        gimbal_rotate_jaw = -1 - (((self.messages[i].bytes[15] ^ 0xFF) << 8) | (self.messages[i].bytes[14] ^ 0xFF))
                    else:
                        print("huh")
                        print(str(self.messages[i].bytes[0])+ " " + str(self.messages[i].bytes[1]) + ' ' + str(self.messages[i].bytes[4])+ " " + str(self.messages[i].bytes[5]) + " " + str(self.messages[i].bytes[8]) + " " + str(self.messages[i].bytes[9]) + ' ' + str(self.messages[i].bytes[10])+ " " + str(self.messages[i].bytes[11]) + " " + str(self.messages[i].bytes[12]) + " " + str(self.messages[i].bytes[13]) + ' ' +str(self.messages[i].bytes[14])+ " " + str(self.messages[i].bytes[15]) + " " + str(self.messages[i].bytes[16]) + " " + str(self.messages[i].bytes[17])+ " " + str(self.messages[i].bytes[18]))
                    term += " rotate to jaw:" + str(gimbal_rotate_jaw)

                    gimbal_rotate_pitch = 0
                    if self.messages[i].bytes[19] < 10: # up
                        gimbal_rotate_pitch = (self.messages[i].bytes[19] << 8) | self.messages[i].bytes[18]
                    elif self.messages[i].bytes[19] > 245: # down
                        gimbal_rotate_pitch = -1 - (((self.messages[i].bytes[19] ^ 0xFF) << 8) | (self.messages[i].bytes[18] ^ 0xFF))
                    else:
                        print("huh")
                        print(str(self.messages[i].bytes[0])+ " " + str(self.messages[i].bytes[1]) + ' ' + str(self.messages[i].bytes[4])+ " " + str(self.messages[i].bytes[5]) + " " + str(self.messages[i].bytes[8]) + " " + str(self.messages[i].bytes[9]) + ' ' + str(self.messages[i].bytes[10])+ " " + str(self.messages[i].bytes[11]) + " " + str(self.messages[i].bytes[12]) + " " + str(self.messages[i].bytes[13]) + ' ' +str(self.messages[i].bytes[14])+ " " + str(self.messages[i].bytes[15]) + " " + str(self.messages[i].bytes[16]) + " " + str(self.messages[i].bytes[17])+ " " + str(self.messages[i].bytes[18]))
                    term += " rotate to pitch:" + str(gimbal_rotate_pitch)
                    print(term)

                   
                elif self.messages[i].bytes[1] == 26: 
                    # off        85 26 9 24 0 63 50 112 255 0   0   0   0 1   0 0   0 0 63 0 
                    #            85 26 9 24 0 63 50   1 255 0   0 127  70 0   0 0   0 0 63 0 
                    # red        85 26 9 24 0 63 50 113 255 0 255   0   0 0 232 3 232 3 15 0 
                    # pink       85 26 9 24 0 63 50 113 255 0 255   0 150 0 232 3 232 3 15 0 
                    # magenta    85 26 9 24 0 63 50 113 255 0 224   0 255 0 232 3 232 3 15 0 
                    # purple     85 26 9 24 0 63 50 113 255 0 100   0 100 0 232 3 232 3 15 0 
                    # blue       85 26 9 24 0 63 50 113 255 0  36 103 255 0 232 3 232 3 15 0 
                    # turquoise  85 26 9 24 0 63 50 113 255 0  69 215 255 0 232 3 232 3 15 0 
                    # green      85 26 9 24 0 63 50 113 255 0   0 127  70 0 232 3 232 3 15 0 
                    # mint       85 26 9 24 0 63 50 113 255 0 161 255  69 0 232 3 232 3 15 0 
                    # yellow     85 26 9 24 0 63 50 113 255 0 255 193   0 0 232 3 232 3 15 0 
                    # orange     85 26 9 24 0 63 50 113 255 0 255  50   0 0 232 3 232 3 15 0 
                    # white      85 26 9 24 0 63 50 113 255 0 255 255 255 0 232 3 232 3 15 0 
                    # black      85 26 9 24 0 63 50 113 255 0   0   0   0 0 232 3 232 3 15 0 

                    # pink rear  85 26 9 24 0 63 50 113 255 0 255   0 150 0 232 3 232 3  1 0
                    # pink front 85 26 9 24 0 63 50 113 255 0 255   0 150 0 232 3 232 3  2 0
                    # pink left  85 26 9 24 0 63 50 113 255 0 255   0 150 0 232 3 232 3  4 0
                    # pink right 85 26 9 24 0 63 50 113 255 0 255   0 150 0 232 3 232 3  8 0

                    # pink pulse 85 26 9 24 0 63 50 114 255 0 255   0 150 0 232 3 232 3  8 0
                    # pink blink 85 26 9 24 0 63 50 115 255 0 255   0 150 0 250 0 250 0  8 0
                    # ping off   85 26 9 24 0 63 50 112 255 0 255   0 150 0 232 3 232 3  8 0

                    # all pulse white 85 26 9 24 0 63 50 2 255 0 255 255 255 0 244 1 244 1 63 0
                    # 85 26 9 24 0 63 50 1 255 0 0 127 70 0 0 0 0 0 63 0

                    #85 26 9 24 0 63 50 113 255 0 255 0 0 0 232 3 232 3 48 0

                    # gimbal ????  85 26 201 195 64 63 60 63 75 0 75 0 75 0 75 0 75 0 75 0
                    # gimbal all   85 26 9 24 0 63 50 113 255 0 255 0 150 0 232 3 232 3 48 0
                    # gimbal all   85 26 9 24 0 63 50 113 255 0 255 0 0 0 232 3 232 3 48 0
                    # gimbal left  85 26 9 24 0 63 50 113 255 0 255 0 150 0 232 3 232 3 16 0
                    # gimbal right 85 26 9 24 0 63 50 113 255 0 255 0 0 0 232 3 232 3 32 0



                    term = ""
                    if self.messages[i].bytes[22] == 0x01:
                        term += "LED chassis rear: "
                    elif self.messages[i].bytes[22] == 0x02:
                        term += "LED chassis front: "
                    elif self.messages[i].bytes[22] == 0x04:
                        term += "LED chassis left: "
                    elif self.messages[i].bytes[22] == 0x08: 
                        term += "LED chassis right: "
                    elif self.messages[i].bytes[22] == 0x0F: # 15
                        term += "LED chassis all: "
                    elif self.messages[i].bytes[22] == 0x10: # 16
                        term += "LED gimbal left: "
                    elif self.messages[i].bytes[22] == 0x20: # 32
                        term += "LED gimbal right: "
                    elif self.messages[i].bytes[22] == 0x30: # 48
                        term += "LED gimbal all: "
                    elif self.messages[i].bytes[22] == 0x3F: # 63
                        term += "LED all: "
                    else:
                        print("unknown led " + str(self.messages[i].bytes[22]))

                    if self.messages[i].bytes[11] == 0x70:
                        term += "off "
                    elif self.messages[i].bytes[11] == 0x71:
                        term += "solid "
                    elif self.messages[i].bytes[11] == 0x72:
                        term += "pulse "
                    elif self.messages[i].bytes[11] == 0x73:
                        term += "blink "
                    elif self.messages[i].bytes[11] == 0x01:
                        term += "standby "
                    else:
                        print("unknown mode " + str(self.messages[i].bytes[11]))

                    r = self.messages[i].bytes[14]
                    g = self.messages[i].bytes[15]
                    b = self.messages[i].bytes[16]
                    # red        85 26 9 24 0 63 50 113 255 0 255   0   0 0 232 3 232 3 15 0 
                    # pink       85 26 9 24 0 63 50 113 255 0 255   0 150 0 232 3 232 3 15 0 
                    # magenta    85 26 9 24 0 63 50 113 255 0 224   0 255 0 232 3 232 3 15 0 
                    # purple     85 26 9 24 0 63 50 113 255 0 100   0 100 0 232 3 232 3 15 0 
                    # blue       85 26 9 24 0 63 50 113 255 0  36 103 255 0 232 3 232 3 15 0 
                    # turquoise  85 26 9 24 0 63 50 113 255 0  69 215 255 0 232 3 232 3 15 0 
                    # green      85 26 9 24 0 63 50 113 255 0   0 127  70 0 232 3 232 3 15 0 
                    # mint       85 26 9 24 0 63 50 113 255 0 161 255  69 0 232 3 232 3 15 0 
                    # yellow     85 26 9 24 0 63 50 113 255 0 255 193   0 0 232 3 232 3 15 0 
                    # orange     85 26 9 24 0 63 50 113 255 0 255  50   0 0 232 3 232 3 15 0 
                    # white      85 26 9 24 0 63 50 113 255 0 255 255 255 0 232 3 232 3 15 0 
                    # black      85 26 9 24 0 63 50 113 255 0   0   0   0 0 232 3 232 3 15 0 
                    if r == 255 and g == 0 and b == 0:
                        term += " RED "
                    elif r == 255 and g == 0 and b == 150:
                        term += " PINK "
                    elif r == 224 and g == 0 and b == 255:
                        term += " MAGENTA "
                    elif r == 100 and g == 0 and b == 100:
                        term += " PURPLE "
                    elif r == 36 and g == 103 and b == 255:
                        term += " BLUE "
                    elif r == 69 and g == 215 and b == 255:
                        term += " TURQOISE "
                    elif r == 0 and g == 127 and b == 70:
                        term += " GREEN "
                    elif r == 161 and g == 255 and b == 69:
                        term += " MINT "
                    elif r == 255 and g == 193 and b == 0:
                        term += " YELLOW "
                    elif r == 255 and g == 50 and b == 0:
                        term += " ORANGE "
                    elif r == 255 and g == 255 and b == 255:
                        term += " WHITE "
                    elif r == 0 and g == 0 and b == 0:
                        term += " BLACK "
                    else:
                        print("unknown color " + str(r) + " " + str(g) + " " + str(b))

                    print(term)
                '''    
                else:#self.messages[i].bytes[1] == 0x1b: # 27
                    print(str(self.messages[i].bytes[0])+ " " + 
                          str(self.messages[i].bytes[1]) + ' ' + 
                          str(self.messages[i].bytes[2]) + ' ' + 
                          str(self.messages[i].bytes[3]) + ' ' + 
                          str(self.messages[i].bytes[4])+ " " + 
                          str(self.messages[i].bytes[5]) + " " + 
                          str(self.messages[i].bytes[6]) + ' ' + 
                          str(self.messages[i].bytes[7]) + ' ' + 
                          str(self.messages[i].bytes[8]) + " " + 
                          str(self.messages[i].bytes[9]) + ' ' + 
                          str(self.messages[i].bytes[10])+ " " + 
                          str(self.messages[i].bytes[11]) + " " + 
                          str(self.messages[i].bytes[12]) + " " + 
                          str(self.messages[i].bytes[13]) + ' ' +
                          str(self.messages[i].bytes[14])+ " " + 
                          str(self.messages[i].bytes[15]) + " " + 
                          str(self.messages[i].bytes[16]) + " " + 
                          str(self.messages[i].bytes[17]) + " " + 
                          str(self.messages[i].bytes[18]) + " " + 
                          str(self.messages[i].bytes[19]) + " " + 
                          str(self.messages[i].bytes[20]) + ' ' +
                          str(self.messages[i].bytes[21])+ " " + 
                          str(self.messages[i].bytes[22]) + " " + 
                          str(self.messages[i].bytes[23]) + ' ' + 
                          str(self.messages[i].bytes[24]) + ' ' + 
                          str(self.messages[i].bytes[25]) + ' ' + 
                          str(self.messages[i].bytes[26]))
                '''    

                '''
                fcnt = math.ceil(self.messages[i].length / 8)
                midx = 0
                midx2 = 0
                for f in range(fcnt):
                    midx2 = midx+8
                    if midx > (self.messages[i].length - 8):
                        midx2 = self.messages[i].length + 1
                    
                    while (self.can1.can.info()[5] == 3):
                        pass # wait till TX buffer is free

                    self.can1.can.send(self.messages[i].bytes[midx:midx2], 0x201)
                    midx += 8
                '''
                self.flush() # flush buffer
                break

    def flush(self):
        for i in range(self.message_count):
            self.messages[i].flush()
        self.message_count = 0