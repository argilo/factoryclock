#!/usr/bin/env python3

# Copyright 2019 Clayton Smith
#
# This program is free software: you can redistribute it and/or modify
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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import calendar
import sched
import threading
import time
import RPi.GPIO as GPIO

PULSE_ON_LEN = 0.150
PULSE_OFF_LEN = 0.250

POSITIVE = 4
NEGATIVE = 17

pulse_lock = threading.Lock()
stop_flag = False


def pulse(pin):
    pulse_lock.acquire()

    GPIO.output(pin, GPIO.HIGH)
    time.sleep(PULSE_ON_LEN)

    GPIO.output(pin, GPIO.LOW)
    time.sleep(PULSE_OFF_LEN)

    pulse_lock.release()


def next_minute():
    utc = time.gmtime()
    return calendar.timegm((utc.tm_year, utc.tm_mon, utc.tm_mday, utc.tm_hour, utc.tm_min+1, 0))


def button_loop(next_min):
    while next_min - time.time() > 2:
        while next_min - time.time() > 2 and GPIO.input(12) == GPIO.LOW:
            pulse(POSITIVE)

        if next_min - time.time() > 2:
            channel = GPIO.wait_for_edge(12, GPIO.FALLING, timeout=1000)
            if channel is not None:
                pulse(POSITIVE)


def minute_loop(sch):
    local = time.localtime()
    print(local.tm_hour, local.tm_min)
    pulse(POSITIVE)
    next_min = next_minute()
    sch.enterabs(next_min, 1, minute_loop, (sch,))
    button_loop(next_min)


GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.OUT)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    sch = sched.scheduler(time.time, time.sleep)
    next_min = next_minute()
    sch.enterabs(next_min, 1, minute_loop, (sch,))
    button_loop(next_min)
    sch.run()
except KeyboardInterrupt:
    pass

GPIO.output(4, GPIO.LOW)
GPIO.cleanup()
