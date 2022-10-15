import network
import json
import gc
import utime as time
from machine import Pin, Timer
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

for i in range(10):
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    print('waiting for connection...')
    time.sleep(1)

if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')
    status = wlan.ifconfig()
    print('ip = ' + status[0])

def button_press(button_key):
    button = buttons[button_key]
    button.value(1)
    timer = Timer(-1)
    timer.init(period=1000, mode=Timer.ONE_SHOT, callback=lambda t:button.value(0))

gc.enable()
gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())

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

@app.errorhandler(RuntimeError)
def runtime_error(request, exception):
    restart()

def restart():
    gc.collect()
    app.shutdown()
    time.sleep(5)
    start_server()

def start_server():
    try:
        app.run(host='0.0.0.0', port=80)
    except:
        restart()

start_server()
