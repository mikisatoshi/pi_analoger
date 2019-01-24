# -*- coding: utf-8 -*-
import json
import numpy as np
import datetime


class PiLoger():
  def __init__(self, ch = 8):
    self.ch = ch

  def get_dummy_data(self):
    dt_now = datetime.datetime.now()
    value = dt_now.hour * 60 + dt_now.minute
    values = ["-",str(datetime.datetime.now()), value, sin(value/100.0), cos(value/10.0), 9999 ,0 ,0, 0, 0, "test"]
    # for i in range(100):
    #   print(sin(i/100))
    return values


def main():

  PL = PiLoger()
  print(PL.get_dummy_data())



if __name__ == '__main__':
  try:
    main()
  except:
    pass
