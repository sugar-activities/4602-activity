import time

import pygame
#import pymedia.video.vcodec as vcodec

from auxiliary import *;
from constants import *;

#_ = lambda x: x

class Recorder(object):
	def __init__(self):
		self.frames= 0
		self._theaterScreen = pygame.display.get_surface().subsurface(geom['theater'])
		self.recording= False
		
	def snapshot(self):
		pygame.image.save(self._theaterScreen, 'ss.bmp')
	
	def add(self, changes):
		if self.recording == 'Shutter':
			addShutter(changes)
		elif self.recording == 'Video':
			addFrame(changes)
	
	def startShuttering(self, interval = 1):
		self.recording= 'Shutter'
		self.frames= 1
		self._storedFrames= {}
		self._previousFrame= None
		self._interval= interval
		self._delay = interval
		self._time = 0
	
	def addShutter(self, changes= None, force=False):
		self._delay += 1
		self._time += 1
		if (self._delay >= self._interval or force) and self._interval != -1:
			#if changes or not self._previousFrame:
			img= pygame.transform.scale(self._theaterScreen, (440, 495 / 2))
			location = directories['temp'] + 'ss%d.jpeg' % (self._time,)
			pygame.image.save(img, location)
			self._previousFrame= location
			self._delay = 0
			self._storedFrames[self._time]= self._previousFrame
			self.frames+= 1
	
	def clearShutter(self):
		for aFile in self._storedFrames.values():
			try:
				os.remove(aFile)
			except:
				print "Failed to delete file %s" % aFile
	
	def stopShuttering(self):
		self.recording= False
		return self._storedFrames
	
	def startRecording(self):
		self.recording= 'Video'
		self.frames= 1
		self._previousFrame= None
		
		#self._videoFile = open('ss/test.mpg', 'wb')
		#params= {
        #      'type': 0,
        #      'gop_size': 12,
        #      'frame_rate_base': 30, # 125,
        #      'max_b_frames': 0,
        #      'height': geom['theater'].height,
        #      'width': geom['theater'].width,
        #      'frame_rate': 90, # 2997,
        #      'deinterlace': 0,
        #      'bitrate': 2700000,
        #      'id': vcodec.getCodecID( 'mpeg1video' )
	#		  }
		#self._enc= vcodec.Encoder(params)
		
	def addFrame(self, changes= None):
		if changes or not self._previousFrame:
			img= self._theaterScreen
			#bmpFrame= vcodec.VFrame(vcodec.formats.PIX_FMT_RGB24, 
            #                   img.get_size(), 
                               # Covert image to 24bit RGB 
            #                  (pygame.image.tostring(img, "RGB"), None, None)      
            #                 )
			# Convert to YUV, then codec
			#convertedFrame= bmpFrame.convert(vcodec.formats.PIX_FMT_YUV420P)
			#self._previousFrame = self._enc.encode(bmpFrame).data
			self._previousFrame= "TEST"
		self._videoFile.write(self._previousFrame)
		self.frames+= 1
	
	def stopRecording(self):
		self._videoFile.close()
		self.recording= False
		print self.frames