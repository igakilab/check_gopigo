# -*- coding: utf-8 -*-
import os
import time
import cv2
import numpy as np
import threading

import datetime
import glob

import sys

#####################################################################################################
class Judge:
  # constructor
  def __init__(self):
    #self.__trgDir = tdir
    self.__judgeInterval = 10	# judge inteval(sec)
    self.__jdgWt = 200			# width of judg area
    self.__jdgHt = 150		# Vertical width of judg area
    self.__area_ratio =  5		# Whether to make true when @ratio or more of the judg area becomes the search color
    self.__fileload = 200       # Max filenumber
    self.__updatelist = 0      # Number of file loaded
    self.sumPoints = 0        # sumpoints
    self.lastcolor = " "      # color take before
    
     
    self.gfiles = ["green"]
    self.bfiles = ["blue"]
    self.yfiles = ["yellow"]  
    self.deleteimg = 0 # number of delete image

    
    self.color = sys.argv
    if(self.color[1] == "-h"):
        print("argument yellow hue , green hue , blue hue")
        sys.exit()
        
        
    self.yellow = int(self.color[1])
    print("set yellow heu: " + str(self.yellow) + "\n")
    self.color = sys.argv
    self.green = int(self.color[2])
    print("set green heu: " + str(self.green) + "\n")
    self.color = sys.argv
    self.blue = int(self.color[3])
    print("set blue heu: " + str(self.blue) + "\n")
 
    
    cv2.namedWindow("green")
    cv2.namedWindow("blue")
    cv2.namedWindow("yellow")

    #calcpoint timer strtup
    self.__prvTime = time.time()
    t = threading.Thread(target = self.__calcPoints)
    t.daemon = True
    t.start()

  # private function
  def __colorDetector(self, hsv, hval, sval, vval):
    frmHt, frmWt, _ = hsv.shape

    maskH = cv2.inRange(hsv[:,:,0], hval[0], hval[1])
    maskS = cv2.inRange(hsv[:,:,1], sval[0], sval[1])
    maskV = cv2.inRange(hsv[:,:,2], vval[0], vval[1])

    # mask integration
    mask = maskH * maskS * maskV
    mask = mask.astype(np.uint8)*255

    kernel = np.ones((4,4), dtype="uint8")
    mask = cv2.erode(mask,kernel,iterations = 3)
    mask = cv2.dilate(mask,kernel,iterations = 3)

    # mask visualize
    img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    res2 = img * np.tile(mask[:,:,None], [1,1,3])
    res2 = res2.astype(np.uint8)

    # judge
    ltH = int(frmHt/2 - self.__jdgHt/2)
    ltW = int(frmWt/2 - self.__jdgWt/2)
    
    dtct = np.sum(mask[ltH:ltH+self.__jdgHt, ltW:ltW+self.__jdgWt] > 0)	#Number of pixels of the color judged as search color 
    jdge = (self.__jdgHt * self.__jdgWt)*(self.__area_ratio/100.0) <= dtct	#Comparison with the number of pixels (area) of the determination area 
    
    if dtct >= self.__jdgWt * self.__jdgHt * (self.__area_ratio/100.0) : # For judgment confirmation
      cv2.rectangle(res2, (ltW, ltH), (ltW+self.__jdgWt, ltH+self.__jdgHt), [0, 0, 255], 2)
      return jdge, res2
    
    return jdge, None

  # private function
  def __judgeGreen(self, hsv):
    jdg, res = self.__colorDetector(hsv, [self.green -5,self.green + 5],[80, 255],[50, 250])
    
    if self.lastcolor != "G":
    
      # For judgment confirmation
        if res is not None:
          cv2.imshow("green", res)

        if jdg :
          print("Get Green Point!")
        
        return jdg

  # private function
  def __judgeBlue(self, hsv):
    jdg, res = self.__colorDetector(hsv, [self.blue -5,self.blue + 5],[80, 255],[50, 250])

    if self.lastcolor != "B":
    #  For judgment confirmation
        if res is not None:
          cv2.imshow("blue", res)

        if jdg :
         print("Get Blue Point!")

        return jdg

  # private function
  def __judgeYellow(self, hsv):
    jdg, res = self.__colorDetector(hsv, [self.yellow -5,self.yellow + 5],[80, 255],[50, 250])

    if self.lastcolor != "Y":
    #  For judgment confirmation
        if res is not None:
         cv2.imshow("yellow", res)

        if jdg :
         print("Get Yellow Point!")

        return jdg

  # private function
  def __calcPoints(self):
    
    t = threading.Timer(self.__judgeInterval, self.__calcPoints)
    t.start()
    
    files = glob.glob( "*.jpg")
    files.sort(key=os.path.getmtime,reverse = True)

    #image file list length
    cmpfiles = len(files)
    if cmpfiles > self.__fileload:
       os.remove(files[self.__fileload])
       self.deleteimg += 1   


    if cmpfiles - self.__updatelist >= self.__fileload or self.__updatelist < self.__fileload:
        for i in range(cmpfiles - self.__updatelist):
          img = cv2.imread(files[i])
          hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
          self.__updatelist += 1
          if self.__judgeGreen(hsv) and self.lastcolor != "G":
            self.sumPoints = self.sumPoints + 1
            self.lastcolor = "G"
            self.gfiles.append(files[i])
          if self.__judgeBlue(hsv) and self.lastcolor != "B":
            self.sumPoints = self.sumPoints + 1
            self.lastcolor = "B"
            self.bfiles.append(files[i])
          if self.__judgeYellow(hsv) and self.lastcolor != "Y":
            self.sumPoints = self.sumPoints + 1
            self.lastcolor = "Y"
            self.yfiles.append(files[i])



    print("TOTAL POINT @" + str(int(time.time() - self.__prvTime)) + "sec is " + str(self.sumPoints) + " points / " + str(self.deleteimg + cmpfiles) + "totalshot\n")
    with open('/var/www/html/score.txt', 'w') as wfp:
        wfp.write("TOTAL POINT @" + str(int(time.time() - self.__prvTime)) + "sec is " + str(self.sumPoints) + " points / " + str(self.deleteimg + cmpfiles) + "totalshot\n")
        wfp.write(str(self.gfiles) + "\n")
        wfp.write(str(self.bfiles) + "\n")
        wfp.write(str(self.yfiles) + "\n")
        #wfp.write(str(self.deleteimg + cmpfiles) + "\n")


#####################################################################################################

def main():

  
  #calc poit class start up
  jdg = Judge()

  while 1:
    key = cv2.waitKey(1)
    if key == ord('q'):
      break

  #stop thread
  del jdg

if __name__ == '__main__':
    main()
