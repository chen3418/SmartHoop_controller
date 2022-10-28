from machine import I2C
from machine import Pin
from machine import sleep
import mpu6050
i2c = I2C(1)     #initializing the I2C method for ESP32
#i2c = I2C(scl=Pin(5), sda=Pin(4))       #initializing the I2C method for ESP8266
mpu= mpu6050.accel(i2c)
while True:
    data = mpu.get_acc_data()
    sleep(500)
    print(data)
    sleep(500)