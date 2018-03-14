#!/usr/local/bin python3

from datetime import datetime

import csv
import uuid
import os

class Webpage(object):
    
    csvName = os.path.join(os.path.dirname('./..'), "data/webpage.csv")
    
    def __init__(self, title):
        self.id = uuid.uuid1()
        self.title = title
        self.appeal = []
        self.complexity = []
        self.entropy = 0

    def __repr__(self):        
        return '<webpage: %s>' % (self.id)

    def write2CSV(self):
        with open(Webpage.csvName, "a+", newline='') as f:
            writer = csv.writer(f)
            self.data = [self.id, self.title, self.appeal, self.complexity, self.entropy]
            writer.writerow(self.data)
        return "Write webpage %s" % self.title