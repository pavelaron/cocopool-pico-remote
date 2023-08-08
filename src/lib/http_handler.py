import re
import errno
import uos as os
import usocket as socket
import ujson as json

from network import WLAN
from machine import Pin, Timer, WDT

types_map = {
    'css'  : 'text/css',
    'gif'  : 'image/gif',
    'html' : 'text/html',
    'jpg'  : 'image/jpeg',
    'js'   : 'application/javascript',
    'json' : 'application/json',
    'png'  : 'image/png',
    'txt'  : 'text/plain',
}

buttons = {
    'up'   : Pin(18, Pin.OUT),
    'stop' : Pin(19, Pin.OUT),
    'down' : Pin(20, Pin.OUT),
}

class HttpHandler:
    def __init__(self, ip, cache_filename):
        self.__ip = ip
        self.__connection = socket.socket()
        self.__cache_filename = cache_filename
        self.__btn_timer = Timer(-1)

    def __open_socket(self):
        address = (self.__ip, 80)
        self.__connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__connection.bind(address)
        self.__connection.listen(1)

    def listen(self):
        print('Listening for requests...')

        self.__open_socket()
        self.__wdt_init()
        
        while True:
            client = self.__connection.accept()[0]
            
            self.__router(client)
            client.close()

    def __wdt_init(self):
        wdt = WDT(timeout=8000)
        wdt.feed()
        
        wdt_timer = Timer(-1)
        wdt_timer.init(mode=Timer.PERIODIC, freq=1000, \
            callback=lambda t:self.__check_connection(wdt))

    def __check_connection(self, wdt):
        if 'state=1' not in str(self.__connection):
            return

        wdt.feed()

    def __router(self, client):
        request = client.recv(1024)
        lines = request.splitlines()
        
        if not lines:
            client.send('HTTP/1.0 400 Bad request\r\n')
            return
        
        route = lines[0]
        
        if re.search('/save-ssid', route):
            body = json.loads(lines[-1].decode('utf-8'))
            keys = body.keys()
            
            if 'ssid' not in keys or 'password' not in keys:
                client.send('HTTP/1.0 400 Bad request\r\n')
                return
            
            with open(self.__cache_filename, 'w') as cache:
                cache.write(json.dumps(body))
                cache.close()
            
            client.send('HTTP/1.0 200 OK\r\n')
        elif re.search('/button/\S+', route):
            direction = re.search('/button/(\S+)', route).group(1).decode('utf-8')
            button = buttons[direction]
            button.value(1)
            self.__btn_timer.init(period=1000, mode=Timer.ONE_SHOT, \
                callback=lambda t:button.value(0))
            
            client.send('HTTP/1.0 200 OK\r\n')
        elif re.search(r'/static/\S+', route):
            client.send('HTTP/1.0 200 OK\r\n')
            path = re.search(r'static/\w+\.?\S*', route)
            filename = path.group(0).decode('utf-8')
            
            ext = filename.split('.')[-1]
            content_type = types_map[ext] if ext in types_map \
                           else 'application/octet-stream'
            
            client.send('Content-Type: ' + content_type + '\r\n')
            client.send('Content-Length: ' + str(os.stat(filename)[6]) + '\r\n\r\n')
            
            self.__send_file(filename, client)
        elif re.search(r'/log', route):
            self.__send_file('log.txt', client)
        elif re.search(r'/log-backup', route):
            self.__send_file('log-backup.txt', client)
        else:
            client.send('HTTP/1.0 200 OK\r\n')
            client.send('Content-Type: text/html; charset=UTF-8\r\n\r\n')
            self.__root(client)

    def __root(self, client):
        html_path = 'index' if WLAN().isconnected() else 'setup'
        self.__send_file(html_path + '.html', client)

    def __send_file(self, filename, client):
        try:
            with open(filename, 'rb') as f:
                while True:
                    data = f.read(1024)
                    if not data:
                        break
                    client.sendall(data)
                
                f.close()
                client.send('\r\n')
        except OSError as exc:
            if exc.errno != errno.ENOENT:
                raise
            
            client.send('HTTP/1.0 404 Not Found\r\n')
