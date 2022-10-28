import network
import espnow
import machine
import time
from machine import Pin, Timer, RTC
from time import sleep_us, sleep
from led_spi import matrix

sta = network.WLAN(network.STA_IF)  # Or network.AP_IF
sta.active(True)
#sta.disconnect()   # For ESP8266
print(sta.config('mac'))
e = espnow.ESPNow()
e.active(True)
peer = b'\xc4\xddW\xc9\x8c '   # MAC address of peer's wifi interface
e.add_peer(peer)
#==================
s = matrix()
a = 0
pb1 = Pin(15, Pin.IN, Pin.PULL_UP)
score = 0

def spress():
#global table
    global s
    global a
    global pb1
    global score
#print('call back')
    if not pb1.value():
        s.swap(0, a%10)
        a +=1
        score += 1
        

def callback(pin):
    timer2 = Timer(2)
    timer2.init(period=50, mode=Timer.ONE_SHOT, callback= lambda t: spress())

pb1 = Pin(15, Pin.IN, Pin.PULL_UP)
pb1.irq(trigger=Pin.IRQ_FALLING,handler = callback)

#==================
#s.display()

while True:
    host, msg = e.recv()
    if msg:             # msg == None if timeout in recv()
        print(host, msg)
        if msg == b'end':
            break
        elif msg == b'free':
            a=0
            s.display()
            #score = str(score)
            #e.send(score.to_bytes(1, 'big'))
            e.send(str(score))
            e.send(b'end')
        
