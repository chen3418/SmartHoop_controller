import network
import espnow
from time import sleep


# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.STA_IF)  # Or network.AP_IF
sta.active(True)
sta.disconnect()   # For ESP8266
print(sta.config('mac'))
e = espnow.ESPNow()
e.active(True)
peer = b'\xe8\x9fm%\xaa\\'   # MAC address of peer's wifi interface
e.add_peer(peer)

e.send("Starting...")       # Send to all peers
for i in range(100):
    e.send(peer, str(i)*20, True)
    sleep(0.5)

e.send(b'end')