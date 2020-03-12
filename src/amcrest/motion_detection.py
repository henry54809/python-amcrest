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
from amcrest.utils import str2bool


class MotionDetection(object):

    @property
    def motion_detection_raw(self):
        return self.get_config("MotionDetect")

    @property
    def motion_detection(self):
        return str2bool(self.get_config("MotionDetect[0].Enable").split('=')[-1].strip())

    @property
    def motion_recording(self):
        return str2bool(self.get_config("MotionDetect[0].EventHandler.RecordEnable").split('=')[-1].strip())

    @property
    def motion_snapshot(self):
        return str2bool(self.get_config("MotionDetect[0].EventHandler.SnapshotEnabled").split('=')[-1].strip())

    @motion_detection.setter
    def motion_detection(self, opt):
        ret = self.set_config(('MotionDetect[0].Enable=', 'true' if opt else 'false'))
        if "ok" not in ret.lower():
            print(ret)

    @motion_recording.setter
    def motion_recording(self, opt):
        key = 'MotionDetect[0].EventHandler.RecordEnable'
        ret = self.set_config((key, 'true' if opt else 'false'))
        if "ok" not in ret.lower():
            print(ret)

    @motion_snapshot.setter
    def motion_snapshot(self, opt):
        key = 'MotionDetect[0].EventHandler.SnapshotEnabled'
        ret = self.set_config((key, 'true' if opt else 'false'))
        if "ok" not in ret.lower():
            print(ret)
