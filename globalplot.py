import pyowm
from pygeocoder import Geocoder
from osgeo import ogr, osr, gdal
import subprocess
import os

print "Loading modules... ",
import simplekml

import shapefile
from mpl_toolkits.basemap import Basemap

import matplotlib.pyplot as plt
import pylab as p
from PIL import Image
import os, os.path, sys
import time
import tempfile, zipfile 
import urllib2, time
print "done!"

MODIS_SATNAME = "terra"



# The pixel size
# "2km", "1km", "500m" or "250m"
RAPIDFIRE_RES = "250m"

# The active fire/hotspot for the lasts time
# "24h", "48h", "7d"
FIRE_LASTS = "24h"
# ==============================

# Year is in format "yyyy"
SUBSET_YEAR = str(time.localtime()[0])
# The day of the year
SUBSET_CODE = "041" #"%03d" % (time.localtime()[7])


URL_FIRE_SHAPES      = "http://firms.modaps.eosdis.nasa.gov/active_fire/shapes/zips/Global_%s.zip" % FIRE_LASTS




def download(url, fout):
   """ Saves the url file to fout filename """
   filein  = urllib2.urlopen(url)
   fileout = open(fout, "wb")

   while True:
      bytes = filein.read(1024)
      fileout.write(bytes)

      if bytes == "": break

   filein.close()
   fileout.close()

def run_main():
   """ Main """
   

   tempdir = tempfile.mkdtemp() 

   


   print "Downloading shape files from MODIS rapid fire... ",
   download(URL_FIRE_SHAPES, "shapes.zip")
   zipf = zipfile.ZipFile('shapes.zip') 

   for name in zipf.namelist():
      data    = zipf.read(name)
      outfile = os.path.join(tempdir, name)
      f       = open(outfile, 'wb')
      f.write(data)
      f.close() 
   zipf.close()
   print "done !"

   print "Parsing shapefile... ",

   shape_path = os.path.join(tempdir, 'Global_%s' % FIRE_LASTS)
   r     = shapefile.Reader(shape_path)
  # print r.fields
   print
   sr= r.shapeRecords()
   print
   total=len(sr)
   print
   xlist=[]
   ylist=[]
   confidence=[]
   
   for i in xrange(total):
      
      sr_test=sr[i]
      
      xlist.append( sr_test.shape.points[0][0]) #longitude
      ylist.append( sr_test.shape.points[0][1]) #latitude
      confidence.append( sr_test.record[8])
         
      
   print "list size: ",len(xlist)
   

   print "done "

   print "Rendering... ",
   
   m = Basemap(projection='cyl')
   
   
   
   m.bluemarble()
   
   
   m.scatter(xlist, ylist, 20, c=confidence, cmap=p.cm.YlOrRd, marker='o', edgecolors='none', zorder=10)
   
   
   p.title("The recent fire hotspots for last %s \n Pixel size: %s | Current Date: %s" % (FIRE_LASTS, RAPIDFIRE_RES,time.strftime("%d/%m/%Y")))
   p.show()
   
   
   
   print "done !"

   
   os.remove("shapes.zip")
   
   

   

if __name__ == "__main__":
   run_main()
