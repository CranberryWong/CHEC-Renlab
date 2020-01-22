#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime

# import pandas as pd
import csv
import uuid
import os
import time

class Webpage(object):
    
    def __init__(self, wid, ext, title, name):
        self.id = uuid.uuid1()
        self.wid = wid
        self.ext = ext
        self.timestamp = int(time.time() * 1000)
        self.title = title
        #self.uid = uid
        self.appeal = 0
        #self.complexity = 0
        #self.entropy = 0
        self.csvName = os.path.join(os.path.dirname('./..'), "data/"+str(ext)+"/%s.csv") % name

    def __repr__(self):        
        return '<webpage: %s>' % (self.id)

    def write2CSV(self):

        with open(self.csvName, "a+", newline='') as f:
            writer = csv.writer(f)
            self.data = [self.id, self.wid, self.timestamp, self.title, self.appeal]
            writer.writerow(self.data)
        return "Write webpage %s" % self.title