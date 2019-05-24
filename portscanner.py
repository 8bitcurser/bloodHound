from time import sleep
from pprint import pprint as pp
from socket import (AF_INET, AF_INET6, SOCK_DGRAM, SOCK_STREAM, error,
                    gaierror, socket)
from argparse import ArgumentParser
from datetime import datetime
from subprocess import call

from _thread import start_new_thread

MAX_PORT = 65535
COMMON_PORTS = 1023
MAX_DOTS = 10
LOCALHOST = '127.0.0.1'

PORT_TYPE = {
    'TCP': SOCK_STREAM,
    'UDP': SOCK_DGRAM,
}

HOST_TYPE = {
    'IPV4': AF_INET,
    'IPV6': AF_INET6,
}

scan_type = 'specific'
start = datetime.now()

parser = ArgumentParser()

parser.add_argument(
    '--h', '-host', help='Host to be looked on, e.g. 127.0.0.1',
    default=LOCALHOST
    )

parser.add_argument(
    '--p', '-port', help='Specify the port number to look on, e.g 80',
    default=0
    )

parser.add_argument(
    '--pt', '-porttype', help='Specify the port type e.g ALL, TCP, UDP',
    default='TCP'
    )

parser.add_argument(
    '--ht', '-hosttype', help='Specify the host type e.g ALL, IPV4, IPV6',
    default='IPV4'
    )

parser.add_argument(
    '--f', '-full', help='Initialize a full scan', action='store_true'
    )

parser.add_argument(
    '--c', '-common', help='Initialize a common scan', action='store_true'
    )
args = parser.parse_args()

p_type = PORT_TYPE.get(args.pt)
h_type = HOST_TYPE.get(args.ht)
opened = []
close = []

call('clear', shell=True)


def waiter():
    """Waiter prints while scanning."""
    for i in range(MAX_PORT):
        print('Scanning: ', end='', flush=True)
        for _ in range(MAX_DOTS):
            print('.', end='', flush=True)
            sleep(0.1)
        print('\n')
        call('clear', shell=True)
    print('\n')
    call('clear', shell=True)


def connect(host, port, host_type, port_type):
    """Attempts to connect to a port on a given host.
    :param host: host (str) e.g 127.0.0.1
    :param port: port (int) e.g 80
    :param host_type: connection host type (obj) e.g AF_INET
    :param port_type: connection port type (obj) e.g SOCK_STREAM
    """
    port_type_name = [k for k, v in PORT_TYPE.items() if v == port_type][0]
    try:
        s = socket(host_type, port_type)
        s.connect((host, port))
        s.close()
        opened.append((host, port, port_type_name))
    except gaierror:
        print("Can't resolve hostname")
    except error:
        close.append((host, port, port_type_name))
    except ConnectionRefusedError:
        close.append((host, port, port_type_name))


def special_scans(ports_amount):
    """Given an amount of ports, analize if open or close.
    :params ports_amount: (int) max amount of ports to analyze
    """
    for port in range(ports_amount):
        if args.pt == 'ALL':
            for ptype in PORT_TYPE.values():
                connect(args.h, port, h_type, ptype)
        else:
            connect(args.h, port, h_type, p_type)


if args.f:
    scan_type = 'full'
    start_new_thread(waiter, ())
    special_scans(MAX_PORT)
elif args.c:
    scan_type = 'common'
    start_new_thread(waiter, ())
    special_scans(COMMON_PORTS)
else:
    connect(args.h, int(args.p), h_type, p_type)

end = datetime.now()
delta = end - start

call('clear', shell=True)
print('Scan type: {}'.format(scan_type))
print('Scan took: {} seconds'.format(delta.seconds))
print('Open:')
print('== Amount of open ports: {}'.format(len(opened)))
pp(opened)
print('\nClosed:')
print('== Amount of close ports: {}'.format(len(close)))