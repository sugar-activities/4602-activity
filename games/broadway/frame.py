import pygame
import spyral

from constants import *;
import state;

import weakref

#_ = lambda x: x

class Frame(weakref.WeakKeyDictionary):
	"""
	A frame is simply a dictionary mapping actors to their states. However,
	it also provides some additional functionality.
	"""
	def copy(self):
		"""
		Overriden method of *dict*. Provides a deep copy instead of a shallow
		copy, so the stored states are new objects; however, the actors remain
		the same.
		"""
		newFrame= Frame();
		for anActor, aState in self.items():
			newFrame[anActor]= aState.copy();
		return newFrame;
	
	def encodeJSON(self):
		""" 
		Encodes the object in a JSON-friendly format (dictionary) and returns it.
		"""
		output= {};
		for anActor, aState in self.items():
			output[id(anActor)]= aState.encodeJSON();
		return output;
	
	@classmethod
	def decodeJSON(cls, input, actorMap):
		"""
		Class method that decodes a JSON-created object into a Frame and returns it.
		
		Requires a dictionary mapping the original actor ID's into the new actor
		objects.
		"""
		newFrame= Frame();
		for oldActorId, anEncodedState in input.items():
			oldActorId= int(oldActorId);
			newFrame[actorMap[oldActorId]]= state.State.decodeJSON(anEncodedState);
		return newFrame;
	
	def __repr__(self):
		return ", ".join([str(anActor.name) + " ("+str(anActor)+") => " + str(aState) for anActor, aState in self.items()]);
			
if __name__ == '__main__':
	test= Frame();
	test["an-actor"]= state.State();
	test2= test.copy();
	test["an-actor"].position= 'sad';
	print test, test2;