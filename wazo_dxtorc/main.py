#!/usr/bin/env python3
# Copyright 2010-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


"""Small client program that send DHCP information to a transfer agent via
a Unix datagram socket.

The client takes the DHCP information from its command line. For example, if
the lease 192.168.1.1 has just been committed by the DHCP server to the DHCP
client with the MAC address 00:11:22:33:44:55, if the script had been called
from a shell, it could have looked like:

  dxtorc 'commit' '192.168.1.1' '0:11:22:33:44:55'

It can also take additional info about the DHCP request. Here's an example
of sending the value of the vendor-class-identifier option, in this case,
'foobar':

  dxtorc 'commit' '192.168.1.1' '0:11:22:33:44:55' '06066.6f.6f.62.61.72.a'

Note: the first 3 digits represent the decimal value of the DHCP option and
      everything after is the hexadecimal representation of the raw value
      of the option, separated by dot.

Empty arguments after the MAC address are ignored.

The first argument can also be one of 'release' or 'expiry'. In this case,
only the IP address needs to be passed to the client:

  dxtorc 'release' '192.168.1.1'

"""

import io
import socket
import sys

UNIX_SERVER_ADDR = '/run/wazo-dxtora/wazo-dxtora.ctl'


def msg_exit(err_msg):
    print(err_msg, file=sys.stderr)
    sys.exit(1)


def parse_args(args):
    """Return a dhcp_info object from the command line arguments..."""
    dhcp_info = {}
    try:
        dhcp_info['op'] = args[0]
        dhcp_info['ip'] = args[1]
        if dhcp_info['op'] == 'commit':
            dhcp_info['mac'] = args[2]
            dhcp_info['options'] = filter(None, args[3:])
        elif dhcp_info['op'] in ('expiry', 'release'):
            pass
        else:
            msg_exit('error: invalid operation')
    except IndexError:
        msg_exit('error: not enough arguments')
    else:
        return dhcp_info


def build_dgram(dhcp_info):
    """Return a datagram from an dhcp_info object..."""
    s = io.StringIO()

    def append(v):
        s.write(v + '\n')

    append(dhcp_info['op'])
    append(dhcp_info['ip'])
    if dhcp_info['op'] == 'commit':
        append(dhcp_info['mac'])
        for option in dhcp_info['options']:
            append(option)
    return s.getvalue().encode('utf-8')


def send_dgram(dgram):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    # It's important to set the socket to non-blocking since we do not
    # want to slow down the calling process (i.e. the DHCP server).
    s.setblocking(0)
    try:
        s.sendto(dgram, UNIX_SERVER_ADDR)
    except OSError:
        msg_exit('error: could not send data to remote socket')
    finally:
        s.close()


def main():
    send_dgram(build_dgram(parse_args(sys.argv[1:])))
