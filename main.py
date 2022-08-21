import network
import socket
import time
import json
from machine import Pin

config_file = open('config.json')
config = json.loads(config_file.read())

ssid = config['wlan']['ssid']
password = config['wlan']['password']

buttons = {
    'up': Pin(18, Pin.OUT),
    'stop': Pin(19, Pin.OUT),
    'down': Pin(20, Pin.OUT)
}

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.config(pm = 0xa11140)
wlan.connect(ssid, password)

htmlFile = open('index.html', 'r')
html = htmlFile.read()

def button_press(button_key, cl):
    cl.send('HTTP/1.0 200 OK\r\n\r\n')
    cl.close()

    button = buttons[button_key]
    button.value(1)
    time.sleep(0.25)
    button.value(0)

max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)

print('listening on', addr)

# Listen for connections
while True:
    try:
        cl, addr = s.accept()
        print('client connected from', addr)
        request = cl.recv(1024)
        print(request)

        query = str(request).splitlines()[0]

        if query.find('TOP=UP') != -1:
            button_press('up', cl)
        elif query.find('TOP=STOP') != -1:
            button_press('stop', cl)
        elif query.find('TOP=DOWN') != -1:
            button_press('down', cl)
        else:
            cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            cl.send(html)
            cl.close()

    except OSError as e:
        cl.close()
        print('connection closed')
