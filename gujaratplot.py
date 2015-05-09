import pyowm
from pygeocoder import Geocoder
from osgeo import ogr, osr, gdal
import subprocess
import os
import pickle
import time
from math import radians, cos, sin, asin, sqrt

print "Loading modules... ",
time.sleep(1)
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



def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 

    # 6367 km is the radius of the Earth
    km = 6367 * c
    return km 




MODIS_SATNAME = "terra"

List=[]


List=[["Gujrat Fire & Safety Agency", 22.299774, 73.202672, "0265 242 8519"],
["Vadodara Central Fire Station",22.300031, 73.201142,"0265 241 3754"],
["Mavdi Road Fire Station",22.271225, 70.789847,"093277 07487"],
["JMC Fire and emergency services",22.467840, 70.067657,"Not Available"],
      ["Diu Fire Station", 20.713893, 70.977257,"Not Available"],
      ["Bhuj Fire Station", 23.239067, 69.681531,"Not Available" ],
      ["Bhavnagar City Fire Brigade",21.770390, 72.130497,"0278 242 4814"]]


def closest(latit,longit):
   c={}
   for LD in List:
      dist = haversine(longit,latit,LD[2], LD[1])
      c[dist]=LD[0]
  
   return c[min(c.keys())]




 
pickle.dump( List, open( "save.p", "wb" ) )
Fire_Stations = pickle.load( open( "save.p", "rb" ) )

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
   time.sleep(1)
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
   time.sleep(1)

   shape_path = os.path.join(tempdir, 'Global_%s' % FIRE_LASTS)
   r     = shapefile.Reader(shape_path)
  # print r.fields
   
   sr= r.shapeRecords()
   
   total=len(sr)
   
   xlist=[]
   ylist=[]
   confidence=[]
   Temperature=[]
   Precipitation=[]
   Wind=[]
   
   Address=[]
   Hotlist=[]
   Closest=[]
   print "done !"
   print "Generating Meta Information... ",
   time.sleep(1)
   owm = pyowm.OWM('68869ecb5eef05b27254ed40fd773d62')
   for i in xrange(total):
      
      sr_test=sr[i]
      longit=float(sr_test.shape.points[0][0])
      latit=float(sr_test.shape.points[0][1])
      
      if (longit>68 and longit<74):
          if (latit>20 and latit<25):
              xlist.append( sr_test.shape.points[0][0]) #longitude
              ylist.append( sr_test.shape.points[0][1]) #latitude
              confidence.append( sr_test.record[8])
              temp=Geocoder.reverse_geocode(latit, longit)
              temp= str(temp[0]).split(',')
              temp=temp[0]+","+temp[1]
              Address.append(temp)
              
              observation= owm.weather_at_coords(latit, longit)
              
              w = observation.get_weather()
              Wind.append(str(w.get_wind()['speed']) )
              
              Precipitation.append(str(w.get_humidity()))
              Temperature.append(str(w.get_temperature('celsius')['temp_min'])+" C")
              Hotlist.append("No")

              Closest.append(closest(latit,longit))

              if (int(sr_test.record[8])>50):
                   if (float(w.get_wind()['speed'])>1.3):
                       if(float(w.get_temperature('celsius')['temp'])>=20):
                           if(float(w.get_humidity())<55):
                               Hotlist.pop()
                               Hotlist.append("Yes")
                               
                                   
              
               
              
         
   print "done !"
   
   print "Generating KML File... ",
   time.sleep(1)
   




  

   kml = simplekml.Kml(open=1)


   single_point = kml.newpoint(name="Gujrat", coords=[(71,23)])
   
   for DP in (Fire_Stations):
      
      
      pnt = kml.newpoint()
      pnt.name =DP[0]
      pnt.description=DP[3]
      pnt.style.iconstyle.icon.href="http://maps.google.com/mapfiles/kml/shapes/phone.png"
      pnt.coords = [(DP[2], DP[1])]
      
   
   
   for i in xrange(len(xlist)):
      pnt = kml.newpoint()
      if Hotlist[i]=="Yes":
          pnt.style.iconstyle.icon.href="firehot.png"
      else:
          pnt.style.iconstyle.icon.href="firenormal.png"
      
      pnt.name =Address[i]

      Description="High Danger Fire: "+Hotlist[i]
      Description=Description+"\nClosest Fire Station: "+str(Closest[i])
      Description=Description+"\nConfidence: "+str(confidence[i])
      Description=Description+"\nTemperature: "+Temperature[i]+"\nHumidity: "+ Precipitation[i]
      Description=Description+"\n Wind Speed: "+Wind[i]+" m/s "
      pnt.description = Description
      
      pnt.coords = [(xlist[i], ylist[i])]
      
   


   kml.save("GujratFires.kml")


   print "done !"
   print "Rendering... ",
   time.sleep(2)

   os.startfile('GujratFires.kml')
    

   """
   
   m = Basemap(projection='cyl')
   
   
   
   m.bluemarble()
   
   
   m.scatter(xlist, ylist, 20, c=confidence, cmap=p.cm.YlOrRd, marker='o', edgecolors='none', zorder=10)
   
   
   p.title("The recent fire hotspots for last %s \n Pixel size: %s | Current Date: %s" % (FIRE_LASTS, RAPIDFIRE_RES,time.strftime("%d/%m/%Y")))
   p.show()
   
   """  
   
   

   
   os.remove("shapes.zip")
   
   
   

   

if __name__ == "__main__":
   run_main()
