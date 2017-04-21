import simplejson as json;
import os, sys, glob;
import time;
import itertools;
import string
import requests

import pygame

#_ = lambda x: x

"""
HACK: Auxilary files are always dirty hacks, but often very convenient ones.
In a perfect program, these would be factored away to other places.
Broadway is not perfect.
"""

# """
# Memory leak debug tools
# """
# def checkAllWidgets(aWidget, skip):
	# if hasattr(aWidget, 'widgets'):
		# for aSubWidget in aWidget.widgets:
			# checkBackrefs(aSubWidget, str(id(aSubWidget)), [id(skip)]);
			# checkAllWidgets(aSubWidget, skip);

# def memoryCheck(something):
	# import objgraph;
	# objgraph.show_backrefs(something, filename=r'C:\Users\acbart\Projects\Thesis\Broadway\objectgraphs\test.png');

# def memoryStop():
	# pass;
	##print objgraph.show_backrefs('FilePanel');

# def getAllInstances(aClass):
	# import gc;
	# gc.collect();
	# return [obj for obj in gc.get_objects() if isinstance(obj, aClass)];

# def checkBackrefs(something, filename='', ignores=[]):
	# import objgraph;
	# objgraph.show_backrefs(something, max_depth=4, too_many= 20, filename= r'C:\Users\acbart\Projects\Thesis\Broadway\objectgraphs\graph'+filename+'.png', extra_ignore=ignores); #

# def checkRemainingRefs(something):
	# print "Refs of",something,"=",sys.getrefcount(something);

def changeSetting(key, value):
	data= json.load(open('games/broadway/settings.txt', 'r'))
	data[key] = value
	json.dump(data, open('games/broadway/settings.txt', 'w'))
	
def findImage(directory, pattern, extensions):
	'''Given a directory, a pattern, and a list of valid extensions,
	returns the first valid image file that matches that pattern'''
	paths= os.path.join(directory,pattern)
	for aPath in glob.glob(paths):
		aFile= os.path.basename(aPath);
		name, period, extension= aFile.partition('.');
		if extension in extensions:
			return aPath;
	return None;
	
def findPattern(directory, pattern, extensions):
	'''Given a directory, a pattern, and a list of valid extensions,
	returns all the files that match the pattern in that directory'''
	found= set();
	paths= os.path.join(directory,pattern)
	for aPath in glob.glob(paths):
		aFile= os.path.basename(aPath);
		name, period, extension= aFile.partition('.');
		if extension in extensions:
			name, underscore, type= name.partition('_');
			found.add(name);
	return found;
	
def findValidBackdrops(graphicExtensions):
	''' Return a list of all the valid backdrops found '''
	if os.path.exists('games/broadway/backdrops'):
		thumbs= findPattern('games/broadway/backdrops', '*_thumb.*', graphicExtensions);
		backs= findPattern('games/broadway/backdrops', '*_back.*', graphicExtensions);
		# intersect the sets to ensure both backdrop and thumb are present
		valids= backs & thumbs;
		if valids:
			return list(valids);
		else:
			raise Exception('Backdrop folder had no valid backdrops');
	else:
		raise Exception('Backdrop folder not found');
def findValidActors():
	''' Return a list of all the valid actors found in the actors folder '''
	if os.path.exists('games/broadway/actors'):
		validActors= [];
		for anActor in os.listdir('games/broadway/actors'):
			anActorDir= os.path.join('games/broadway/actors', anActor);
			if os.path.isdir(anActorDir):
				dataFile= os.path.join(anActorDir, anActor + '.txt');
				if os.path.exists(dataFile):
					validActors.append(anActor);
		if validActors:
			return validActors;
		else:
			raise Exception('No valid actors were found');
	else:
		raise Exception('Actor folder not found');
	
class Enumerate(object):
	"""
	Used to conveniently create enumerations. A single string is passed in of
	space-delimited words, with each word becoming an element of the enumeration.
	
	e.g.
		animals("DOG CAT BIRD COW")
		would create the following constants:
			animals.DOG
			animals.CAT
			animals.BIRD
			animals.COW
	"""
	def __init__(self, names):
		self.names= names.split();
		for number, name in enumerate(self.names):
			setattr(self, name, number)

	def items(self):
		return self.names[:];

def getMoveString(position):
	"""
	Depending on if the position given is a string or not, determines if the
	position in question is onscreen or offscreen.
	TODO: Figure out which class should own this. Probably *Action*.
	"""
	if type(position) is str:
		return _('Come in:');
	else:
		return _('Leave:   ');

	
def splitListAt(list, at):
	""" Returns two lists from the original, representing it split at a point"""
	return list[:at], list[at:];

def calculateLinearMovement(timeProgress, pos1, pos2):
	"""
	Performs linear interpolation between two positions for a given floating
	time between 0 and 1.
	"""
	x1, y1= pos1;
	x2, y2= pos2;
	xDistance = (x2 - x1) * timeProgress;
	yDistance = (y2 - y1) * timeProgress;
	newX= x1 + xDistance;
	newY= y1 + yDistance;
	return newX, newY;
	
def getCurrentTime():
	"""
	Wrapper for getting the current time.
	"""
	return time.time();


def flatten(listOfLists):
	"""
	Flatten one level of nesting for a list of lists.
	What's in the lists? WHATEVER YOU PUT IN IT.
	"""
	flatList= [anElement for aList in listOfLists for anElement in aList];
	return flatList;

def safeStr(aThing):
	"""
	Ensures that any strings passed in are stored as regular strings, not unicode.
	Doesn't do anything to other types.
	"""
	if type(aThing) == unicode:
		return str(aThing);
	else:
		return aThing;
	
def filenameStrip(filename):
	"""
	Returns a copy of the string made suitable for saving to a unix file system.
	Culled from this Stack Overflow:
	http://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename-in-python
	"""
	valid_chars = frozenset("-_.() %s%s" % (string.ascii_letters, string.digits))
	return ''.join(c for c in filename if c in valid_chars)

"""
aspect_scale.py - Scaling surfaces keeping their aspect ratio
Raiser, Frank - Sep 6, 2k++
crashchaos at gmx.net

This is a pretty simple and basic function that is a kind of
enhancement to pygame.transform.scale. It scales a surface
(using pygame.transform.scale) but keeps the surface's aspect
ratio intact. So you will not get distorted images after scaling.
A pretty basic functionality indeed but also a pretty useful one.

Usage:
is straightforward.. just create your surface and pass it as
first parameter. Then pass the width and height of the box to
which size your surface shall be scaled as a tuple in the second
parameter. The aspect_scale method will then return you the scaled
surface (which does not neccessarily have the size of the specified
box of course)

Dependency:
a pygame version supporting pygame.transform (pygame-1.1+)
"""
def aspect_scale(img,(bx,by)):
	""" Scales 'img' to fit into box bx/by.
	 This method will retain the original image's aspect ratio """
	ix,iy = img.get_size()
	if ix < iy:
		# fit to width
		scale_factor = bx/float(ix)
		sy = scale_factor * iy
		if sy > by:
			scale_factor = by/float(iy)
			sx = scale_factor * ix
			sy = by
		else:
			sx = bx
	else:
		# fit to height
		scale_factor = by/float(iy)
		sx = scale_factor * ix
		if sx > bx:
			scale_factor = bx/float(ix)
			sx = bx
			sy = scale_factor * iy
		else:
			sy = by

	return pygame.transform.scale(img, (sx,sy))