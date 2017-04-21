import os,sys;
import time;
import subprocess;
import random;
import math;
from struct import unpack;

#_ = lambda x: x

import pygame
import spyral

from constants import *;
from broadway import hacks
import state;
import action;
import voice;

class Actor(spyral.sprite.Sprite):
	"""
	Represents a character in the game, both the one in the script and
	the image on the screen.
	"""
	def __init__(self, directory, name="", narrator= False):
		"""
		Initializes the Actor
		
		| *directory* is the directory containing graphics and the text file
		| *name* is the user-given name of the Actor. If no name is given, the directory is used.
		| *narrator* is a boolean indicating if this actor is the narrator
		"""
		self.face= spyral.sprite.Sprite();
		self.face.mouth= False;
		spyral.sprite.Sprite.__init__(self)
		self.state= state.State();
		self.narrator= narrator;
		self.changeImages(directory);
		if narrator:
			self.pos= marks['narrator'];
			self.image= spyral.util.new_surface((1,1));
			self.face.image= spyral.util.new_surface((1,1));
		if name:
			self.name= name;
		else:
			self.name= directory;
		self.voice= defaults['voice'];
		self.face.layer= 'faces';
		self.layer= 'stage';
	
	def add(self, *groups):
		""" Override sprite's add method to also add the face to the 
		group(s)"""
		spyral.sprite.Sprite.add(self, *groups);
		self.face.add(*groups);
	
	def kill(self):
		""" Override sprite's kill method to also kill the face """
		if self.face:
			self.face.kill();
			self.face= None;
		spyral.sprite.Sprite.kill(self);
	
	def remove(self, *groups):
		""" Override sprite's remove method to also remove the face from the 
		group(s) """
		spyral.sprite.Sprite.remove(self, *groups);
		if self.face:
			self.face.remove(*groups);
			self.face= None;
	
	def encodeJSON(self):
		""" 
		Encodes the object in a JSON-friendly format (dictionary) and returns it.
		"""
		output= {};
		output['Id']= id(self);
		output['Voice']= self.voice.encodeJSON();
		output['Name']= self.name;
		output['Directory']= self.directory;
		output['Narrator']= self.narrator;
		return output;
	
	@classmethod
	def decodeJSON(cls, input):
		"""
		Class method that decodes a JSON-created object into an Actor and returns it.
		Additionally returns the original ID of this actor
		"""
		directory= safeStr(input['Directory']);
		name= safeStr(input['Name']);
		narrator= safeStr(input['Narrator']);
		newActor= Actor(directory, name, narrator);
		newActor.voice= voice.Voice.decodeJSON(input['Voice']);
		return newActor, input['Id'];

	#def isTalkingLoudly(self, length, startTime, samples):
	def isTalkingLoudly(self):
		"""
		For a given array of samples with a total length and startTime, 
		determines if at this point in time, the actor is speaking loudly.
		"""
		# timePosition= (getCurrentTime() - startTime) / length;
		# samplePosition= int( timePosition * defaults['mixer-frequency']);
		# startPosition= max(0, samplePosition- defaults['mouth-range']);
		# endPosition= min(defaults['mixer-frequency']-1, samplePosition+ defaults['mouth-range']);
		# absHeights= numpy.core.abs(samples[startPosition:endPosition]);
		# if absHeights.size <= 0:
			# height= 0;
		# else:
			# height= numpy.average(absHeights);
		# return (height > defaults['mouth-threshold']);
		return (random.randint(1, 4) == 1);
	
	def quickSpeak(self, text):
		speechPath= os.path.join(directories['temp'], "speech.wav");
		subprocess.call([processes['espeak'], 
							"-w", speechPath,
							"-p", str(self.voice.pitch),
							"-s", str(self.voice.speed),
							"-v", self.voice.espeakName,
							text])
		speech= pygame.mixer.Sound(speechPath);
		speech.play();
		
	
	def changeImages(self, directory):
		"""
		Changes the directory that this Actor takes it's images from.
		"""
		self.directory= directory;
		self.loadImages();
		self.poses= self.bodies.keys();
		self.looks= self.faces.keys();
		if not self.narrator:
			self.changeBody(True, True, True, True);
	
	def shortName(self, length):
		"""
		If the name is more than the length, shortens it and ends it with dots.
		"""
		if len(self.name) > length:
			return self.name[:length-3]+'...';
		else:
			return self.name;
	
	def setState(self, state):
		"""
		Set's this actor to the given state, and updates it graphically.
		The state is copied, so that the original will not be affected if 
		changes are made (such as via applyAction).
		"""
		changes= state.intersect(self.state)
		self.state= state.copy();
		self.changeBody(*changes);
	
	def applyAction(self, action):
		"""
		Uses the action to change the actor's current state, and update it
		graphically.
		"""
		changes= action.getStateChange();
		self.state.applyAction(action);#####
		self.changeBody(*changes);
	
	def reposition(self, position= None):
		"""
			Move the actor based on either the given position or the position 
			given by it's state.
		"""
		if self.narrator: return;
		if position is None:
			position= self.state.position;
		if type(position) is str:
			self.pos= marks['offstage'];
		else:
			self.rect.center= position;
	
	def repositionFace(self):
		"""
		Updates the location of the actors face using the current position
		"""
		if self.narrator: return;
		if self.state.pose not in self.anchors: return;
		faceAnchor= self.anchors[self.state.pose];
		if self.state.direction == 'left':
			dx, dy = faceAnchor
			faceAnchor= (-dx, dy)
		self.face.rect.center= self.rect.center ;
		self.face.pos= spyral.point.add(self.face.pos, faceAnchor)
	
	def changeBodyPosition(self):
		"""
		Repositions both the body and face of the actor
		"""
		if self.narrator: return;
		self.reposition();
		self.repositionFace();
	def changeBodyDirection(self):
		"""
		Updates the direction of the body and face of the actor
		"""
		if self.narrator: return;
		self.changeFaceExpression();
		self.changeBodyPose();
	def changeFaceState(self, mouth):
		"""
		Changes whether the mouth is currently open or not; doesn't do any
		repositioning.
		"""
		if self.narrator: return;
		if self.state.look not in self.faces: return;
		self.face.image= self.faces[self.state.look][mouth][self.state.direction == 'left']
		self.face.rect.size= self.face.image.get_rect().size;
		self.face.mouth= mouth;
	def changeFaceExpression(self):
		"""
		Updates the actor's expression and ensures it is at the correct position
		"""
		if self.narrator: return;
		if self.state.look not in self.faces: return;
		self.face.image= self.faces[self.state.look][self.face.mouth][self.state.direction == 'left']
		self.face.rect.size= self.face.image.get_rect().size;
		self.repositionFace();
	def changeBodyPose(self):
		"""
		Updates the actor's pose and ensures it is at the correct position
		"""
		if self.narrator: return;
		if self.state.pose not in self.bodies: return;
		self.image = self.bodies[self.state.pose][self.state.direction == 'left']
		self.rect.size= self.image.get_rect().size;
		self.changeBodyPosition();
	
	def changeBody(self, position, look, pose, direction):
		"""
		Uses the boolean arguments to identify what aspects of the actor
		to update graphically
		"""
		if self.narrator: return;
		if pose: self.changeBodyPose();
		if look: self.changeFaceExpression();
		if position: self.changeBodyPosition();
		if direction: self.changeBodyDirection();
	
	def loadImages(self):
		"""
		Initializes the data structures that hold the bodies and faces of the 
		actor, and then loads all the graphical data from the current directory.
		The directory should have the following structure
			face_<face>_open.png
			face_<face>_close.png
			pose_<pose>.png
			<actor>.txt
			thumb.png
		"""
		self.bodies= {};
		self.anchors= {};
		self.faces= {};
		bodiesNames, self.anchors, facesNames= self.readPathsFile();
		self.thumb= self.loadThumb();
		self.bodies= self.loadBodies(bodiesNames);
		self.faces= self.loadFaces(facesNames);
		
	def readPathsFile(self):
		"""
		Opens the paths file for the actor, located in the directory with the
		same name as the directory. Returns lists of all the faces and poses,
		and a dictionary of the poses and their face-anchors.
		
		Each line in the file is one of:
			face, <emotion>
			body, <pose>, <anchor-x>, <anchor-y>
		"""
		actorPath= os.path.join('games/broadway/actors', self.directory, self.directory+".txt")
		if os.path.exists(actorPath):
			actorFile= open(actorPath, 'r');
			bodies= [];
			anchors= {};
			faces= [];
			for aLine in actorFile:
				type, comma, data= aLine.partition(',');
				type= type.strip();
				if type == 'body':
					body, x, y= data.split(',');
					anchors[body.strip()]= (int(x), int(y)) ;
					bodies.append(body.strip());
				elif type == 'face':
					faces.append(data.strip());
				else:
					print "Unknown type in",actorFile;
			actorFile.close();
			return bodies, anchors, faces;
		else:
			return [],{},[];
	
	def loadThumb(self):
		"""
		Loads the thumbnail image for the actor
		"""
		thumbFile= os.path.join('games/broadway/actors', self.directory, "thumb.gif")
		# HACK: in the future, it will always be PNG
		if not os.path.exists(thumbFile):
			thumbFile= os.path.join('games/broadway/actors', self.directory, "thumb.png")
		if os.path.exists(thumbFile):
			thumb= spyral.util.load_image(thumbFile);
			return thumb;
		else:
			print "Couldn't load thumb,",thumbFile;
			return spyral.util.new_surface(geom['thumb'].size);
		
	def loadBodies(self, bodyNames):
		"""
		Iterates over the list of given body names and loads the images 
		associated with each one (expects files named "pose_<body name>.png")
		
		Returns a dictionary mapping the name to the image.
		"""
		bodyImages= {};
		for aBody in bodyNames:
			bodyFile= os.path.join('games/broadway/actors', self.directory, "pose_"+aBody+".gif")
			# HACK: in the future, it will always be PNG
			if not os.path.exists(bodyFile):
				bodyFile= os.path.join('games/broadway/actors', self.directory, "pose_"+aBody+".png")
			if os.path.exists(bodyFile):
				body= spyral.util.load_image(bodyFile);
				bodyImages[aBody]= (body, pygame.transform.flip(body, True, False));
		return bodyImages;
		
	def loadFaces(self, faceNames):
		"""
		Iterates over the list of given face names and loads the images 
		associated with each one, both the open mouthed and closed mouth version.
		
		Returns a dictionary mapping the name to a tuple of open and closed
		mouth versions of the image.
		"""
		faceImages= {};
		for aFace in faceNames:
			faceOpenFile= os.path.join('games/broadway/actors', self.directory, "face_"+aFace+"_open.gif")
			faceCloseFile= os.path.join('games/broadway/actors', self.directory, "face_"+aFace+"_closed.gif")
			# HACK: in the future, it will always be PNG
			if not os.path.exists(faceOpenFile):
				faceOpenFile= os.path.join('games/broadway/actors', self.directory, "face_"+aFace+"_open.png")
			if not os.path.exists(faceCloseFile):
				faceCloseFile= os.path.join('games/broadway/actors', self.directory, "face_"+aFace+"_closed.png")
			if os.path.exists(faceCloseFile) and os.path.exists(faceOpenFile):
				faceOpen= spyral.util.load_image(faceOpenFile);
				faceClose= spyral.util.load_image(faceCloseFile);
			else:
				print "Couldn't find either",faceOpenFile,"or",faceCloseFile;
			flipClose= pygame.transform.flip(faceClose, True, False);
			flipOpen= pygame.transform.flip(faceOpen, True, False);
			faceImages[aFace]= ((faceClose, flipClose), (faceOpen, flipOpen));
		return faceImages;
	
	"""
	The following series of functions follow a consistent pattern
	<act>Begin(self, data)
		-> new phase (element of phases enumeration), progress (float 0..1)
	<act>Continue(self, data)
		-> new phase (element of phases enumeration), progress (float 0..1)
	<act>End(self, data)
		-> new phase (element of phases enumeration), progress (float 0..1)
	Each tuple of <act>s maps to an action verb via the actorDispatch at the
	end.
	"""
	
	def _feelBegin(self, emotion):
		"""
		Changes the actor's state and immediately moves to the CONTINUE phase
		"""
		self.applyAction(action.Action(self, verbs.FEEL, emotion));
		self._actionStartTime= getCurrentTime();
		return phases.CONTINUE, 0;
	def _feelContinue(self, emotion):
		"""
		Delays transition to the END phase until a actor pause duration passes.
		"""
		timePassed= getCurrentTime() - self._actionStartTime;
		if (timePassed >= defaults['actor-pause']):
			return phases.END, 1;
		else:
			return phases.CONTINUE, timePassed / defaults['actor-pause'];
	def _feelEnd(self, emotion):
		"""
		No action
		"""
		return phases.END, 1;
		
	def _sayBegin(self, text):
		"""
		Creates the speech file using Espeak, and begins playback of it.
		If the file isn't 0-length, move to CONTINUE phase.
		"""
		speechPath= os.path.join(directories['temp'], "speech.wav");
		subprocess.call([processes['espeak'], 
							"-w", speechPath,
							"-p", str(self.voice.pitch),
							"-s", str(self.voice.speed),
							"-v", self.voice.espeakName,
							text])
		self._actionSpeech= pygame.mixer.Sound(speechPath);
		# HACK: There's an error in sndarray that miscalculates the size of
		# the array. Therefore, I'm using this hack from the Speak activity.
		# self._actionSamples= pygame.sndarray.array(self._actionSpeech);
		self._actionChannel= self._actionSpeech.play();
		if hacks['mute']: self._actionChannel.set_volume(0);
		self._actionStartTime= getCurrentTime();
		if self._actionSpeech.get_length() > 0:
			return phases.CONTINUE, 0;
		else:
			return phases.END, 1;
	def _sayContinue(self, text):
		"""
		Delays transition to the END phase until the speech is finished,
		while also moving the mouth when the speech is at a threshold.
		"""
		if self._actionChannel.get_busy():
			length= self._actionSpeech.get_length();
			if self.isTalkingLoudly() and text.strip():
				self.changeFaceState(True);
			else:
				self.changeFaceState(False);
			timePassed= getCurrentTime() - self._actionStartTime;
			progress= timePassed / self._actionSpeech.get_length();
			return phases.CONTINUE, progress;
		else:
			return phases.END, 1;
	def _sayEnd(self, text):
		"""
		Ensures that the actor's mouth is left closed. Don't want them to look
		stupid.
		"""
		self.changeFaceState(False);
		return phases.END, 1;
		
	def _moveBegin(self, target):
		"""
		Calculates how long it will take the actor to move to the target.
		Additionally, if the actor is offstage, moves them to an actual position.
		If the actor is not already at the target, transition to the CONTINUE phase.
		"""
		self._actionStartPosition= self.state.position;
		if type(self._actionStartPosition) is str:
			if marks['center'][0] <= target[0]:
				self._actionStartPosition= marks['offstage-right'];
			else:
				self._actionStartPosition= marks['offstage-left'];
		distance= spyral.point.dist(self._actionStartPosition, target);
		self._actionStartTime= getCurrentTime();
		self._actionTravelTime= distance / defaults['actor-speed'] 
		if self._actionTravelTime == 0:
			return phases.END, 1;
		else:
			return phases.CONTINUE, 0;
	def _moveContinue(self, target):
		"""
		Linearaly interpolate the actor's position according to how much
		time has passed.
		
		When the calcluated time has passed, advance to the END phase.
		"""
		currentTime= getCurrentTime() - self._actionStartTime;
		progress= max(min(currentTime / self._actionTravelTime, 1), 0);
		def modulate(value):
			return math.sin(value * math.pi / 2);
		progress= modulate(progress);
		currentPosition= calculateLinearMovement(progress, self._actionStartPosition, target);
		self.reposition(currentPosition);
		self.repositionFace();
		if progress >= 1:
			return phases.END, progress;
		else:
			return phases.CONTINUE, progress;
	def _moveEnd(self, target):
		"""
		Apply the action to ensure we didn't accidentally overshoot our target.
		"""
		self.applyAction(action.Action(self, verbs.MOVE, target));
		return phases.END, 1;
		
	def _doBegin(self, pose):
		"""
		Apply the action
		"""
		self.applyAction(action.Action(self, verbs.DO, pose));
		self._actionStartTime= getCurrentTime();
		return phases.CONTINUE, 0;
	def _doContinue(self, pose):
		"""
		Delay until the actor pause duration has passed, then transition.
		"""
		timePassed= getCurrentTime() - self._actionStartTime;
		if (timePassed >= defaults['actor-pause']):
			return phases.END, 1;
		else:
			return phases.CONTINUE, timePassed / defaults['actor-pause'];
	def _doEnd(self, pose):
		"""
		No action.
		"""
		return phases.END, 1;
		
	def _faceBegin(self, direction):
		"""
		Change the actors direction.
		"""
		self.applyAction(action.Action(self, verbs.FACE, direction));
		self._actionStartTime= getCurrentTime();
		return phases.CONTINUE, 0;
	def _faceContinue(self, direction):
		"""
		Delay until the actor pause duration has passed, then transition.
		"""
		timePassed= getCurrentTime() - self._actionStartTime;
		if (timePassed >= defaults['actor-pause']):
			return phases.END, 1;
		else:
			return phases.CONTINUE, timePassed / defaults['actor-pause'];
	def _faceEnd(self, direction):
		"""
		No action.
		"""
		return phases.END, 1;
		
	def _exitBegin(self, direction):
		"""
		Calculate the actual position the actor should exit to, based on the
		direction and their current y-position (actor moves perfectly horizontally)
		"""
		targetX,fakeY= marks['offstage-'+direction];
		if type(self.state.position) is str:
			targetY= fakeY;
		else:
			currentX, targetY= self.state.position;
		self._actionTarget= (targetX,targetY);
		return self._moveBegin(self._actionTarget);
	def _exitContinue(self, direction):
		"""
		Exiting is just moving offstage.
		"""
		return self._moveContinue(self._actionTarget);
	def _exitEnd(self, direction):
		"""
		Exiting is just moving offstage.
		"""
		return self._moveEnd(self._actionTarget);
		
	def _enterBegin(self, target):
		"""
		Entering is just moving onstage.
		"""
		return self._moveBegin(target);
	def _enterContinue(self, target):
		"""
		Entering is just moving onstage.
		"""
		return self._moveContinue(target);
	def _enterEnd(self, target):
		"""
		Entering is just moving onstage.
		"""
		return self._moveEnd(target);
		
	def _focusBegin(self, garbage):
		"""
		No action
		"""
		return phases.END, 0;
	def _focusContinue(self, garbage):
		"""
		No action
		"""
		return phases.END, 1;
	def _focusEnd(self, garbage):
		"""
		No action
		"""
		return phases.END, 1;
		
	def _startBegin(self, garbage):
		"""
		No action
		"""
		return phases.END, 0;
	def _startContinue(self, garbage):
		"""
		No action
		"""
		return phases.END, 1;
	def _startEnd(self, garbage):
		"""
		No action
		"""
		return phases.END, 1;
	
	"""
	The actor dispatch is a dictionary mapping verbs to a tuple of act methods.
	"""
	actorDispatch= {verbs.FEEL  :  (_feelBegin, _feelContinue, _feelEnd),
					verbs.SAY   :  (_sayBegin, _sayContinue, _sayEnd),
					verbs.MOVE  :  (_moveBegin, _moveContinue, _moveEnd),
					verbs.DO    :  (_doBegin, _doContinue, _doEnd),
					verbs.FACE  :  (_faceBegin, _faceContinue, _faceEnd),
					verbs.EXIT  :  (_exitBegin, _exitContinue, _exitEnd),
					verbs.ENTER :  (_enterBegin, _enterContinue, _enterEnd),
					verbs.FOCUS :  (_focusBegin, _focusContinue, _focusEnd),
					verbs.START :  (_startBegin, _startContinue, _startEnd)};