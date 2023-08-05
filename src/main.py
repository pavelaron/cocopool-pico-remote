import machine

from cocopool import Cocopool
from logger import Logger

if __name__ == '__main__':
    try:
        Cocopool()
    except Exception as error:
        Logger(error)
        machine.reset()
