#!/usr/bin/env python3

import time
import sys
import pigpio
import os

class IOManager(object):
  def __init__(self):
    os.system("sudo pigpiod")
    sys.stdout.write("Initing IO")
    sys.stdout.flush()
    for i in range(1, 5):
      time.sleep(1)
      sys.stdout.write(".%d" %(4-i,))
      sys.stdout.flush()

    self.io = pigpio.pi()
    self.io.set_mode(4, pigpio.INPUT)
    self.io.set_pull_up_down(4, pigpio.PUD_UP)
    self.io.set_mode(18, pigpio.OUTPUT)
    self.io.set_mode(26, pigpio.OUTPUT)
    self.setSound(0)

  def turnOnWetDisplays(self):
    self.io.write(4, 1)

  def readClicker(self):
    return not self.io.read(4)

  def setSound(self, setting):
    self.io.write(26, setting)
