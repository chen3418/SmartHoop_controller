from machine import Pin, Timer, RTC
from time import sleep_us
import machine
import time

#machine.freq(160000000)
'''
display_buffer = [
    b'\x00\x00\x00\x00\x00\x00\x00\x00', 
    b'\x00\x00\x00\x00\x00\x00\x00\x00', 
    b'\x0e\x00\x00\x00\x00\x00\x00\x00', 
    b'\x0f\x00\x00\x00\x00\x00\x00\x00', 
    b'\x1b\x00\x00\x00\x00\x00\x00\x00', 
    b'\x18\x00\x00\x00\x00\x00\x00\x00', 
    b'\x1e\x00\x00\x00\x00\x00\x00\x00', 
    b'\x1f\x00\x00\x00\x00\x00\x00\x00', 
    b'\x1b\x00\x00\x00\x00\x00\x00\x00', 
    b'\x1b\x00\x00\x00\x00\x00\x00\x00', 
    b'\x1b\x00\x00\x00\x00\x00\x00\x00', 
    b'\x1b\x00\x00\x00\x00\x00\x00\x00', 
    b'\x1f\x00\x00\x00\x00\x00\x00\x00', 
    b'\x0e\x00\x00\x00\x00\x00\x00\x00', 
    b'\x00\x00\x00\x00\x00\x00\x00\x00', 
    b'\x00\x00\x00\x00\x00\x00\x00\x00'
]'''

'''
inp = [    0x00, 0x00, 
    0x00, 0x00, 
    0x0e, 0x00, 
    0x1f, 0x00, 
    0x1b, 0x00, 
    0x1b, 0x00, 
    0x1b, 0x00, 
    0x1b, 0x00, 
    0x1f, 0x00, 
    0x1f, 0x00, 
    0x03, 0x00, 
    0x1b, 0x00, 
    0x1e, 0x00, 
    0x1e, 0x00, 
    0x00, 0x00, 
    0x00, 0x00]

ou = []
for x in range(32):
    if x%2 == 0:
        ou.append(inp[x])
print(ou)
'''

class matrix:
    
    R1 = Pin(33, Pin.OUT)
    R2 = Pin(25, Pin.OUT)
    G1 = Pin(0, Pin.OUT)
    G2 = Pin(16, Pin.OUT)
    B1 = Pin(32, Pin.OUT)
    #B2 = Pin(13, Pin.OUT)
    hspi = machine.SPI(1, 10000000) # mosi->p13 as B2
    
    R1.off()
    R2.off()
    G1.off()
    G2.off()
    B1.off()

    A = Pin(12, Pin.OUT)
    B = Pin(5, Pin.OUT)
    C = Pin(26, Pin.OUT)
    D = Pin(18, Pin.OUT)

    A.off()
    B.off()
    C.off()
    D.off()
    
    #CLK = Pin(18, Pin.OUT) CLK is hspi clk @ 10MHz
    OE  = Pin(27, Pin.OUT)
    LAT = Pin(19, Pin.OUT)

    OE.on() # active low
    LAT.off()
    
    
    def __init__(self):
        self.buffer = [bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00'),
                  bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00'),
                  bytearray(b'\x0e\x00\x00\x00\x00\x00\x00\x00'),
                  bytearray(b'\x1f\x00\x00\x00\x00\x00\x00\x00'),
                  bytearray(b'\x1b\x00\x00\x00\x00\x00\x00\x00'),
                  bytearray(b'\x1b\x00\x00\x00\x00\x00\x00\x00'),
                  bytearray(b'\x1b\x00\x00\x00\x00\x00\x00\x00'),
                  bytearray(b'\x1b\x00\x00\x00\x00\x00\x00\x00'),
                  bytearray(b'\x1b\x00\x00\x00\x00\x00\x00\x00'),
                  bytearray(b'\x1b\x00\x00\x00\x00\x00\x00\x00'),
                  bytearray(b'\x1b\x00\x00\x00\x00\x00\x00\x00'),
                  bytearray(b'\x1b\x00\x00\x00\x00\x00\x00\x00'),
                  bytearray(b'\x1f\x00\x00\x00\x00\x00\x00\x00'),
                  bytearray(b'\x0e\x00\x00\x00\x00\x00\x00\x00'),
                  bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00'),
                  bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00')]
        
        self.table =[[0, 0, 14, 31, 27, 27, 27, 27, 27, 27, 27, 27, 31, 14, 0, 0],
                [0, 0, 6, 14, 30, 6, 6, 6, 6, 6, 6, 6, 31, 31, 0, 0],
                [0, 0, 14, 31, 27, 27, 27, 3, 6, 14, 13, 27, 31, 31, 0, 0],
                [0, 0, 14, 31, 27, 27, 7, 14, 7, 3, 27, 27, 31, 30, 0, 0],
                [0, 0, 6, 6, 14, 14, 14, 30, 26, 31, 31, 6, 15, 15, 0, 0],
                [0, 0, 31, 31, 24, 24, 30, 31, 3, 3, 27, 27, 31, 14, 0, 0],
                [0, 0, 14, 15, 27, 24, 30, 31, 27, 27, 27, 27, 31, 14, 0, 0],
                [0, 0, 31, 31, 27, 22, 6, 6, 6, 12, 12, 12, 12, 12, 0, 0],
                [0, 0, 14, 31, 27, 27, 31, 14, 31, 27, 27, 27, 31, 14, 0, 0],
                [0, 0, 14, 31, 27, 27, 27, 27, 31, 31, 3, 27, 30, 14, 0, 0]]
        
    def swap(self, pos, num):
        for x in range(16):
            self.buffer[x][pos]= self.table[num][x]
  


    def select_line(self, num):
        
        ID = (num&0x8)>>3
        IC = (num&0x4)>>2
        IB = (num&0x2)>>1
        IA = (num&0x1)>>0
        
        self.A.value(IA)
        self.B.value(IB)
        self.C.value(IC)
        self.D.value(ID)

    def display(self):
        c = 0
        b = 0
        a = 0
        for x in range(4800):
            #if b == 320:
             #   self.swap(0, a%10)
             #   b = 0
              #  a += 1
            for y in self.buffer:
                #print(type(x))
                self.select_line(c%16)
                c+=1
                self.hspi.write(y)
                self.LAT.on()
                self.LAT.off()
                self.OE.off()
                sleep_us(100)
                self.OE.on()
            #b+= 1
                #if c == 16:
                 #   c = 0
            #end of 1 frame
            #b += 1
        

#========================test==================================

#start = time.ticks_ms()
#s = matrix()
#delta = time.ticks_diff(time.ticks_ms(), start)
#print(delta)
#a = 0
#def callback(pin):
#    timer2 = Timer(2)
#    timer2.init(period=25, mode=Timer.ONE_SHOT, callback= lambda t: spress())
    
#def spress():
    #global table
    #global s
#    global a
    #print('call back')
#   s.swap(0, a%10)
#    a +=1

#pb1 = Pin(15, Pin.IN, Pin.PULL_UP)
#pb1.irq(trigger=Pin.IRQ_FALLING,handler = callback)

#s.display()
#delta = time.ticks_diff(time.ticks_ms(), start)
#print(delta)

