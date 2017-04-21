import pygame
import spyral

from constants import *;
import action;

#_ = lambda x: x

class State(object):
	"""
	A state is representation of the state of an Actor. There are four parts:
	a *direction* (which way they're facing), a *position* (where they are on
	the screen), a *pose* (the body image they are using), and a *look* (the
	expression of their face).
	"""
	def __init__(self, pos= (0,0), dir= 'left', pose='stands', look='happy'):
		"""
		Initializes a new *State* object.
		"""
		self.direction= dir; #direction.LEFT, RIGHT
		self.position= pos; #tuple, 'left', 'right'
		self.pose= pose; #string
		self.look= look; #string
	
	def encodeJSON(self):
		""" 
		Encodes the object in a JSON-friendly format (dictionary) and returns it.
		"""
		output= {};
		output['Position']= self.position;
		output['Look']= self.look;
		output['Pose']= self.pose;
		output['Direction']= self.direction;
		return output;
	
	def intersect(self, other):
		"""
		Returns which of the aspects of two states differ.
		"""
		differentPosition= (self.position != other.position);
		differentLook= (self.look != other.look);
		differentPose= (self.pose != other.pose);
		differentDirection= (self.direction != other.direction);
		return differentPosition, differentLook, differentPose, differentDirection;
	
	@classmethod
	def decodeJSON(cls, input):
		"""
		Class method that decodes a JSON-created object into a State and returns
		it.
		"""
		return State(safeStr(input['Position']),
					 safeStr(input['Direction']),
					 safeStr(input['Pose']),
					 safeStr(input['Look']));
	
	def __repr__(self):
		"""
		Creates a simple string representation of the *State*.
		"""
		position= str(self.position);
		look= str(self.look);
		pose= str(self.pose);
		direction= self.direction;
		return "("+", ".join([position,look,pose,direction])+")";

	def copy(self):
		"""
		Returns a new *State* object based on this one.
		"""
		return State(self.position, self.direction, self.pose, self.look);
	
	def makeActions(self, character):
		"""
		Given a *State* object, creates a list of *Action*s that could be 
		applied to another state to transform it into this one.
		"""
		actionList= [action.Action(character, verbs.FEEL, self.look),
					 action.Action(character, verbs.MOVE, self.position),
					 action.Action(character, verbs.DO, self.pose),
					 action.Action(character, verbs.FACE, self.direction)];
		return actionList;
	
	def applyAction(self, action):
		"""
		Transform this *State* according to the *Action*.
		"""
		verb= action.verb;
		if verb == verbs.FEEL:
			self.look= action.objects;
		elif verb == verbs.DO: 
			self.pose= action.objects;
		elif verb == verbs.FACE: 
			self.direction= action.objects;
		elif verb == verbs.MOVE: 
			self.position= action.objects;
		elif verb == verbs.EXIT: 
			self.position= action.objects;
		elif verb == verbs.ENTER: 
			self.position= action.objects;
	
	def getFromAction(self, action):
		"""
		Given an *Action*, returns the field in the *State* that the action's
		verb corresponds to.
		"""
		verb= action.verb;
		if verb == verbs.FEEL:
			return self.look;
		elif verb == verbs.MOVE: 
			return self.position;
		elif verb == verbs.DO: 
			return self.pose;
		elif verb == verbs.FACE: 
			return self.direction;
		elif verb == verbs.EXIT: 
			return self.position;
		elif verb == verbs.ENTER: 
			return self.position;