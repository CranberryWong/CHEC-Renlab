#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime

# import pandas as pd
import csv
import uuid
import os

class Webpage(object):
    
    csvName = os.path.join(os.path.dirname('./..'), "data/webpage.csv")
    
    def __init__(self, wid, title, uid):
        self.id = uuid.uuid1()
        self.wid = wid
        self.title = title
        self.uid = uid
        self.appeal = 0
        self.complexity = 0
        self.entropy = 0

    def __repr__(self):        
        return '<webpage: %s>' % (self.id)

    def write2CSV(self):

        with open(Webpage.csvName, "a+", newline='') as f:
            writer = csv.writer(f)
            self.data = [self.id, self.wid, self.title, self.uid, self.appeal, self.complexity, self.entropy]
            writer.writerow(self.data)
        return "Write webpage %s" % self.title