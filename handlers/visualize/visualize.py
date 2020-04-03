#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tornado.web
import tornado.locale
import random
import time
import os
import re
import csv
import pickle
import numpy as np
import collections
import json
from scipy.cluster.hierarchy import fcluster
# from matplotlib import pyplot as plt
from PIL import Image, ImageDraw
# from scipy.misc import imresize
from selenium import webdriver
from handlers.base import BaseHandler
from handlers.aesthetics.settings import WebpageList
from models.user import User
from models.webpage import Webpage
from functools import reduce
from handlers.exception import ErrorHandler
from handlers.visualize.settings import WebpageList

prefix = '/Pictures/buffer/'

webpageDict={

    # high
    'microsoft.com':6.73,
    'pantone.com':6.23,

    #middle
    'skima.jp':5.1,
    'designmodo.com':4.43,
    'freebiesbug.com':5.03,

    # lower
    'infoq.com':3.66,
    'olderadults.mobi':3.56,
    'math.com':2.96,
    'pxtoem.com':3.1,
    'yuchrszk.blogspot.com':3.93
}


def getReturnedRanking():
    returned_ranking = {"frequency": [], "appeal": [], "homo": [], "entropy": []}

    csv_path = os.path.join(os.path.dirname('./..'), "static/sample/")
    with open(os.path.join(csv_path, 'ttt.csv'), "r+") as f:
        reader = csv.reader(f)
        sample_count = 0; sample_total = 147
        j = 2; chart_frequency = 0; chart_appeal = 0; chart_homo = 0; chart_entropy = 0
        
        for i in reader:
            if i[0] != "title":
                sample_count += 1
                
                if float(i[3]) < j:
                    chart_frequency += 1
                    chart_appeal += float(i[3])
                    chart_homo += float(i[-2])
                    chart_entropy += float(i[-1])
                else:
                    returned_ranking["frequency"].append(chart_frequency)
                    returned_ranking["appeal"].append(chart_appeal/chart_frequency)
                    returned_ranking["homo"].append(chart_homo/chart_frequency)
                    returned_ranking["entropy"].append(chart_entropy/chart_frequency)
                    chart_frequency = 0; chart_appeal = 0; chart_homo = 0; chart_entropy = 0
                    chart_frequency += 1
                    chart_appeal += float(i[3])
                    chart_homo += float(i[-2])
                    chart_entropy += float(i[-1])
                    j += 1
                    if sample_count == sample_total:
                        returned_ranking["frequency"].append(chart_frequency)
                        returned_ranking["appeal"].append(chart_appeal/chart_frequency)
                        returned_ranking["homo"].append(chart_homo/chart_frequency)
                        returned_ranking["entropy"].append(chart_entropy/chart_frequency)
    return returned_ranking

global returned_ranking

returned_ranking = getReturnedRanking()

class HomeHandler(BaseHandler):
    def get(self):
        BaseHandler.initialize(self)
        self.title = 'Optimizing Your Design'
        self.render("visualization/vhome.html")

class MainHandler(BaseHandler):
    def get(self):
        pagetitle = self.get_argument("pagetitle")
        BaseHandler.initialize(self)
        appeal = webpageDict[pagetitle]
        self.title = 'Optimizing'
        self.render("visualization/vmain.html", pagetitle = pagetitle, appeal = int(appeal) + 2, location = [], mark = '', originappeal = appeal, returned_ranking = returned_ranking)

    def post(self):
        BaseHandler.initialize(self)
        pagetitle = self.get_argument("pagetitle")
        appeal = self.get_argument("appeal")

        originappeal = webpageDict[pagetitle]
        
        print(appeal)
        windowWidth = 1900
        windowHeight = 900 + 123
        self.title = "Optimizing"
        location, mark = homogeneityModel(pagetitle, float(appeal))
        self.render("visualization/vmain.html", pagetitle = pagetitle, appeal = appeal, location = location, mark = mark, originappeal = originappeal, returned_ranking = returned_ranking)
        # driver = webdriver.Chrome()
        # driver.set_window_size(windowWidth, windowHeight)
        # driver.get(url)
        # driver.save_screenshot(os.getenv("HOME") + prefix + 'webpages/' + domainNAME + '.png')
        # driver.close()

def reject_outliers(data, m=2.):
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / (mdev if mdev else 1.)
    return data[s < m]

def homogeneityModel(title, appeal):
    steps = 80
    max_d = 4.88
    op_location = []
    resolution = (1680/steps, 800/steps)

    # Homogeneity-number-based
    if appeal <= (5.04 + 1):
        homomiddle = int(1.68433776 * appeal + 2.368360062544003) + 1
        homonumber = [homomiddle - 1, homomiddle, homomiddle + 1]
        homostep = -0.02
        mark = 'i'
    else:
        homomiddle = int(-1.37811713 * appeal + 18.35588028408704) + 1
        homonumber = [homomiddle - 1, homomiddle, homomiddle + 1]
        homostep = 0.02
        mark = 'd'
    print(homonumber)
    
    z_path = os.path.join(os.path.dirname('./..'), "static/sample/")
    with open(os.path.join(z_path, 'z.pkl'), 'rb') as f:
        z_test = pickle.load(f)
        zm = z_test[title]

        # Current
        clusters0 = fcluster(zm, max_d, criterion='distance')
        hist0 = collections.Counter(clusters0)
        histData0 = hist0.items()
        setNum = len(set(clusters0))
        print("setNum " + str(setNum))

        hist1 = collections.Counter([])

        if setNum in homonumber:
            setNum1 = setNum
            while setNum1 == setNum:
                max_d += homostep
                clusters1 = fcluster(zm, max_d, criterion='distance')
                hist1 = collections.Counter(clusters1)
                setNum1 = len(set(clusters1))
                print("setNum1:" + str(setNum1))

        while setNum not in homonumber:
            max_d += homostep
            clusters1 = fcluster(zm, max_d, criterion='distance')
            hist1 = collections.Counter(clusters1)
            histData1 = hist1.items()
            setNum1 = len(set(clusters1))
            # print(hist1)
            # print(max_d)
            # print(histData1)
            print("setNum1:" + str(setNum1))
            if setNum1 in homonumber:
                break
        

        print("hist1:" + str(hist1))
        diff = hist1 - hist0
        print("diff:" + str(diff))
        if len(diff) >= 3:
            diff = diff.most_common()[:3]
        else:
            diff = diff.most_common()

        for i in diff:
            result = np.where(clusters1 == i[0])
            print("result:" + str(result))
            yresult = np.array(list(map(lambda y: y//steps, result)))
            xresult = np.array(list(map(lambda x: x%steps, result)))
            print("yresult:" + str(yresult))

            yresult = reject_outliers(yresult)
            xresult = reject_outliers(xresult)

            originx = ((np.max(xresult) + np.min(xresult))/2) * resolution[0]
            originy = (np.max(yresult) + np.min(yresult))/2 * resolution[1]
            radius = (((np.max(yresult) - np.min(yresult)))*resolution[1]/2 + ((np.max(xresult) - np.min(xresult)))*resolution[0]/2)/2

            op_location.append([originx, originy, radius])
        print(op_location)
    return op_location, mark

        # infile = os.path.join(os.path.dirname('./../..'), "static/sample/") + title +'.png'
        # im = Image.open(infile)
        # im = array(im.convert('HSV'))

        # codeim0 = clusters.reshape(steps, steps)
        # codeim0 = imresize(codeim0, im0.shape[:2], 'nearest')

        # imshow(codeim0)
        # show()