from machine import Pin
from time import sleep_us
from micropython import const

#send data through SPI to WS0010 by bit banging

#delay constant
DelayClock  = const(2)       #delay 2us to slow clock
DelayClear  = const(7000)    #clear screen takes 6.2ms
DelayPower  = const(100000)  #wait 100ms when first power on

# instruction constant
ClearDisplay  = const(0x01)  #clear display, clear takes 6.2ms 
DisplayOn     = const(0x0c)  #00001 100, display on, no cursor, dont blink
FunctionSet   = const(0x3b)  #001 110 11, 8 bits, 2 lines, 8x5, font table 3
ReturnCursor  = const(0x02)  #return cursor to home position
SetIncrement  = const(0x06)  #000001 10, cursor increment, dont shift display

#build char table
CharTable = {}

CharTable = {0: 48, 1: 49, 'K': 75, 'J': 74, 'U': 85, 'T': 84, 'W': 87, 'V': 86, 'Q': 81, 'P': 80, 'S': 83, 'R': 82, '2': 50, 2: 50, 'Y': 89, '3': 51, 'X': 88, 'Z': 90, 3: 51,
             4: 52, 5: 53, '6': 54, 6: 54, 7: 55, '8': 56, 8: 56, ':': 58, 'e': 101, 'd': 100, 'g': 103, 'f': 102, 'a': 97, 'c': 99, 'b': 98, 'm': 109, 'l': 108, 'o': 111, 'n': 110,
             'i': 105, 'h': 104, 'k': 107, 'j': 106, 'u': 117, 't': 116, 'w': 119, 'v': 118, 'q': 113, 'p': 112, 's': 115, 'r': 114, ' ': 32, '5': 53, '4': 52, '7': 55, 'y': 121, 'x': 120,
             '0': 48, '1': 49, 'z': 122, 'E': 69, 'D': 68, 'G': 71, 'F': 70, 'A': 65, 'C': 67, 'B': 66, 'M': 77, 'L': 76, 'O': 79, 'N': 78, 'I': 73, 'H': 72, '+': 43, '-': 45, '.': 46,
             '9': 57}

#for i in range(0,26):
#    CharTable[chr(ord('A')+i)] = 0x41 + i
#    CharTable[chr(ord('a')+i)] = 0x61 + i
    
#for i in range(0,9):
#    CharTable[str(i)] = 0x30 + i
#    CharTable[i] = 0x30 + i
    
#CharTable[' '] = 0x20
#CharTable[':'] = 0x3a

#print(CharTable)

clk = Pin(5, Pin.OUT)
mosi = Pin(17, Pin.OUT)
cs = Pin(16, Pin.OUT)

pb1 = Pin(34, Pin.IN, Pin.PULL_DOWN)
pb2 = Pin(35, Pin.IN, Pin.PULL_DOWN)
pb3 = Pin(32, Pin.IN, Pin.PULL_DOWN)
pb4 = Pin(33, Pin.IN, Pin.PULL_DOWN)


    
def clock():
    
    clk.off()
    sleep_us(DelayClock)
    clk.on()
    sleep_us(DelayClock)
    
    return None


def send(data):
    
    cs.off()  #select the display
    sleep_us(DelayClock)
    
    if len(data) == 10:
        for bit in data:
            if bit:
                mosi.on()
                clock()
            else:
                mosi.off()
                clock()
    else:
        print("data is not 10bits")
        
    sleep_us(DelayClock)    
    cs.on()
    
    return None


def cmd(data):
    
    send_data = [0,0] + HextoList(data)
    send(send_data)
    
    return None

def clr():
    
    cmd(ClearDisplay)
    sleep_us(DelayClear)
    
    return None

def dis(data):
    
    send_data = [1,0] + HextoList(data)
    send(send_data)

    
def HextoList(inp):
    
    I7 = (inp&0x80)>>7
    I6 = (inp&0x40)>>6
    I5 = (inp&0x20)>>5
    I4 = (inp&0x10)>>4
    I3 = (inp&0x08)>>3
    I2 = (inp&0x04)>>2
    I1 = (inp&0x02)>>1
    I0 = (inp&0x01)>>0
    
    return [I7, I6, I5, I4, I3, I2, I1, I0]


def InitializeOLED():
   
    cs.on()
    clk.off()
    sleep_us(DelayPower)
    
    cmd(FunctionSet)
    cmd(DisplayOn)
    clr()
    cmd(ReturnCursor)
    cmd(SetIncrement)
    
    return None

def disp_line1(line):
    
    cmd(0x80)
    for char in line:
        dis(CharTable[char])
    
    return None


def disp_line2(line):
    
    cmd(0x80 + 64)
    for char in line:
        dis(CharTable[char])
    
    return None
    
    
def mode_selection():
    
    global key
    global function_list

    key = 0
    clr()
    disp_line1('Select Mode')
    disp_line2(' F   T   S ')
    while key == 0:
        scan_input()
    
    print('m')
    return function_list[key-1]()

def in_session():
    
    global key
    clr()
    disp_line1('In session...')
    key = 0
    sleep_us(5000000) #hold 5s
    #mode_selection()
    
    return None

def set_timer(t):
    
    global key
    global timer
    
    timer = t
    
    disp1 = 'Timer: ' + str(t) + ' Mins     '
    disp_line1(disp1)
    disp_line2('-1  +1  OK  Back')
    while key < 3:
        scan_input()
        
        if key == 1:
            if timer == 0:
                timer = 99
            else:
                timer -= 1
        elif key == 2:
            if timer == 99:
                timer = 0
            else:
                timer += 1
        disp1 = 'Timer: ' + str(timer) + ' Mins     '
        disp_line1(disp1)
        disp_line2('-1  +1  OK  Back')

    
def time_mode():
    
    global timer
    global key
    
    set_timer(15)
    if key == 3:
        return in_session()

    return None

def free_mode():
    
    return in_session()

def game_mode():
    
    return in_session()

def scan_input(): # keep scanning until button pushed, return accordingly
    
    global key
    key = 0
    
    while key == 0:
        if pb1.value() == 1:
            key = 1
        elif pb2.value() == 1:
            key = 2
        elif pb3.value() == 1:
            key = 3
        elif pb4.value() == 1:
            key = 4
        sleep_us(100000) #scan rate 10/s
        #print(key)
    return None



############### test main ####################################
 
function_list = [free_mode, time_mode, game_mode, mode_selection]
key = 0
timer = 0

InitializeOLED()
for i in range(100):
    mode_selection()
    
#for i in range(500):
#    inpt = pb1.value()
#    print(inpt)
#    #disp_line1(str(inpt))
#    sleep_us(100000) #scan rate 10/s

#sleep_us(10000000)
#disp_line1('Time: 15 mins')
#disp_line2('-1  +1  OK  Back')

#sleep_us(2000000)
#disp_line1('Enter your Name:')
#disp_line2('Aaron J          ')

    
    
    
    
