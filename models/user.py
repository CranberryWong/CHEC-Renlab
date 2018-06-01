#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime

import csv
import uuid
import os
# import pandas as pd
from mongoengine import Document, StringField, DateTimeField, EmailField, IntField, EmbeddedDocument, DictField, ListField

class User(object):
    
    csvName = os.path.join(os.path.dirname('./..'), "data/user.csv")

    def __init__(self, ever, email, name, gender, age, country, edu, design):
        self.id = str(uuid.uuid1())
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
'''
    def write2CSV(self):
        print(User.csvName)
        f = pd.read_csv(User.csvName)
        print(f)
        self.data = {"id": self.id, 
                     "ever": self.ever, 
                     "email": self.email,
                     "name": self.name, 
                     "gender": self.gender, 
                     "age": self.age, 
                     "country": self.country, 
                     "edu": self.edu, 
                     "design": self.design, 
                     "time": self.time, 
                     "rating": self.rating}
        print(self.data)
        f.append(self.data, ignore_index=True)
        print(f)
        f.to_csv(User.csvName)
        return self.name
    
    def revise2CSV(self, id, ratings):
        with open(User.csvName, "r") as f:
            reader = csv.reader(f)
            for i in reader:
                if i[0] == id:
                    i[-1] = ratings
        with open(User.csvName)
'''
        
