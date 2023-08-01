import utime as time
import sys
import io
import os

class Logger:
    def __init__(self, error):
        self.__logfile = 'log.txt'
        self.__logfile_backup = 'log-backup.txt'

        self.__cleanup()
        
        now = time.localtime()
        stamp = '[{}-{:02d}-{:02d}, {:02d}:{:02d}:{:02d}]' \
                .format(now[0], now[1], now[2], now[3], now[4], now[5])
        
        buf = io.StringIO()
        sys.print_exception(error, buf)
        
        with open(self.__logfile, 'a') as log:
            log.write('{}:\n{}\n\n'.format(stamp, buf.getvalue()))
            log.close()

    def __cleanup(self):
        files = os.listdir()
        
        if self.__logfile not in files:
            return
            
        size = os.stat(self.__logfile)[6]
        if size < 5 * 1024:
            return
        
        if self.__logfile_backup in files:
            os.remove(self.__logfile_backup)
            
        os.rename(self.__logfile, self.__logfile_backup)
