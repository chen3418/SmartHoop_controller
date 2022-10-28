from machine import I2C, sleep


class accel():
    
    STANDARD_GRAVITY = 9.80665
    def __init__(self, i2c, addr=0x68):
        self.iic = i2c
        self.addr = addr
        #self.iic.start()
        self.iic.writeto(self.addr, bytearray([107, 0]))
        #print(self.iic.readfrom_mem(self.addr, 0x1c, 1))
        self.iic.writeto_mem(self.addr, 0x1c, b'\x10')
        print(self.iic.readfrom_mem(self.addr, 0x1c, 1))
        #self.iic.stop()
    
    def get_acc_data(self):
        a = self.iic.readfrom_mem(self.addr, 0x3B, 2)
        #self.iic.stop()
        b = self.bytes_toint(a[0], a[1])
        return b

    def get_raw_values(self):
        #self.iic.start()
        a = self.iic.readfrom_mem(self.addr, 0x3B, 14)
        #self.iic.stop()
        return a

    def get_ints(self):
        b = self.get_raw_values()
        c = []
        for i in b:
            c.append(i)
        return c

    def bytes_toint(self, firstbyte, secondbyte):
        if not firstbyte & 0x80:
            return firstbyte << 8 | secondbyte
        return - (((firstbyte ^ 255) << 8) | (secondbyte ^ 255) + 1)

    def get_values(self):
        raw_ints = self.get_raw_values()
        vals = {}
        vals["AcX"] = self.bytes_toint(raw_ints[0], raw_ints[1])
        vals["AcY"] = self.bytes_toint(raw_ints[2], raw_ints[3])
        vals["AcZ"] = self.bytes_toint(raw_ints[4], raw_ints[5])
        vals["Tmp"] = self.bytes_toint(raw_ints[6], raw_ints[7]) / 340.00 + 36.53
        vals["GyX"] = self.bytes_toint(raw_ints[8], raw_ints[9])
        vals["GyY"] = self.bytes_toint(raw_ints[10], raw_ints[11])
        vals["GyZ"] = self.bytes_toint(raw_ints[12], raw_ints[13])
        return vals  # returned in range of Int16
        # -32768 to 32767
'''
    def val_test(self):  # ONLY FOR TESTING! Also, fast reading sometimes crashes IIC
        from time import sleep
        while 1:
            print(self.get_values())
            sleep(0.05)
            '''
i2c = I2C(1) 
mpu= accel(i2c)
hit = 0

for i in range(100):
    data = mpu.get_acc_data()# / 4096 
    #sleep(500)
    if data > 700 or data < -700:
        print('hit')
    else:
        print('---')
    #print(hit)
    sleep(100)