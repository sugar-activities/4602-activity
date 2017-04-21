import random;
import itertools;

import pygame
import spyral

from broadway import hacks
from constants import *
import auxiliary;

#_ = lambda x: x

class Backdrop(spyral.sprite.Sprite):
	"""
	A *Backdrop* is the large Sprite that the *Actor*s act in front of. It
	represents the current scene. Besides an image, it also has a collection
	of template Plot Twists associated with it.
	
	In the future, *Backdrop*s might have a foreground in front of the *Actor*s.
	"""
	def __init__(self, name='*', external= False, asString= False):
		"""
		Initializes a backdrop
		
		| *name* the name of the backdrop being created.
		"""
		spyral.sprite.Sprite.__init__(self)
		self.directory= name;
		self.external = external
		if asString:
			self.image = asString
			self.twists= [[] for x in xrange(limits['actors'])]
		elif external: 
			self.loadExternalImage()
			self.twists= [[] for x in xrange(limits['actors'])]
		else:
			self.loadImage();
			self.loadTwists();
		self.layer= 'upstage';
	
	def loadTwists(self):
		"""
		Loads the twists associated with the Backdrop
		"""
		twistsPath= os.path.join('games/broadway/backdrops', 'twists.%s.txt' % hacks['language']);
		twistsFile= open(twistsPath, 'r');
		self.twists= [[] for x in xrange(limits['actors'])];
		capturingState = 'Seeking'
		for aTwist in twistsFile:
			if aTwist.strip() == self.directory:
				capturingState = 'Grabbing'
			elif capturingState == 'Grabbing':
				if aTwist.startswith('\t'):
					actorsUsed= aTwist.count("%s");
					self.twists[actorsUsed].append(aTwist.strip());
				else:
					break;
		twistsFile.close();
	
	def getRandomTwist(self, possibleActors):
		"""
		Given a list of *actor*s, generate a random twist from the templates.
		"""
		possibleLists= self.twists[:len(possibleActors)];
		totalList= flatten(possibleLists);
		if totalList:
			templatedTwist= random.choice(totalList);
		else:
			templatedTwist= _("Add more actors to see more twists!");
		actorCount= templatedTwist.count("%s")+1;
		actorList= [random.choice(possibleActors[1:]) for anActor in xrange(actorCount-1)];
		possibleActorNames= tuple([anActor.name for anActor in actorList]);
		return templatedTwist % possibleActorNames;
	
	def getLongestTwist(self):
		allTwists= list(itertools.chain(*self.twists))
		if allTwists:
			return max(allTwists, key=len);
		else:
			return ""
	
	def loadImage(self):
		"""
		Loads the image associated with the backdrop.
		"""
		imagePath= auxiliary.findImage('games/broadway/backdrops',self.directory+'_back.*', graphicExtensions);
		if imagePath is None:
			blank = spyral.util.new_surface(geom['theater'].size)
			blank.fill(colors['green'])
			self.image= blank;
		else:
			self.image= spyral.util.load_image(imagePath);
		self.rect.size= geom['theater'].size;
	
	def loadExternalImage(self):
		self.image= spyral.util.load_image(self.directory)
		# Perform some math to figure out the ideal new scaling ratio
		ow, oh= self.image.get_size()
		nw, nh = geom['theater'].size
		if ow != nw and oh != nh:
			ow, oh, nw, nh= float(ow), float(oh), float(nw), float(nh)
			self.rect.size= geom['theater'].size;
			ratio = max(nw/ow, nh/oh)
			width, height = (ratio * ow, ratio * oh)
			scaledImage = pygame.transform.smoothscale(self.image, (int(width), int(height)))
			self.image = spyral.util.new_surface(geom['theater'].size)
			if width > nw or height > nh:
				dest = (0,0)
				target = Rect( float(width - nw) /2, float(height - nh) / 2, nw, nh)
			self.image.blit(scaledImage, dest, target) 
	
	def encodeJSON(self):
		""" 
		Encodes the object in a JSON-friendly format (dictionary) and returns it.
		"""
		output= {};
		output['External']= self.external
		if self.external:
			pygame.image.save(self.image, directories['temp']+'/temp.png')
			f= open(directories['temp']+'/temp.png', 'rb')
			output['Image']= f.read().encode('base64')
			f.close()
		else:
			output['Directory']= self.directory;
		return output;
	
	@classmethod
	def decodeJSON(cls, input):
		"""
		Class method that decodes a JSON-created object into a Backdrop and returns it.
		"""
		if 'External' in input and input['External']:
			f= open(directories['temp']+'/temp.png', 'wb')
			f.write(input['Image'].decode('base64'))
			f.close()
			image= spyral.util.load_image(directories['temp']+'/temp.png')
			return Backdrop("", external=True, asString=image)
		else:
			directory= safeStr(input['Directory']);
			return Backdrop(directory);
		