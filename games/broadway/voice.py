import simplejson as json;

import constants;
import auxiliary;

#_ = lambda x: x

class Voice(object):
	"""
	Represents the parameters for an Espeak voice. Externally, the visible name
	is what is displayed to the user. Internally, the espeakName, pitch, and
	speed are used as parameters to the external eSpeak process.
	"""
	def __init__(self, visibleName, espeakName, pitch, speed):
		"""
		Initializes the Voice object.
		
		| *visibleName* a string that is presented to the user in a Panel.
		| *espeakName* the name of the voice that eSpeak should use.
		| *pitch* the pitch of the voice (0-100)
		| *speed* the speed of the voice (0-255)
		"""
		self.visibleName= visibleName;
		self.espeakName= espeakName;
		self.pitch= pitch;
		self.speed= speed;
	
	def encodeJSON(self):
		""" 
		Encodes the object in a JSON-friendly format (dictionary) and returns it.
		"""
		output= {};
		output['Visible Name']= self.visibleName;
		output['Espeak Name']= self.espeakName;
		output['Pitch']= self.pitch;
		output['Speed']= self.speed;
		return output;
	
	@classmethod
	def decodeJSON(cls, input):
		"""
		Class method that decodes a JSON-created object into a Voice and returns it.
		"""
		for aVoice in constants.voices:
			if (aVoice.visibleName == input['Visible Name']):
				return aVoice;
		return Voice(safeStr(input['Visible Name']),
					 safeStr(input['Espeak Name']),
					 safeStr(input['Pitch']),
					 safeStr(input['Speed']));