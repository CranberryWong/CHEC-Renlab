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
        self.render("visualization/vmain.html", pagetitle = pagetitle, appeal = int(appeal) + 2, location = [], mark = '')

    def post(self):
        BaseHandler.initialize(self)
        pagetitle = self.get_argument("pagetitle")
        appeal = self.get_argument("appeal")
        print(appeal)
        windowWidth = 1900
        windowHeight = 900 + 123
        self.title = "Optimizing"
        location, mark = homogeneityModel(pagetitle, float(appeal))
        self.render("visualization/vmain.html", pagetitle = pagetitle, appeal = appeal, location = location, mark = mark)
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
    if appeal <= 5.04:
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
        while setNum not in homonumber:
            max_d += homostep
            clusters1 = fcluster(zm, max_d, criterion='distance')
            hist1 = collections.Counter(clusters1)
            histData1 = hist1.items()
            setNum1 = len(set(clusters1))
            # print(hist1)
            # print(max_d)
            # print(histData1)
            print(setNum1)
            if setNum1 in homonumber:
                break
        print(hist1)
        diff = hist1 - hist0
        print(diff)
        if len(diff) >= 3:
            diff = diff.most_common()[:3]
        else:
            diff = diff.most_common()

        for i in diff:
            result = np.where(clusters1 == i[0])
            print(result)
            yresult = np.array(list(map(lambda y: y//steps, result)))
            xresult = np.array(list(map(lambda x: x%steps, result)))
            print(yresult)

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