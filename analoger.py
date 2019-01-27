# -*- coding: utf-8 -*-
import json,datetime,time,sys
import numpy as np
import pandas as pd
from sklearn.covariance import EmpiricalCovariance, MinCovDet
try:
  import ADS1x15
except:
  pass
try:
  import bme280_
except:
  pass
try:
  import RPi.GPIO as GPIO
except:
  pass 


class PiAnaloger():
  def __init__(self, mode = 0, streamsize = 100):
    """
    [mode] is key to swith getting sample data or getting loger data.

    """
    self.mode = int(mode)
    self.streamsize = streamsize
    self.streamlist = []
    self.streamcounter = 0
    self.sleeptime =0

    if self.mode == 0:
      self.init_get_sample_data()
      self.init_detect_error01()
    elif self.mode == 1:
      self.init_get_adc_data()
      self.init_detect_error01()
    elif self.mode == 2:
      self.init_get_bme_data()
      self.init_detect_error01()


  def stream(self):
    self.streamcounter += 1

    if self.mode == 0:
      data = self.get_sample_data()
    elif self.mode == 1:
      data = self.get_adc_data()
    elif self.mode == 2:
      data = self.get_bme_data()

    self.streamlist.append(data) 
    time.sleep(self.sleeptime) 
    
    # print(self.streamcounter)

    if self.streamcounter > self.streamsize:
      self.streamlist.pop(0)

      self.detect_error01()

  def __fin__(self):
    self.fin_detect_error01()


  def init_get_adc_data(self):
    self.adc = ADS1x15.ADS1115()
    self.counter_adc = 0
    self.GAIN = 1

  def get_adc_data(self):
    values = [0]*4
    for i in range(4):
        # Read the specified ADC channel using the previously set gain value.
        values[i] = self.adc.read_adc(i, gain=self.GAIN)
    return np.hstack([[time.clock(),self.streamcounter],np.array(values).flatten()])


  def init_get_sample_data(self, filepath = "sample.csv"):
    self.sample = pd.read_csv(filepath)
    self.counter_sample = 0
    self.rowsize = len(self.sample)


  def get_sample_data(self):
    if self.counter_sample >= self.rowsize:
      self.counter_sample = 0

    data = self.sample.query("index ==" + str(int(self.counter_sample)))
    self.counter_sample += 1

    return np.hstack([[time.clock(),self.streamcounter],np.array(data).flatten()])



  def init_get_bme_data(self):
    self.counter_bme = 0

  def get_bme_data(self):
    self.counter_bme += 1
    return np.hstack([[time.clock(),self.streamcounter],np.array(bme280_.getData()).flatten()])


  def init_detect_error01(self):
    self.timestep01 = 0.0001
    self.lateststeptime = 0
    self.counter01 = 0
    self.ch_num = 3
    self.log01 = []


  def detect_error01(self):
    if self.timestep01 < self.streamlist[-1][0] - self.lateststeptime:
      self.counter01 += 1
      self.lateststeptime = self.streamlist[-1][0]
      # print("self.counter01       " + str(self.counter01).zfill(6))
      # print("self.streamlist.size " + str(np.array(self.streamlist).shape))
      print(self.streamlist[-1])

      emp_cov = EmpiricalCovariance().fit(np.array(self.streamlist)[- int(self.streamsize / 2 ) : , 2 : 2+self.ch_num])
      # print(np.array(self.streamlist)[-1,2:5])
      maha = emp_cov.mahalanobis(np.array(self.streamlist)[-1,2:2+self.ch_num].reshape(1,-1))

      print("maha = " + str(maha[0]))

      self.log01.append(np.hstack([self.streamlist[-1],maha[0]]))
      # maha = emp_cov.mahalanobis(np.array(self.streamlist)[:,2:5])
      # print(maha)

  def fin_detect_error01(self):
    dt_now = datetime.datetime.now()
    np.savetxt("./../storage/log01_" +str(datetime.date.today()) + '_' + str(dt_now.hour).zfill(2) +"-"+ str(dt_now.minute).zfill(2) +"-"+ str(dt_now.second).zfill(2) + ".csv", np.array(self.log01), delimiter=",")



class Getstatus():
  def __init__(self):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(21, GPIO.IN)


  def get_input_status(self):
    if GPIO.input(21) == GPIO.HIGH:
      return 1
    else:
      return 0



def main():

  value = sys.argv
  print(value)
  try:
    runmode = int(value[1])
  except:
    runmode = 0

  PAL = PiAnaloger(mode = runmode)


##== wait triger sequence ===============

  if runmode == 0 :
    pass


  if 1 <= runmode and runmode <= 9: 
    GS = Getstatus()
    while True:
      if GS.get_input_status() != 0 :
        break

##== stream control ===============


  if runmode == 0 :
    i = 0
    while True:
      i += 1
      if 500 < i:
        break

      PAL.stream()


  if 1 <= runmode and runmode <= 9: 
    while True:
      if GS.get_input_status() == 0 :
        break

      PAL.stream()


  PAL.__fin__()


if __name__ == '__main__':

  main()

