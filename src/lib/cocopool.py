import network
import sys
import errno
import gc
import utime as time
import ujson as json
import ubinascii as binascii
from machine import Pin, Timer, unique_id
from microdot import Microdot, Request, send_file

app = Microdot()
cache_filename = 'cache.json'

buttons = {
    'up'   : Pin(18, Pin.OUT),
    'stop' : Pin(19, Pin.OUT),
    'down' : Pin(20, Pin.OUT)
}

class Cocopool:
    Request.socket_read_timeout = None

    def __init__(self):
        self.__start_server()

    def __connect_sta(self, ssid, password):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.config(pm=0xa11140)
        wlan.connect(ssid, password)
        
        for i in range(10):
            if wlan.status() < 0 or wlan.status() >= 3:
                break
            print('waiting for connection...')
            time.sleep(1)
        
        if wlan.status() != 3:
            self.__init_ap()
        else:
            print('connected')
            status = wlan.ifconfig()
            print('ip = ' + status[0])
            
        self.__set_hostname()

    def __init_ap(self):
        ssid = 'Cocopool-' + binascii.hexlify(unique_id()).decode()
        
        ap = network.WLAN(network.AP_IF)
        ap.config(essid=ssid, password='123456789')
        ap.active(True)
        
        print('Access point active')
        print(ap.ifconfig())
        
        self.__set_hostname()

    def __set_hostname(self):
        network.hostname('cocopool')
        print('network hostname: ', network.hostname())

    def __restart(self):
        gc.collect()
        app.shutdown()
        time.sleep(5)
        self.__start_server()

    def __start_server(self):
        try:
            with open(cache_filename, 'r') as cache:
                data = json.load(cache)
                cache.close()
            
            ssid = data['ssid']
            password = data['password']
            self.__connect_sta(ssid, password)
        except OSError as exc:
            if exc.errno != errno.ENOENT:
                raise
            
            self.__init_ap()

        gc.enable()
        gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())

        try:
            app.run(host='0.0.0.0', port=80)
        except KeyboardInterrupt:
            sys.exit(130)
        except:
            self.__restart()

    @app.get('/')
    def index(request):
        if network.WLAN().isconnected() == False:
            return send_file('setup.html')
        
        return send_file('index.html')

    @app.post('/save-ssid')
    def setup(request):
        body = request.json
        keys = body.keys()
        
        if 'ssid' not in keys or 'password' not in keys:
            return 'bad request', 400
        
        with open(cache_filename, 'w') as cache:
            cache.write(json.dumps(body))
            cache.close()
        
        return '', 200

    @app.get('/static/<path:path>')
    def static(request, path):
        if '..' in path:
            return 'Not found', 404
        return send_file('static/' + path)

    @app.get('/button/<direction>')
    def handle(request, direction):
        button = buttons[direction]
        button.value(1)
        timer = Timer(-1)
        timer.init(period=1000, mode=Timer.ONE_SHOT, callback=lambda t:button.value(0))
        
        return '', 200

    @app.errorhandler(RuntimeError)
    def runtime_error(request, exception):
        gc.collect()
        app.shutdown()
        time.sleep(5)
        
        try:
            app.run(host='0.0.0.0', port=80)
        except KeyboardInterrupt:
            sys.exit(130)
