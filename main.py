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

html = """
<!DOCTYPE html>
<html>
<head>
  <title>Cocopool Remote</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body, html {
      background-color: #ebecf0;
      font-family: sans-serif;
      font-size: 16px;
    }

    div, p {
      color: #babecc;
      text-shadow: 1px 1px 1px white;
    }

    .container-buttons {
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
    }

    .button {
      display: block;
      position: relative;
      width: 80px;
      height: 80px;
      box-sizing: content-box;
      padding: 20px;
      background-color: #ebecf0;
      color: #61677c;
      font-weight: bold;
      border: 0;
      outline: 0;
      font-size: 16px;
      border-radius: 20px;
      box-shadow: -5px -5px 20px white, 5px 5px 20px #babecc;
      transition: all 0.2s ease-in-out;
      cursor: pointer;
      font-weight: 600;
      margin: 20px;
      -webkit-tap-highlight-color: transparent;
    }

    .button:active {
      box-shadow: inset 1px 1px 2px #babecc, inset -1px -1px 2px white;
    }

    .arrow {
      position: absolute;
      transform: translate(-50%, -50%);
      left: 50%;
      top: 50%;
      width: 0;
      height: 0;
      border-left: 18px solid transparent;
      border-right: 18px solid transparent;
    }

    .arrow-up {
      border-bottom: 30px solid #babecc;
    }

    .arrow-down {
      border-top: 30px solid #babecc;
    }

    .arrow-stop {
      border: 15px solid #babecc;
    }

    @media (orientation: landscape) {
      .container-buttons {
        position: fixed;
        width: 100%;
        text-align: center;
      }

      .button {
        display: inline-block;
        margin: 10px;
      }
    }
  </style>
</head>
<body>
  <div>
    <div class="container-buttons">
      <button class="button" name="UP">
        <div class="arrow arrow-up"></div>
      </button>
      <button class="button" name="STOP">
        <div class="arrow arrow-stop"></div>
      </button>
      <button class="button" name="DOWN">
        <div class="arrow arrow-down"></div>
      </button>
    </div>
  </div>
  <script type="text/javascript">
    (function() {
      var buttons = document.getElementsByClassName('button');

      for (var i = 0; i < buttons.length; ++i) {
        buttons[i].addEventListener('click', function(e) {
          var name = e.currentTarget.name;
          var http = new XMLHttpRequest();

          http.open('HEAD', './?TOP=' + name);
          http.send();
        });
      }
    })();
  </script>
</body>
</html>
"""

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
