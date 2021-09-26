#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 15:08:15 2021

@author: siddhartha
"""

import urllib.request
import numpy as np
import json
import os, sys, platform
import getopt
import subprocess
import time
import datetime
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from gcmap import GCMapper
from PIL import Image ,ImageDraw
gcm = GCMapper()



def getLoc(IP):
    "Turn a string representing an IP address into a lat long pair"
    #Other geolocation services are available
    #url = "https://geolocation-db.com/json/"+IP
    url = "http://ip-api.com/json"+"/"+IP
    print("requesting "+url+"for JSON file")
    response = urllib.request.urlopen(url)
    encoding = response.info().get_content_charset('utf8')
    data = json.loads(response.read().decode(encoding))
    try:
        #lat= float(data["latitude"])
        #lon= float(data["longitude"])
        
        lat= float(data["lat"])
        lon= float(data["lon"])        
        country = str(data["countryCode"]) 
        city = str(data["city"])
        isp = str(data["isp"])
        
        if lat == 0.0 and lon == 0.0:
            return (None, None)
        return (lat,lon,country,city)
    except:
        return (None,None,None,None)

def printHelp():
    print ("./vis_route.py IPv4Address")
    print (" e.g. ./vis_route.py <Ipaddress> ")

try:
    opts, args = getopt.getopt(sys.argv,"h")
except getopt.GetoptError:
    printHelp()
    sys.exit()
for opt, arg in opts:
    if opt == '-h':
        printHelp()
        sys.exit()
if len(args) != 2:
    printHelp()
    sys.exit()
IP= args[1]

#Start traceroute command
proc = subprocess.Popen(["traceroute -m 25 -n "+IP], stdout=subprocess.PIPE, shell=True,universal_newlines=True)
#plot a pretty enough map
fig = plt.figure(figsize=(10, 6), edgecolor='w')
print("Downloading satellite imagery from NASA ...\n")
m = Basemap(projection='hammer', lon_0=0,resolution='l')
#m = Basemap(width=12000000,height=9000000,projection='lcc',
#resolution=None,lat_1=45.,lat_2=55,lat_0=50,lon_0=-107.)
m.bluemarble()
#m.drawcoastlines(color='r', linewidth=0.5)
#m.fillcontinents(color='green',lake_color='aqua')
# draw parallels and meridins.
m.drawparallels(np.arange(-90.,120.,30.))
m.drawmeridians(np.arange(0.,420.,60.))
#m.drawmapboundary(fill_color='aqua')
#m.shadedrelief(scale=0.05)
#Where we are coming from
lastLon= None
lastLat= None
count = 0
#Parse individual traceroute command lines
for line in proc.stdout:
    
    #print(line)#,end="")
    hopIP=line.split()[1]
    if hopIP in ("*" , "to"):
        continue
    (lat,lon,country,city)=getLoc(hopIP)
    if (lat is None):
        continue
    if lastLat is not None and (lastLat-lat + lastLon-lon) != 0.0:
        #print(lastLat,lastLon,lat,lon)
        #IP = hopIP
        count += 1
        x,y = m(lon,lat)     
        loc = city+","+country
        print("\n\nlocation: "+loc+"\n\n")
        m.scatter(x,y,s=100,marker='o',color='red',label=loc)
        loc = loc+"\n"+hopIP
        plt.text(x,y,loc,color="white",horizontalalignment='left',verticalalignment='bottom',fontsize=9,bbox=dict(facecolor='white',alpha=0.2))
        line, = m.drawgreatcircle(lastLon,lastLat,lon,lat,color='r',label=loc)
        plot_name = "imgseq/"+str(count)+".png"
        plt.savefig(plot_name,facecolor='black',dpi=100)
    lastLat = lat
    lastLon = lon

#plt.tight_layout()
if(count >= 1):
	dt = datetime.datetime.now()
	gif_name = IP+"_"+str(dt)+".gif"
	#plt.savefig(plot_name,facecolor='black',dpi=100)
	#plt.show()
	plt.close()

images = []
for i in range(1,count+1):
	path = "imgseq/"+str(i)+".png"
	img = Image.open(path)
	images.append(img)

images[0].save(gif_name,save_all=True,append_images=images[1:],optimize=False,duration=700,loop=20)
print("Done, please open the GIF created in the main folder ...")
print("deleting the image seqence genrated for making gif ...")
cleaning_process = subprocess.Popen("cd imgseq && rm *.png",shell=True)
print("OK !")
