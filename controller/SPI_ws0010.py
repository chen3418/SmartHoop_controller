from machine import Pin
from time import sleep_us, sleep_ms, sleep
from micropython import const
from C_BLE import ESP32_BLE
import network
import espnow
import bluetooth

#send data through SPI to WS0010 by bit banging
class Controller():
    
    #=====================ESP-NOW
    sta = network.WLAN(network.STA_IF)  # Or network.AP_IF
    sta.active(True)

    print(sta.config('mac'))
    e = espnow.ESPNow()
    e.active(True)
    peer = b'\xc4\xddW\xcaI\xb0'   # MAC address of backboard
    e.add_peer(peer)
    #=====================
    
    #=====================BLE
    if_BLE = 0
    score = ''
    BLE = ESP32_BLE("controller")
    #=================================

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

    # some ASCII code for letter
    Space = const(32)
    LetterA = const(65)
    LetterZ = const(90)

    #build char table
    #CharTable = {}

    CharTable = {0: 48, 1: 49, 'K': 75, 'J': 74, 'U': 85, 'T': 84, 'W': 87, 'V': 86, 'Q': 81, 'P': 80, 'S': 83, 'R': 82, '2': 50, 2: 50, 'Y': 89, '3': 51, 'X': 88, 'Z': 90, 3: 51,
                 4: 52, 5: 53, '6': 54, 6: 54, 7: 55, '8': 56, 8: 56, ':': 58, 'e': 101, 'd': 100, 'g': 103, 'f': 102, 'a': 97, 'c': 99, 'b': 98, 'm': 109, 'l': 108, 'o': 111, 'n': 110,
                 'i': 105, 'h': 104, 'k': 107, 'j': 106, 'u': 117, 't': 116, 'w': 119, 'v': 118, 'q': 113, 'p': 112, 's': 115, 'r': 114, ' ': 32, '5': 53, '4': 52, '7': 55, 'y': 121, 'x': 120,
                 '0': 48, '1': 49, 'z': 122, 'E': 69, 'D': 68, 'G': 71, 'F': 70, 'A': 65, 'C': 67, 'B': 66, 'M': 77, 'L': 76, 'O': 79, 'N': 78, 'I': 73, 'H': 72, '+': 43, '-': 45, '.': 46,
                 '9': 57, '?': 0x3f}

    LetterList = [' ', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g',
                  'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

    def __init__(self):
        self.key = 0
        self.function_list = [self.free_mode, self.time_mode, self.game_mode, self.mode_selection]
        #self.if_BLE = 0
        #self.e = 0
        #self.score = 0
        self.timer = 15
        #self.BLE_MSG = ''
        self.name = '                '
        self.LetterIndex = 1
        
        #assign pins
        self.clk = Pin(27, Pin.OUT)
        self.mosi = Pin(14, Pin.OUT)
        self.cs = Pin(12, Pin.OUT)

        self.pb1 = Pin(32, Pin.IN, Pin.PULL_UP)
        self.pb2 = Pin(33, Pin.IN, Pin.PULL_UP)
        self.pb3 = Pin(25, Pin.IN, Pin.PULL_UP)
        self.pb4 = Pin(26, Pin.IN, Pin.PULL_UP)
        

    def clock(self):
        self.clk.off()
        sleep_us(self.DelayClock)
        self.clk.on()
        sleep_us(self.DelayClock)


    def send(self, data): 
        self.cs.off()  #select the display
        sleep_us(self.DelayClock)
        
        if len(data) == 10:
            for bit in data:
                if bit:
                    self.mosi.on()
                    self.clock()
                else:
                    self.mosi.off()
                    self.clock()
        else:
            print("data is not 10bits")
            
        sleep_us(self.DelayClock)    
        self.cs.on()


    def cmd(self, data):
        send_data = [0,0] + self.HextoList(data)
        self.send(send_data)


    def clr(self):
        self.cmd(self.ClearDisplay)
        sleep_us(self.DelayClear)
        

    def cursor_on(self):
        self.cmd(0x0e)

    def cursor_off(self):
        self.cmd(0x0c)

    def dis(self, data):
        send_data = [1,0] + self.HextoList(data)
        self.send(send_data)

        
    def HextoList(self, inp): 
        I7 = (inp&0x80)>>7
        I6 = (inp&0x40)>>6
        I5 = (inp&0x20)>>5
        I4 = (inp&0x10)>>4
        I3 = (inp&0x08)>>3
        I2 = (inp&0x04)>>2
        I1 = (inp&0x02)>>1
        I0 = (inp&0x01)>>0
        
        return [I7, I6, I5, I4, I3, I2, I1, I0]


    def InitializeOLED(self):
        self.cs.on()
        self.clk.off()
        sleep_us(self.DelayPower)
        
        self.cmd(self.FunctionSet)
        self.cmd(self.DisplayOn)
        self.clr()
        self.cmd(self.ReturnCursor)
        self.cmd(self.SetIncrement)
        

    def disp_line1(self, line):
        
        self.cmd(0x80)
        for char in line:
            self.dis(self.CharTable[char])


    def disp_line2(self, line):
        
        self.cmd(0x80 + 64)
        for char in line:
            self.dis(self.CharTable[char])
        

    def disp_one_char_at_pos(self, pos, char):
        
        self.cmd(0x80 + pos)
        self.dis(self.CharTable[char])
        

    def shift_cursor_left(self):
        self.cmd(0x10)
        
    def shift_cursor_right(self):
        self.cmd(0x14)
        
    def mode_selection(self):
        self.key = 0
        self.clr()
        self.disp_line1('Select Mode')
        self.disp_line2(' F   T   S ')
        while self.key == 0:
            self.scan_input()
            if self.if_BLE:
                print('in bluetooth...\n')
                return self.BLE_mode()
            #print('in bluetooth...\n')
        print('function selected')
        
        return self.function_list[self.key-1]()

    def in_session(self):
        global e
        global key
        global score
        self.clr()
        self.disp_line1('In session...')
        while True:
            sleep(5)
            break
            host, msg = self.e.recv()
            if msg:             # msg == None if timeout in recv()
                print(host, msg)
                if msg == b'end':
                    break
                else:
                    self.score = msg
                
        self.key = 0


    def set_timer(self, t):
        self.timer = t
        
        disp1 = 'Timer: ' + str(t) + ' Mins     '
        self.disp_line1(disp1)
        self.disp_line2('-1  +1  OK  Back')
        while self.key < 3:
            self.scan_input()
            
            if self.key == 1:
                if self.timer == 0:
                    self.timer = 99
                else:
                    self.timer -= 1
            elif self.key == 2:
                if self.timer == 99:
                    self.timer = 0
                else:
                    self.timer += 1
            disp1 = 'Timer: ' + str(self.timer) + ' Mins     '
            self.disp_line1(disp1)
            #disp_line2('-1  +1  OK  Back')

        
    def time_mode(self):
        self.set_timer(15)
        if self.key == 3:
            return self.in_session()


    def free_mode(self):
        self.e.send('free')
        return self.in_session()

    def BLE_mode(self):
        while self.if_BLE:
            if self.BLE.MSG == 'free':
                self.BLE.clearMSG()
                self.e.send('free')
                return self.in_session()
                print('free mode')
            else:
                print(self.BLE.MSG)
                self.BLE.clearMSG()
            sleep_us(100000)
        
        return self.mode_selection()

    def game_mode(self):
        
        # signal the board
        # show in session
        self.in_session()
        
        # receive signal from board (istop10 == true)
            # let user input their name
            # send name to board 
        if 1 : #should detect if score is in top 10
            self.clr()
            self.disp_line1('You are in Top10')
            self.disp_line2('Leave a name')
            sleep_us(2000000)
            
            self.input_name()


    def input_name(self):
        
        self.name = '                '
        letter = ' '
        
        cursor_pos = 0 #track position of cursor, start at 0, also the size of name, should be 0-15
        self.cursor_on()
        self.clr()
        self.disp_line2('prv nxt  OK Back')
        self.disp_one_char_at_pos(cursor_pos, letter)
        self.shift_cursor_left()
        
        while True:
        # if cursor_pos == 0 and user hit back print confirm? Y   N
        # elif cursor_pos == 15 and user hit ok print confirm? Y   N
            self.key = 0
            letter = self.name[cursor_pos]
            self.LetterIndex = self.LetterList.index(letter)
            self.disp_one_char_at_pos(cursor_pos, letter)
            self.shift_cursor_left()
            
            while self.key < 3:
                self.scan_input() #wait until user press a key
            
            #shift in LetterList to find the letter user wants
                if self.key == 1:
                    if self.LetterIndex == 0:
                        self.LetterIndex = 52
                    else:
                        self.LetterIndex -= 1
                
                elif self.key == 2:
                    if self.LetterIndex == 52:
                        self.LetterIndex = 0
                    else:
                        self.LetterIndex += 1
            
                letter = self.LetterList[self.LetterIndex]
                self.disp_one_char_at_pos(cursor_pos, letter)
                self.shift_cursor_left()
                #disp_line2('prv nxt  OK Back')
            
            if self.key == 3:
                if cursor_pos == 15:
                    self.disp_line2('confirm?   Y  N ')
                    self.key = 0
                    while self.key < 3:
                        self.scan_input()
                    if self.key == 3:
                        self.cursor_off()
                        #send name to board
                        return None
                    else:
                        self.disp_line2('prv nxt  OK Back')
                        #disp_one_char_at_pos(cursor_pos, letter)
                        #shift_cursor_left()
                
                else:
                    list1 = list(self.name)
                    list1[cursor_pos] = letter
                    name = ''.join(list1)
                    cursor_pos += 1
                    #letter = name[cursor_pos]
                    #LetterIndex = LetterList.index(letter)
                    #cursor_pos += 1
                    #letter = ' '
                    #disp_one_char_at_pos(cursor_pos, letter)
                    
            else: #key == 4   
                if cursor_pos == 0:
                    self.key = 0
                    self.disp_line2('exit?    Y   N  ')
                    while self.key < 3:
                        self.scan_input()
                    if self.key == 3:
                        self.name = 'Anonymous'
                        self.cursor_off()
                        # back to mode selection
                        # sent name to board
                        return None
                    else:
                        self.disp_line2('prv nxt  OK Back')
                else:
                    if letter != ' ':
                        list1 = list(name)
                        list1[cursor_pos] = letter
                        self.name = ''.join(list1)
                    
                    cursor_pos -= 1
                    #letter = name[cursor_pos]
                    #LetterIndex = LetterList.index(letter)
                    #list1 = list(name)
                    #list1[cursor_pos] = letter
                    #name = ''.join(list1)
                    

    def scan_input(self): # keep scanning until button pushed, return accordingly
        self.key = 0
        
        while self.key == 0 and not self.if_BLE:
            if self.pb1.value() == 0:
                #print(pb1.value())
                self.key = 1
            elif self.pb2.value() == 0:
                self.key = 2
            elif self.pb3.value() == 0:
                self.key = 3
            elif self.pb4.value() == 0:
                self.key = 4
            
            sleep_us(100000) #scan rate 10/s
            print(self.key)
        return None



############### test main ####################################
if __name__ == "__main__":
    '''
    ble = ESP32_BLE("controller")

    function_list = [free_mode, time_mode, game_mode, mode_selection]
    key = 0
    timer = 0
    LetterIndex = 1
    istop10 = True
    name = '                '
'''
    c = Controller()
    c.InitializeOLED()
    
    for i in range(10):  
        c.mode_selection()
        print(c.name)
        #ble.send(score)
        sleep_us(100000)
        
    c.clr()
    c.disp_line1('Test End')
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







#for i in range(0,26):
#    CharTable[chr(ord('A')+i)] = 0x41 + i
#    CharTable[chr(ord('a')+i)] = 0x61 + i
    #LetterList.append(chr(ord('a') + i))

#print(LetterList)
#for i in range(0,9):
#    CharTable[str(i)] = 0x30 + i
#    CharTable[i] = 0x30 + i
    
#CharTable[' '] = 0x20
#CharTable[':'] = 0x3a

#print(CharTable)

   
    
    
    
