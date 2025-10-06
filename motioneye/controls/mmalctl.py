# Copyright (c) 2013 Calin Crisan
# This file is part of motionEye.
#
# motionEye is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from logging import debug
from subprocess import CalledProcessError

from motioneye import utils


def _list_mmal_devices():
    try:
        binary = utils.call_subprocess(['which', 'vcgencmd'])

    except CalledProcessError:  # not found
        debug('unable to detect MMAL camera: vcgencmd has not been found')
        return []

    try:
        support = utils.call_subprocess([binary, 'get_camera'])

    except CalledProcessError:  # not found
        debug('unable to detect MMAL camera: "vcgencmd get_camera" failed')
        return []

    if support.startswith('supported=1 detected=1'):
        debug('MMAL camera detected')
        return [('vc.ril.camera', 'VideoCore Camera')]

    return []


def _list_libcamera_devices():
    try:
        binary = utils.call_subprocess(['which', 'libcamera-hello'])

    except CalledProcessError:  # not found
        debug('unable to detect libcamera device: libcamera-hello not found')
        return []

    try:
        output = utils.call_subprocess([binary, '--list-cameras'])

    except CalledProcessError:  # command failed
        debug('unable to detect libcamera device: "libcamera-hello --list-cameras" failed')
        return []

    cameras = []
    for line in output.splitlines():
        line = line.strip()
        if not line or line.startswith('Available cameras:'):
            continue

        if ' : ' not in line:
            continue

        index, description = line.split(' : ', 1)
        if not index.isdigit():
            continue

        name = description.split('[')[0].strip() or 'Raspberry Pi Camera'
        path = 'vc.ril.camera' if not cameras else f'vc.ril.camera.{len(cameras)}'
        cameras.append((path, name))

    if not cameras:
        debug('no libcamera devices were discovered')

    return cameras


def list_devices():
    # currently MMAL support is designed specifically for the RPi;
    # therefore we can rely on the vcgencmd to report MMAL cameras.
    # On Raspberry Pi OS Bullseye and later, libcamera replaced the
    # legacy stack, so fall back to the libcamera tooling.

    debug('detecting Raspberry Pi camera')

    cameras = _list_mmal_devices()
    if cameras:
        return cameras

    return _list_libcamera_devices()
