import bluetooth
from time import sleep_ms

class ESP32_BLE():
    def __init__(self, name):
        #self.led = Pin(2, Pin.OUT)
        #self.timer1 = Timer(0)
        self.connection = True
        self.name = name
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        self.ble.config(gap_name=name)
        self.disconnected()
        self.ble.irq(self.ble_irq)
        self.register()
        self.advertiser()
        self.MSG = ''

    def connected(self):
        self.connection = True
        print('Bluetooth connected...\n')
        #self.led.value(1)
        #self.timer1.deinit()

    def disconnected(self):
        self.connection = False
        print('Bluetooth disconnected...\n')
        #self.timer1.init(period=100, mode=Timer.PERIODIC, callback=lambda t: self.led.value(not self.led.value()))

    def ble_irq(self, event, data):
        #global BLE_MSG
        if event == 1: #_IRQ_CENTRAL_CONNECT  connected
            self.connected()
        elif event == 2: #_IRQ_CENTRAL_DISCONNECT  disconnected
            self.advertiser()
            self.disconnected()
        elif event == 3: #_IRQ_GATTS_WRITE  receive data
            buffer = self.ble.gatts_read(self.rx)
            self.MSG = buffer.decode('UTF-8').strip()
            
    def register(self):        
        #service_uuid = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
        #reader_uuid = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
        #sender_uuid = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'
        sender_uuid = '6d68efe5-04b6-4a85-abc4-c2670b7bf7fd'
        service_uuid = '4fafc201-1fb5-459e-8fcc-c5c9c331914b'
        reader_uuid = '07c4743f-639c-49ab-9d14-31ca27193ad0'

        services = (
            (
                bluetooth.UUID(service_uuid), 
                (
                    (bluetooth.UUID(sender_uuid), bluetooth.FLAG_NOTIFY), 
                    (bluetooth.UUID(reader_uuid), bluetooth.FLAG_WRITE),
                )
            ), 
        )

        ((self.tx, self.rx,), ) = self.ble.gatts_register_services(services)

    def send(self, data):
        self.ble.gatts_notify(0, self.tx, data + '\n')

    def advertiser(self):
        name = bytes(self.name, 'UTF-8')
        adv_data = bytearray('\x02\x01\x02') + bytearray((len(name) + 1, 0x09)) + name
        self.ble.gap_advertise(100, adv_data)
        #print(adv_data)
        #print("\r\n")
        
    def clearMSG(self):
        self.MSG = ''

if __name__ == "__main__":
    ble = ESP32_BLE("ESP32BLE")

    while True:
        print(ble.MSG)
        sleep_ms(1000)

