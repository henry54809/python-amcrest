"""Amcrest system module."""
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

import datetime
import pytz

from amcrest.utils import str2bool

SUPPORTED_TIMEZONES = dict([(k, v) for v, k in enumerate([
    '+0000', '+0100', '+0200', '+0300', '+0330', '+0400', '+0430', '+0500',
    '+0530', '+0545', '+0600', '+0630', '+0700', '+0800', '+0900', '+0930',
    '+1000', '+1100', '+1200', '+1300', '-0100', '-0200', '-0300', '-0330',
    '-0400', '-0500', '-0600', '-0700', '-0800', '-0900', '-1000', '-1100', '-1200'
    ])
])

class System(object):
    """Amcrest system class."""
    @property
    def current_time(self):
        ret = self.command(
            'global.cgi?action=getCurrentTime'
        )
        return ret.content.decode('utf-8')

    @current_time.setter
    def current_time(self, date):
        """
        According with API:
            The time format is "Y-M-D H-m-S". It is not be effected by Locales.
            TimeFormat in SetLocalesConfig

        Params:
            date = "Y-M-D H-m-S"
            Example: 2016-10-28 13:48:00

        Return: True
        """
        ret = self.command(
            'global.cgi?action=setCurrentTime&time={0}'.format(date)
        ).content.decode('utf-8')

        if "ok" not in ret.lower():
            print(ret)

    @property
    def dst(self):
        ret = filter(lambda row: row, self.get_config('Locales').replace('table.Locales.', '').split('\r\n'))
        config = dict(map(lambda row: row.split('='), ret))
        if not str2bool(config.get('DSTEnable')):
            return False
        return (
            datetime.datetime(int(config['DSTStart.Year']), int(config['DSTStart.Month']), int(config['DSTStart.Day']), 
            int(config['DSTStart.Hour']), int(config['DSTStart.Minute'])),
            datetime.datetime(int(config['DSTEnd.Year']), int(config['DSTEnd.Month']), int(config['DSTEnd.Day']), 
            int(config['DSTEnd.Hour']), int(config['DSTEnd.Minute']))
        )
    
    @dst.setter
    def dst(self, config):
        if config is None:
            return self.set_config(("Locales.DSTEnable", "false"))
        assert len(config) == 2 and isinstance(config[0], datetime.datetime) and isinstance(config[1], datetime.datetime)
        dst_config = {
            'Locales.DSTEnable': 'true',
            'Locales.DSTStart.Year': config[0].year,
            'Locales.DSTStart.Month': config[0].month,
            'Locales.DSTStart.Day': config[0].day,
            'Locales.DSTStart.Hour': config[0].hour,
            'Locales.DSTStart.Minute': config[0].minute,
            'Locales.DSTEnd.Year': config[1].year,
            'Locales.DSTEnd.Month': config[1].month,
            'Locales.DSTEnd.Day': config[1].day,
            'Locales.DSTEnd.Hour': config[1].hour,
            'Locales.DSTEnd.Minute': config[1].minute
        }
        ret = self.set_config(*dst_config.items())
        if "ok" not in ret.lower():
            print(ret)

    @property
    def general_config(self):
        return self.get_config('General')

    @property
    def version_http_api(self):
        ret = self.command(
            'IntervideoManager.cgi?action=getVersion&Name=CGI'
        )
        return ret.content.decode('utf-8')

    @property
    def software_information(self):
        ret = self.command(
            'magicBox.cgi?action=getSoftwareVersion'
        )
        swinfo = ret.content.decode('utf-8')
        if ',' in swinfo:
            version, build_date = swinfo.split(',')
        else:
            version, build_date = swinfo.split()
        return (version, build_date)

    @property
    def hardware_version(self):
        ret = self.command(
            'magicBox.cgi?action=getHardwareVersion'
        )
        return ret.content.decode('utf-8')

    @property
    def device_type(self):
        ret = self.command(
            'magicBox.cgi?action=getDeviceType'
        )
        return ret.content.decode('utf-8')

    @property
    def serial_number(self):
        ret = self.command(
            'magicBox.cgi?action=getSerialNo'
        )
        return ret.content.decode('utf-8').split('=')[-1]

    @property
    def machine_name(self):
        ret = self.command(
            'magicBox.cgi?action=getMachineName'
        )
        return ret.content.decode('utf-8')

    @property
    def system_information(self):
        ret = self.command(
            'magicBox.cgi?action=getSystemInfo'
        )
        return ret.content.decode('utf-8')

    @property
    def vendor_information(self):
        ret = self.command(
            'magicBox.cgi?action=getVendor'
        )
        return ret.content.decode('utf-8')

    @property
    def onvif_information(self):
        ret = self.command(
            'IntervideoManager.cgi?action=getVersion&Name=Onvif'
        )
        return ret.content.decode('utf-8')

    def config_backup(self, filename=None):
        ret = self.command(
            'Config.backup?action=All'
        )

        if not ret:
            return None

        if filename:
            with open(filename, "w+") as cfg:
                cfg.write(ret.content.decode('utf-8'))
            return None

        return ret.content.decode('utf-8')

    @property
    def device_class(self):
        """
        During the development, device IP2M-841B didn't
        responde for this call, adding it anyway.
        """
        ret = self.command(
            'magicBox.cgi?action=getDeviceClass'
        )
        return ret.content.decode('utf-8')

    def shutdown(self):
        """
        From the testings, shutdown acts like "reboot now"
        """
        ret = self.command(
            'magicBox.cgi?action=shutdown'
        )
        return ret.content.decode('utf-8')

    def reboot(self, delay=None):
        cmd = 'magicBox.cgi?action=reboot'

        if delay:
            cmd += "&delay={0}".format(delay)

        ret = self.command(cmd)
        return ret.content.decode('utf-8')

    def auto_reboot(self, date, everyday=False):
        # No reboot
        if date is None:
            return self.set_config(("AutoMaintain.AutoRebootDay", -1))
        assert isinstance(date, datetime.datetime)
        date_info = date.timetuple()
        config = {
            "AutoMaintain.AutoRebootDay": 7 if everyday else date.isoweekday(),
            "AutoMaintain.AutoRebootHour": date_info.tm_hour,
            "AutoMaintain.AutoRebootMinute": date_info.tm_min
        }
        return self.set_config(*config.items())
