import json
import sys
import numpy as np
import pandas as pd

from kite import kite
from kite.xrg import xrg
from kitevector import vector

if __name__ == "__main__":

	path = 'tmp/vector/vector*.csv'
	filespec = kite.CsvFileSpec()
	hosts = ['localhost:7878']

	vs = vector.KiteVector(hosts, path, filespec)

	res = vs.nbest([4,6,8], -70, 3)
	print(res)


