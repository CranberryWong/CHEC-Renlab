#!/usr/local/bin python3

from datetime import datetime

import csv
import uuid
import os

class User(object):
    
    csvName = os.path.join(os.path.dirname('./..'), "data/user.csv")

    def __init__(self, ever, email, name, gender, age, country, edu, design):
        self.id = uuid.uuid1()
        self.ever = ever
        self.email = email
        self.name = name
        self.gender = gender
        self.age = age
        self.country = country
        self.edu = edu
        self.design = design
        self.time = datetime.now()
        self.rating = {}

    def __repr__(self):
        return '<form: %s>' % self.name

    def write2CSV(self):
        with open(User.csvName, "a+", newline='') as f:
            writer = csv.writer(f)
            self.data = [self.id, self.ever, self.email, self.name, self.gender, self.age, self.country, self.edu, self.design, self.time, self.rating]
            writer.writerow(self.data)  
        return "Write user %s" % self.name