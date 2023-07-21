import network
import re
import os
import usocket as socket
import ujson as json

from machine import Pin, Timer

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
    'down' : Pin(20, Pin.OUT)
}

class HttpHandler:
    def __init__(self, ip, cache_filename):
        self.__ip = ip
        self.__cache_filename = cache_filename
    
    def __open_socket(self):
        address = (self.__ip, 80)
        connection = socket.socket()
        connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        connection.bind(address)
        connection.listen(1)
        
        return connection

    def listen(self):
        print('Listening for requests...')
        connection = self.__open_socket()
        
        while True:
            client = connection.accept()[0]
            
            self.__router(client)
            client.close()
            
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
            timer = Timer(-1)
            timer.init(period=1000, mode=Timer.ONE_SHOT, callback=lambda t:button.value(0))
            
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
        else:
            client.send('HTTP/1.0 200 OK\r\n')
            client.send('Content-Type: text/html; charset=UTF-8\r\n\r\n')
            self.__root(client)
            
        
    def __root(self, client):
        html_path = 'index' if network.WLAN().isconnected() else 'setup'
        self.__send_file(html_path + '.html', client)
            
    def __send_file(self, filename, client):
        with open(filename, 'rb') as f:
            while True:
                data = f.read(1024)
                if not data:
                    break
                client.sendall(data)
            
            f.close()
            client.send('\r\n')
