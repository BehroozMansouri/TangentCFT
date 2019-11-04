import csv
import sys
import os

__author__ = 'FWTompa'

"""
Control manages control files for indexing and searching in Tangent
"""

class Control:
    def __init__(self,cntl=None):
        self.parms = {}
        csv.field_size_limit(999999999) # NTCIR cntl file has 17853644 characters (limit is now approx 50 times bigger) 
        if not cntl:
            cntl = "tangent.cntl"  # use tangent.cntl as the default control file name
        if not os.path.exists(cntl):
            raise Exception(cntl+" does not exist.")
        self.store("cntl",cntl)
        with open(cntl, mode='r', encoding='utf-8', newline='') as file:
            reader = csv.reader(file, delimiter='\t', lineterminator='\n', quoting=csv.QUOTE_NONE, escapechar="\\")
            for (parm,value) in reader:
                self.store(parm,value) # set all the control parameters

    def read(self,parm,num=False,default=None):
        val = self.parms.get(parm.strip(),default)
        if val and num:
            try:
                val = int(val)
            except ValueError:
                print("Parameter %s not numeric; value given is %s; using %s" % (parm,val,default))
                val = default
        return (val if val else default)

    def store(self,parm,val):
        self.parms[parm.strip()] = val.strip()

    def dump(self):
        cntl = self.parms["cntl"]
        with open(cntl, mode='w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file, delimiter='\t', lineterminator='\n', quoting=csv.QUOTE_NONE, escapechar="\\")
            for pair in self.parms.items():
                writer.writerow(pair)

