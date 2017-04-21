import pygame
import spyral

from constants import *;
import actor;

#_ = lambda x: x

class Director(object):
	"""
	The *Director* is responsible for managing the theater mode; that is, it
	is responsible for telling the actors when to perform actions according to 
	the	script.
	
	Additionally, provides a callback system to run a function when playback
	finishes an action or the entire script.
	"""
	
	def __init__(self, script, subtitler):
		"""
		Initializes the Director
		
		| *script* is the Script object that the Director draws on to direct
		| *subtitler* is the Subtitler object that the Director reports action
		to
		"""
		self.playing= False;
		self.script= script;
		self.subtitler= subtitler;
		self.reset();
	
	def act(self, action):
		"""
		Dispatches the given action to it's subject, making it perform it
		according to the current phase.
		"""
		subject, verb, objects= action.subject, action.verb, action.objects;
		if verb in actor.Actor.actorDispatch:
			perform= actor.Actor.actorDispatch[verb][self.actionPhase];
			self.actionPhase, self.actionProgress=  perform(subject, objects);
		else:
			self.actionPhase= phases.END;
	
	def beginAction(self):
		"""
		Checks if the script has been read all the way through to the ending,
		and if so, stops the action. Otherwise, it begins a new action, which
		involves notifying the subtitler.
		"""
		if self.timeProgress >= self.ending:
			self.stop();
		else:
			action= self.script.actions[self.timeProgress];
			self.act(action);
			self.subtitler.newAction(action);
	
	def continueAction(self):
		"""
		Dispatches the current action and notifies the Subtitler
		"""
		action= self.script.actions[self.timeProgress];
		self.act(action);
		self.subtitler.continueAction(self.actionProgress);
	
	def getCurrentAction(self):
		return self.script.actions[self.timeProgress]
	
	def endAction(self):
		"""
		Advances along the script, dispatches an the end of the action,
		handles any callbacks currently associated with the script, and
		notifies the subtitler that the action has finished.
		"""
		action= self.script.actions[self.timeProgress];
		self.act(action);
		self.timeProgress+= 1;
		self.actionPhase= phases.BEGIN;
		if self.continualCallback is not None:
			self.continualCallback(self.timeProgress, self.actionProgress);
		self.subtitler.stopAction();
	
	def handleAction(self):
		"""
		Based on the current phase, either begins, continues, or ends
		an action.
		"""
		if self.playing:
			# The time is being checked after the action is gotten.
			if self.actionPhase == phases.BEGIN:
				self.beginAction();
			elif self.actionPhase == phases.CONTINUE:
				self.continueAction();
			else:
				self.endAction();
			
	def reset(self):
		"""
		Resets the reading of the script to the very beginning.
		"""
		self.timeProgress= 0;
		self.actionProgress= 0;
		self.actionPhase= phases.BEGIN;
		self.ending= len(self.script.actions);
		self.playing= False;
		self.results= None;
		self.script.setFrame(self.timeProgress);
	
	def isDone(self):
		"""
		Tests if we're done reading the script.
		"""
		return self.timeProgress >= len(self.script.actions);
		
	def start(self, callback= None, continualCallback= None):
		"""
		Begin playback of the script from the beginning.
		"""
		self.reset();
		self.playing= True;
		self.callback= callback;
		self.continualCallback= continualCallback;
		self.script.setFrame(self.timeProgress);
		
	def startAt(self, start, callback= None, continualCallback= None):
		"""
		Begin playback of the script from a given starting point
		"""
		self.start(callback, continualCallback);
		self.timeProgress= start;
		self.script.setFrame(self.timeProgress);
		
	def startRange(self, start, end, callback= None, continualCallback= None):
		"""
		Begin playback of a portion of the script
		"""
		self.startAt(start, callback, continualCallback);
		self.ending= end;
		self.script.setFrame(self.timeProgress);
		
	def stop(self):
		"""
		Halt playback of the script at this point. This is called both
		naturally at the end of a script and by user action.
		"""
		self.playing= False;
		self.subtitler.stopAction();
		pygame.mixer.stop();
		if self.callback is not None:
			self.callback();
	
	def goto(self, timePosition, callback):
		"""
		Change the current time position to the one given. Stops playback.
		"""
		self.actionProgress= 0;
		self.actionPhase= phases.BEGIN;
		self.playing= False;
		self.timeProgress= timePosition;
		self.script.setFrame(self.timeProgress);
		if callback is not None: callback(self.timeProgress, 0);
		
	def rewindAll(self, callback= None):
		"""
		Set playback to the beginning of the script.
		"""
		self.goto(0, callback);
	
	def forwardAll(self, callback= None):
		"""
		Set playback to the end of the script.
		"""
		amount= len(self.script.actions)
		self.goto(amount, callback);
	
	def rewind(self, callback= None):
		"""
		Set playback a few frames back (based on the theater-skip default)
		"""
		amount= max(1, len(self.script.actions) // defaults['theater-skip']);
		amount= max(0, self.timeProgress-amount);
		self.goto(amount, callback);
	
	def forward(self, callback= None):
		"""
		Set playback a few frames forward (based on the theater-skip default)
		"""
		amount= max(1, len(self.script.actions) // defaults['theater-skip']);
		amount= min(len(self.script.actions), self.timeProgress+amount);
		self.goto(amount, callback);