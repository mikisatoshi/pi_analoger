# -*- coding: utf-8 -*-
import json
import numpy as np
import pandas as pd
import datetime,time
from sklearn.covariance import EmpiricalCovariance, MinCovDet
import bme280_

class PiAnaloger():
  def __init__(self, mode = 0, streamsize = 200):
    """
    [mode] is key to swith getting sample data or getting loger data.

    """
    self.mode = mode
    self.streamsize = streamsize
    self.streamlist = []
    self.streamcounter = 0

    try:
      self.init_get_data()
    except:
      pass

    try:
      self.init_get_sample_data()
    except:
      pass

    try:
      self.init_get_bme_data()
    except:
      pass

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
    
    # print(self.streamcounter)

    if self.streamcounter > self.streamsize:
      self.streamlist.pop(0)
      self.detect_error01()

  def __fin__(self):
    self.fin_detect_error01()


  def init_get_adc_data(self):
    pass

  def get_adc_data(self):
    pass


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

      print(maha[0])

      self.log01.append(np.hstack([self.streamlist[-1],maha[0]]))
      # maha = emp_cov.mahalanobis(np.array(self.streamlist)[:,2:5])
      # print(maha)

  def fin_detect_error01(self):
    dt_now = datetime.datetime.now()
    np.savetxt("./../storage/log01_" +str(datetime.date.today()) + '_' + str(dt_now.hour).zfill(2) +"-"+ str(dt_now.minute).zfill(2) +"-"+ str(dt_now.second).zfill(2) + ".csv", np.array(self.log01), delimiter=",")


def get_input_status():
  status = 1
  print("status is "  + str(status).zfill(2))
  return status



def main():

  PAL = PiAnaloger(mode = 2)

  while True:
    status = get_input_status()
    if status != 0 :
      break

  i = 0

  while True:
    PAL.stream()
    i +=1

    status = get_input_status()
    if status == 0 :
      break
    if i > 500:
      break

  PAL.__fin__()


if __name__ == '__main__':

  main()

