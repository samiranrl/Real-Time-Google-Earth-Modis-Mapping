#!/usr/bin/env python
# coding: utf-8

import os
import Image
import random
import urllib
import cStringIO
import cairo
#from geofunctions import *


class TileServer(object):
    def __init__(self):
        self.imdict = {}
        self.surfdict = {}
        self.layers = 'ROADMAP'
        self.path = './'
        self.urltemplate = 'http://ecn.t{4}.tiles.virtualearth.net/tiles/{3}{5}?g=0'
        self.layerdict = {'SATELLITE': 'a', 'HYBRID': 'h', 'ROADMAP': 'r'}

    def tiletoquadkey(self, xi, yi, z):
        quadKey = ''
        for i in range(z, 0, -1):
            digit = 0
            mask = 1 << (i - 1)
            if(xi & mask) != 0:
                digit += 1
            if(yi & mask) != 0:
                digit += 2
            quadKey += str(digit)
        return quadKey

    def loadimage(self, fullname, tilekey):
        im = Image.open(fullname)
        self.imdict[tilekey] = im
        return self.imdict[tilekey]

    def tile_as_image(self, xi, yi, zoom):
        tilekey = (xi, yi, zoom)
        result = None
        try:
            result = self.imdict[tilekey]
        except:
            filename = '{}_{}_{}_{}.jpg'.format(zoom, xi, yi, self.layerdict[self.layers])
            fullname = self.path + filename
            try:
                result = self.loadimage(fullname, tilekey)
            except:
                server = random.choice(range(1,4))
                quadkey = self.tiletoquadkey(*tilekey)
                print quadkey
                url = self.urltemplate.format(xi, yi, zoom, self.layerdict[self.layers], server, quadkey)
                print "Downloading tile %s to local cache." % filename
                urllib.urlretrieve(url, fullname)
                result = self.loadimage(fullname, tilekey)
        return result

if __name__ == "__main__":
    ts = TileServer()
    im = ts.tile_as_image(5, 9, 4)
    im.show()
