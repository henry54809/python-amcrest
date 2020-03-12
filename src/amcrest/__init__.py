# -*- coding: utf-8 -*-
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# vim:sw=4:ts=4:et
import threading
import socket
import queue
from contextlib import closing

from .exceptions import AmcrestError, CommError, LoginError  # noqa: F401
from .http import Http

__RTSP_PORT = 554

def scan_devices(subnet, timeout=None):
    """
    Scan cameras in a range of ips

    Params:
    subnet - subnet, i.e: 192.168.1.0/24
                if mask not used, assuming mask 24

    timeout_sec - timeout in sec

    Returns:
    """
    amcrest_ips = queue.Queue()
    def __raw_scan(ipaddr, timeout=None):
        # If devices not found, try increasing timeout
        socket.setdefaulttimeout(timeout or 0.2)

        with closing(socket.socket()) as sock:
            try:
                sock.connect((ipaddr, __RTSP_PORT))
                amcrest_ips.put(ipaddr)
            # pylint: disable=bare-except
            except:
                pass

    # Maximum range from mask
    # Format is mask: max_range
    max_range = {
        16: 256,
        24: 256,
        25: 128,
        27: 32,
        28: 16,
        29: 8,
        30: 4,
        31: 2
    }

    # If user didn't provide mask, use /24
    if "/" not in subnet:
        mask = int(24)
        network = subnet
    else:
        network, mask = subnet.split("/")
        mask = int(mask)

    if mask not in max_range:
        raise RuntimeError("Cannot determine the subnet mask!")

    # Default logic is remove everything from last "." to the end
    # This logic change in case mask is 16
    network = network.rpartition(".")[0]

    if mask == 16:
        # For mask 16, we must cut the last two
        # entries with .

        # pylint: disable=unused-variable
        for i in range(0, 1):
            network = network.rpartition(".")[0]
    threads = []
    # Trigger the scan
    # For clear coding, let's keep the logic in if/else (mask16)
    # instead of only one if
    if mask == 16:
        for seq1 in range(0, max_range[mask]):
            for seq2 in range(0, max_range[mask]):
                ipaddr = "{0}.{1}.{2}".format(network, seq1, seq2)
                thd = threading.Thread(
                    target=__raw_scan, args=(ipaddr, timeout)
                )
                thd.start()
                threads.append(thd)
    else:
        for seq1 in range(0, max_range[mask]):
            ipaddr = "{0}.{1}".format(network, seq1)
            thd = threading.Thread(
                target=__raw_scan, args=(ipaddr, timeout)
            )
            thd.start()
            threads.append(thd)
    for thread in threads:
        thread.join()
    ips = []
    while not amcrest_ips.empty():
        ips.append(amcrest_ips.get())
    return ips

class AmcrestCamera(object):
    """Amcrest camera object implementation."""

    def __init__(self, host, port, user,
                 password, verbose=True, protocol='http', ssl_verify=True,
                 retries_connection=None, timeout_protocol=None):
        super(AmcrestCamera, self).__init__()
        self.camera = Http(
            host=host,
            port=port,
            user=user,
            password=password,
            verbose=verbose,
            protocol=protocol,
            ssl_verify=ssl_verify,
            retries_connection=retries_connection,
            timeout_protocol=timeout_protocol
        )
