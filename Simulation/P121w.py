import numpy as np
from icecream import ic
import os
import re
data='/Users/david/Downloads/p121_lab1_data/'
files=[]
for file in os.listdir(data):
  if file.endswith('.txt'):
    files.append(os.path.join(data,file))
files=sorted(files)

weights = {
    '200':3,
    '300':2,
    '400':1.5,
    '500':1,
    '750':0.75,
    '1000':0.5
}

def extract_number(text):
  electron_matches = re.findall(r"Electron \d+ Pt ([\d.-]+) Eta ([\d.-]+) Phi ([\d.-]+) Charge ([\d.-]+)", text)
  for match in electron_matches:
    # data = {
    #     'pt': float(match[0]),
    #     'eta': float(match[1]),
    #     'phi': float(match[2]),
    #     'charge': int(match[3])
    # }
    data = [float(match[0]),
            float(match[1]),
            float(match[2]),
            int(match[3])]
    return data

def read_file(file,weight,energy):
  data_list = []
  with open(file, 'r') as f:
    content = f.read()
    events = content.split('NumElectrons:')[1:]
    events = ['NumElectrons:' + e for e in events]
    for event in events:
      lines = event.split('\n')
      if len(lines)!=4:
        if len(lines)>4:
          ic(lines)
          exit()
        continue
      p1 = extract_number(lines[1])
      p2 = extract_number(lines[2])
      if p1[-1]+p2[-1]!=0:
        continue
      p1.append(weight)
      p2.append(weight)
      p1.append(energy)
      p2.append(energy)
      p1 = np.array(p1)
      p2 = np.array(p2)

    # p1 = {
    #     'pt': float(match[0]),
    #     'eta': float(match[1]),
    #     'phi': float(match[2]),
    #     'charge': int(match[3]),
    #     'weight': 0.50,
    #     'energy': 1000 GeV
    # }
      data_list.append([p1,p2])
  return data_list
well_data = []
for file_path in files:
    # re.search looks for 'mll' or 'mzp' followed by one or more digits (\d+)
    match = re.search(r'(?:mll|mzp)(\d+)', file_path)
    if match:
        mass_value = int(match.group(1))
        try:
          weight = weights[str(mass_value)]
        except KeyError:
          weight = 2
        data_reader = read_file(file_path,weight,mass_value)
        well_data.append(data_reader)
