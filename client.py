import sys
import select
import socket
import time
from pynput import keyboard

class Client():
    def __init__(self):
    
        self.ip = '192.168.137.10'
        self.port = 8123

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.ip, self.port))

        self.speed = 0.10
        self.forward = 0
        self.backward = 0
        self.left = 0
        self.right = 0

        self.controls = {
                    'w': 'forward',
                    's': 'backward',
                    'a': 'left',
                    'd': 'right',

                    'Key.up': 'forward',
                    'Key.down': 'backward',
                    'Key.left': 'left',
                    'Key.right': 'right',

                }

        listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release)
        listener.start()

    def on_press(self, key):
        command = self.controls.get(str(key))
        if command:
            #print(command)
            setattr(self, command, self.speed)

    def on_release(self, key):
        command = self.controls.get(str(key))
        if command:
            #print(command)
            setattr(self, command, 0)

        elif key == keyboard.Key.esc:
            # Stop listener
            return False


client = Client()
interval = 0.055 # loop target in seconds
last = time.time()
counter = 0
start = time.time()
while True:
    next = last + interval
    sleep = next - time.time()
    if sleep > 0.0:
        time.sleep(sleep)
    last = next

    #time.sleep(0.075)
    if client.forward + client.backward + client.left + client.right > 0:
        counter += 1
        now = time.time()
        print(str(counter) + ': ' + str(int((now - start) * 1000)))
        start = now
        x = client.forward - client.backward
        y = client.left - client.right
        #print(client.forward, client.backward, client.left, client.right)
        #print(x,y)
        client.sock.sendall(('CMD:'+str(x)+','+str(y)+'\r\n').encode())