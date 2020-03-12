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
import pytz
import tzlocal
import datetime

from amcrest.utils import str2bool, config_parser
from .system import SUPPORTED_TIMEZONES

class Network(object):

    @property
    def wlan_config(self):
        return self.get_config('WLan')

    @property
    def telnet_config(self):
        config = self.get_config('Telnet').replace('table.Telnet.', '').split('\r\n')
        return config_parser(config)

    @telnet_config.setter
    def telnet_config(self, status):
        """
        status:
            false - Telnet is disabled
            true  - Telnet is enabled
        """
        return self.set_config(('Telnet.Enable', 'true' if str2bool(status) else 'false'))

    @property
    def network_config(self):
        config = self.get_config('Network').replace('table.Network.', '').split('\r\n')
        return config_parser(config)

    @property
    def network_interfaces(self):
        ret = self.command(
            'netApp.cgi?action=getInterfaces'
        )
        config = ret.content.decode('utf-8').replace('netInterface[0].', '').split('\r\n')
        return config_parser(config)

    @property
    def upnp_status(self):
        ret = self.command(
            'netApp.cgi?action=getUPnPStatus'
        )
        return ret.content.decode('utf-8')

    @property
    def upnp_config(self):
        config = self.get_config('UPnP').replace('table.UPnP.', '').split('\r\n')
        return config_parser(config)

    @upnp_config.setter
    def upnp_config(self, upnp_opt):
        """
        01/21/2017

        Note 1:
        -------
        The current SDK from Amcrest is case sensitive, do not
        mix UPPERCASE options with lowercase. Otherwise it will
        ignore your call.

        Example:

        Correct:
                "UPnP.Enable=true&UPnP.MapTable[0].Protocol=UDP"

        Incorrect:
            "UPnP.Enable=true&UPnP.Maptable[0].Protocol=UDP"
                                      ^ here should be T in UPPERCASE

        Note 2:
        -------
        In firmware Amcrest_IPC-AWXX_Eng_N_V2.420.AC00.15.R.20160908.bin
        InnerPort was not able to be changed as API SDK 2.10 suggests.

        upnp_opt is the UPnP options listed as example below:
        +-------------------------------------------------------------------+
        | ParamName                      | Value  | Description             |
        +--------------------------------+----------------------------------+
        |UPnP.Enable                     | bool   | Enable/Disable UPnP     |
        |UPnP.MapTable[index].Enable     | bool   | Enable/Disable UPnP map |
        |UPnP.MapTable[index].InnerPort  | int    | Range [1-65535]         |
        |UPnP.MapTable[index].OuterPort  | int    | Range [1-65535]         |
        |UPnP.MapTable[index].Protocol   | string | Range {TCP, UDP}        |
        |UPnP.MapTable[index].ServiceName| string | User UPnP Service name  |
        +-------------------------------------------------------------------+

        upnp_opt format:
        <paramName>=<paramValue>[&<paramName>=<paramValue>...]
        """
        ret = self.command(
            'configManager.cgi?action=setConfig&{0}'.format(upnp_opt)
        )
        return ret.content.decode('utf-8')

    @property
    def ntp_config(self):
        config = self.get_config('NTP').replace('table.NTP.', '').split('\r\n')
        return config_parser(config)

    @ntp_config.setter
    def ntp_config(self, ntp=None):
        """
        ntp_opt is the NTP options listed as example below:

        NTP.Address=clock.isc.org
        NTP.Enable=false
        NTP.Port=38
        NTP.TimeZone=9
        NTP.UpdatePeriod=31

        ntp_opt format:
        <paramName>=<paramValue>[&<paramName>=<paramValue>...]
        """
        if not ntp:
            return self.set_config(('NTP.Enable', 'false'))
        tz = tzlocal.get_localzone()
        if 'timezone' in ntp:
            tz = pytz.timezone(ntp['timezone'])
        tz_offset = SUPPORTED_TIMEZONES.get(tz.localize(datetime.datetime.now()).strftime('%z'))
        assert 'port' in ntp and 'address' in ntp
        config = {
            'NTP.TimeZone': tz_offset,
            'NTP.Enable': 'true',
            'NTP.Port': ntp['port'],
            'NTP.UpdatePeriod': ntp.get('update_min', 10),
            'NTP.Address': ntp['address']
        }
        return self.set_config(*config.items())

    @property
    def rtsp_config(self):
        """Get RTSP configuration."""
        config = self.get_config('RTSP').replace('table.RTSP.', '').split('\r\n')
        return config_parser(config)
