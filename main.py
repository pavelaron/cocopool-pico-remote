import network
import time
import json
from machine import Pin
from microdot import Microdot, send_file

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

def button_press(button_key):
    button = buttons[button_key]
    button.value(1)
    time.sleep(1)
    button.value(0)

app = Microdot()

@app.route('/')
def index(request):
    return send_file('index.html')

@app.route('/static/<path:path>')
def static(request, path):
    if '..' in path:
        return 'Not found', 404
    return send_file('static/' + path)

@app.route('/button/<direction>', methods=['HEAD'])
def handle(request, direction):
    button_press(direction)
    return '', 200

app.run(host='0.0.0.0', port=80)
