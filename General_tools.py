from NuRadioReco.modules.io import NuRadioRecoio
import datetime
import os

def get_input(input):
    input_dir=[]
    for i in os.listdir(input):
        if i.endswith('.nur'):
            input_dir.append(os.path.join(input,i))
    return input_dir

def get_readARIANNAData(input_path):
    return NuRadioRecoio.NuRadioRecoio(get_input(input_path))

def output_dir(output_path,directory):
    pass

def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]  # Choose the pivot
    left = [x for x in arr if x < pivot]  # Elements less than pivot
    middle = [x for x in arr if x == pivot]  # Elements equal to pivot
    right = [x for x in arr if x > pivot]  # Elements greater than pivot
    return quicksort(left) + middle + quicksort(right)
