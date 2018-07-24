#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from models.webpage import Webpage
from handlers.settings import suncolor_sequence

import numpy as np
import matplotlib.pyplot as plt
import csv
import pickle
import os

webpageCSV = Webpage.csvName
appealData = os.path.join(os.path.dirname('./..'), "data/appeal.pkl")
complexityData = os.path.join(os.path.dirname('./..'), "data/complexity.pkl")
appealGraph = os.path.join(os.path.dirname('./..'), "data/appeal.png")
complexityGraph = os.path.join(os.path.dirname('./..'), "data/complexity.png")

def pagePreference():
    webpageAData = {}
    webpageCData = {}
    with open(webpageCSV, "r+") as f:
        reader = csv.reader(f)
        for i in reader:
            if i[0] == 'id':
                continue
            if i[1] not in webpageAData:
                webpageAData[i[1]] = {}
                webpageCData[i[1]] = {}
            webpageAData[i[1]][i[3]] = i[-3]
            webpageCData[i[1]][i[3]] = i[-2]

        with open(appealData, "wb") as f:
            pickle.dump(webpageAData, f)
        with open(complexityData, "wb") as f:
            pickle.dump(webpageCData, f)
        #print(webpageAData)
    return webpageAData, webpageCData

def graphGenerate():
    with open(appealData, "r+b") as f:
        appeal = pickle.load(f)
    with open(complexityData, "rb") as f:
        complexity = pickle.load(f)
    userColor = {}
    n = 0
    plt.figure()
    plt.title("appeal")
    #print(appeal)
    for k, v in appeal.items():
        appealMean = []
        print(k)
        for u, r in v.items():
            print(u,r)
            #if u not in userColor:
                #userColor[u] = suncolor_sequence[n]
                #n += 1
            appealMean.append(int(r))
            print(appealMean)
            #plt.scatter(int(k), int(r), color=userColor[u])
        plt.scatter(int(k), np.mean(appealMean), color=suncolor_sequence[0])
    plt.savefig(appealGraph)
    complexityMean = []
    plt.figure()
    plt.title("complexity")
    for k, v in complexity.items():
        for u, r in v.items():
            complexityMean.append(int(r))
            #plt.scatter(int(k), int(r), color=userColor[u])
        plt.scatter(int(k), np.mean(complexityMean), color=suncolor_sequence[0])
    plt.savefig(complexityGraph) 
    return "end"
    
