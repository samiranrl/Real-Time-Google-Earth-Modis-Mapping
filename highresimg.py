

print "Loading modules... ",

import shapefile
from mpl_toolkits.basemap import Basemap
import pylab as p
from PIL import Image
import os, os.path, sys
import time
import tempfile, zipfile 
import urllib2, time
print "done!"

MODIS_SATNAME = "terra"

#http://rapidfire.sci.gsfc.nasa.gov/subsets
SUBSET_NAME = "FAS_India2"

# The pixel size
# "2km", "1km", "500m" or "250m"
RAPIDFIRE_RES = "250m"

# The active fire/hotspot for the lasts time
# "24h", "48h", "7d"
FIRE_LASTS = "7d"
# ==============================

# Year is in format "yyyy"
SUBSET_YEAR = str(time.localtime()[0])
# The day of the year
SUBSET_CODE = "041" #"%03d" % (time.localtime()[7])
TUPLE_MODIS = (SUBSET_NAME, SUBSET_YEAR, SUBSET_CODE, MODIS_SATNAME, RAPIDFIRE_RES)
# The download urls
URL_RAPIDFIRE_SUBSET = "http://rapidfire.sci.gsfc.nasa.gov/subsets/?subset=%s.%s%s.%s.%s.zip" % TUPLE_MODIS
URL_METADATA         = "http://rapidfire.sci.gsfc.nasa.gov/subsets/?subset=%s.%s%s.%s.%s.txt" % TUPLE_MODIS
URL_FIRE_SHAPES      = "http://firms.modaps.eosdis.nasa.gov/active_fire/shapes/zips/Global_%s.zip" % FIRE_LASTS
IMAGE_FILE           = '%s.%s%s.%s.%s.jpg' % TUPLE_MODIS

def parseTerm(metadata, term):
   """ Parses the txt or html metadata file """
   start = metadata.find(term + ":") + len(term)+1
   end   = metadata[start:].find("\n")
   val   = float(metadata[start:start+end])
   return val

def downloadString(url):
   """ Returns a string with the url contents """
   filein = urllib2.urlopen(url)
   data   = filein.read()
   filein.close()
   return data

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
   print "Crawling last near real-time true-color image from MODIS... ",
   download(URL_RAPIDFIRE_SUBSET, "data.zip")

   try:
      zipf    = zipfile.ZipFile('data.zip') 
   except zipfile.BadZipfile:
      print "\n\n\tError: BadZipfile, maybe the data is not yet ready on MODIS site !\n"
      sys.exit(-1)

   tempdir = tempfile.mkdtemp() 

   for name in zipf.namelist():
      data    = zipf.read(name)
      outfile = os.path.join(tempdir, name)
      f       = open(outfile, 'wb')
      f.write(data)
      f.close() 

   zipf.close()

   image_path  = os.path.join(tempdir, IMAGE_FILE)
   image_modis = Image.open(image_path)
   print "done !"

   print "Downloading MODIS image metadata... ",
   metadata = downloadString(URL_METADATA)
   ll_lon = parseTerm(metadata, "LL lon")
   ll_lat = parseTerm(metadata, "LL lat")
   ur_lon = parseTerm(metadata, "UR lon")
   ur_lat = parseTerm(metadata, "UR lat")
   print "done !"

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
   
   sr= r.shapeRecords()
   
   total=len(sr)
   
   xlist=[]
   ylist=[]
   confidence=[]
   
   for i in xrange(total):
      sr_test=sr[i]
      xlist.append( sr_test.shape.points[0][0]) #longitude
      ylist.append( sr_test.shape.points[0][1]) #latitude
      confidence.append( sr_test.record[8])
   
   print "done !"
   print "Rendering... ",
   m = Basemap(projection='cyl', llcrnrlat=ur_lat, urcrnrlat=ll_lat,\
               llcrnrlon=ll_lon, urcrnrlon=ur_lon, resolution='f')
   m.drawcoastlines()
   m.drawmapboundary(fill_color='aqua') 
   m.scatter(xlist, ylist, 20, c=confidence, cmap=p.cm.YlOrRd, marker='o', edgecolors='none', zorder=10)
   m.imshow(image_modis)
   
   
   p.title("The recent fire hotspots for last %s \n Pixel size: %s | Current Date: %s | Area Mapped: %s" % (FIRE_LASTS, RAPIDFIRE_RES,time.strftime("%d/%m/%Y"),SUBSET_NAME))
   p.show()

   os.remove("data.zip")
   
   
   

   

if __name__ == "__main__":
   run_main()
