import network
import sys
import gc
import utime as time
import ujson as json
import ubinascii as binascii
from machine import Pin, Timer
from microdot import Microdot, send_file

cache_filename = 'cache.json'
wlan_connection = network.STA_IF

buttons = {
    'up'   : Pin(18, Pin.OUT),
    'stop' : Pin(19, Pin.OUT),
    'down' : Pin(20, Pin.OUT)
}

def button_press(button_key):
    button = buttons[button_key]
    button.value(1)
    timer = Timer(-1)
    timer.init(period=1000, mode=Timer.ONE_SHOT, callback=lambda t:button.value(0))

def connect_sta(ssid, password):
    wlan = network.WLAN(wlan_connection)
    wlan.active(True)
    wlan.config(pm=0xa11140)
    wlan.connect(ssid, password)
    
    for i in range(10):
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        print('waiting for connection...')
        time.sleep(1)
    
    if wlan.status() != 3:
        init_ap()
    else:
        print('connected')
        status = wlan.ifconfig()
        print('ip = ' + status[0])
        
def init_ap():
    global wlan_connection
    wlan_connection = network.AP_IF
    ssid = 'Cocopool-' + binascii.hexlify(machine.unique_id()).decode()
    
    ap = network.WLAN(wlan_connection)
    ap.config(essid=ssid, password='123456789')
    ap.active(True)
    
    print('Access point active')
    print(ap.ifconfig())

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

try:
    with open(cache_filename, 'r') as cache:
        data = json.load(cache)
        cache.close()
    
    ssid = data['ssid']
    password = data['password']
    connect_sta(ssid, password)
except Exception as error:
    init_ap()

gc.enable()
gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())

app = Microdot()

@app.route('/')
def index(request):
    if wlan_connection == network.AP_IF:
        return send_file('setup.html')
    
    return send_file('index.html')

@app.route('/save-ssid', methods=['POST'])
def setup(request):
    body = request.json
    keys = body.keys()
    
    if 'ssid' not in keys or 'password' not in keys:
        return 'bad request', 400
    
    with open(cache_filename, 'w') as cache:
        cache.write(json.dumps(body))
        cache.close()
    
    return '', 201

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

if __name__ == '__main__':
    try:
        start_server()
    except KeyboardInterrupt:
        sys.exit(130)
