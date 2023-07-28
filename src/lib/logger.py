import utime as time
import sys
import io

class Logger:
    def __init__(self, error):
        now = time.localtime()
        stamp = '[{}-{:02d}-{:02d}, {:02d}:{:02d}:{:02d}]' \
                .format(now[0], now[1], now[2], now[3], now[4], now[5])
        
        buf = io.StringIO()
        sys.print_exception(error, buf)
        
        with open('log.txt', 'a') as log:
            log.write('{}:\n{}\n\n'.format(stamp, buf.getvalue()))
            log.close()
