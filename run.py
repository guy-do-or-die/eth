#! .env/bin/python

import multiprocessing
import socket
import http
import sys

from burn import reg, log, check

import config


if __name__ == '__main__':
    try:
        log('welcome!')
        #reg()
        check()
    except (socket.error,
            KeyboardInterrupt,
            http.client.RemoteDisconnected) as e:
        log(e, type='error')
        log('bye!')
