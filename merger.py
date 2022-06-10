import sys
import os.path
import json
import numpy as np


if __name__ == "__main__":

    with open(sys.argv[1]) as file1, open(sys.argv[2]) as file2, open('voxels/merged.json', 'w') as out:
        injson1 = json.load(file1)
        injson2 = json.load(file2)
        LENX, LENY, LENZ = injson1['lenx'], injson1['leny'], injson1['lenz']
        _list1 = np.array(injson1['data'])
        _list2 = np.array(injson2['data'])

        _list3 = _list1 + _list2

        outjson = {'lenx': LENX, 'leny': LENY, 'lenz': LENZ, 'data': _list3.tolist()}

        json.dump(outjson, out)
