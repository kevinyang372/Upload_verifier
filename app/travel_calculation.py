import numpy as np
import pandas as pd
import json
import requests
from math import sin, cos, sqrt, atan2, radians
from sklearn.ensemble import IsolationForest
from sklearn import svm

def request_file(distance, latitude, longitude):
  api_base = 'https://api.safecast.org/measurements.json?'
  api_request = 'distance='+str(distance)+'&latitude='+str(latitude)+'&longitude='+str(longitude)
  api_url = api_base + api_request
  response = requests.get(api_url)

  if response.status_code == 200:
      strings = json.loads(response.content.decode('utf-8'))
      k = []
      for i in strings:
          #k.append([i['latitude'],i['longitude'],i['value']])
          k.append(i['value'])
      return k
  else:
      return None

def prediction_IsolationForest(points, neighbors):
  clf = IsolationForest()
  clf.fit(neighbors)
  return clf.decision_function(points)

def local_mean(value, neighbors):
  k = float(np.mean(neighbors)) / value
  return k

def predict(travel_data):

  travel = []
  locx = []
  locy = []
  value = []
  user = travel_data[0]["User"]
  drive = travel_data[0]["Drive"]

  for i in range(len(travel_data)):
      travel.append([float(travel_data[i]["Latitude"]),float(travel_data[i]["Longitude"]),float(travel_data[i]["Value"])])
      locx.append(float(travel_data[i]["Latitude"]))
      locy.append(float(travel_data[i]["Longitude"]))
      value.append(float(travel_data[i]["Value"]))

  hist_eva = []
  iterations = int(len(travel)/10)
  decision = []

  one_travel_eva = test_point_in_one_travel(locx,locy,value)

  for i in range(len(travel)):
      radius = 100
      neighbors = request_file(radius,travel[i][0],travel[i][1])
      if neighbors == [] or neighbors == None:
          continue
      #hist_eva.append(self.prediction_IsolationForest([travel[i]],neighbors))
      ratio = local_mean(value[i],neighbors)
      if ratio > 0.5 and ratio < 2:
        decision.append(1)
      else:
        decision.append(0)
      hist_eva.append(ratio)

  highly_fluctuated_point = []
  for i in one_travel_eva:
    highly_fluctuated_point.append({"Latitude": travel[i][0], "Longitude": travel[i][1], "Value": travel[i][2]})


  return {"user": user, "drive": drive, "latitude": locx, "longitude": locy, "result": decision, "fluctuation": highly_fluctuated_point, "ratio": hist_eva, "value": value}

def test_point_in_one_travel(locx, locy, value):

  if len(locx) == 1:
    return []

  suspicious_points = []
  for i in range(len(locx) - 1):
      if value[i] / value[i+1] > 2 or value[i] / value[i+1] < 0.5:
          suspicious_points.append(i)
          
  return suspicious_points