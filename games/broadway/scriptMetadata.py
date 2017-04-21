import simplejson as json;

from auxiliary import *;
from constants import *;

#_ = lambda x: x

class ScriptMetadata(object):
	"""
	Metadata is information about a *Script* that isn't core. This includes the
	*title*, *description*, and *author*'s. There's nothing fancy here. Heck,
	it probably could have just been a Dict without any real trouble. But hey,
	why not. It was demonstrated very admirably in my 475 class that you can
	never have enough METADATA. It's not like security, which is way too easy
	to overdo!
	
	And I deny that this classes existence is strictly a sarcastic joke. It just
	looks that way, acts that way, and quacks that way. Oh wait, this is Python.
	Duck typing. Right.
	"""
	def __init__(self):
		"""
		Initializes the *ScriptMetadata*.
		"""
		self.reset();
	
	def reset(self):
		"""
		Resets all data associated with the Script.
		"""
		self.title= "";
		self.author= "";
		self.description= "";
		self.version = information['version']
	
	def toText(self):
		"""
		Returns a textual representation of this metadata
		"""
		return  (_("Title: %s\n"
				  "Author(s): %s\n"
				  "Description: %s\n"
				  "Version: %s\n") % 
				 (self.title,
				  self.author,
				  self.description,
				  self.version))
	
	def encodeJSON(self):
		""" 
		Encodes the object in a JSON-friendly format (dictionary) and returns it.
		"""
		output= {};
		output['Title']= self.title;
		output['Author']= self.author;
		output['Description']= self.description;
		output['Version']= information['version']
		return output;
	
	@classmethod
	def decodeJSON(cls, input):
		"""
		Class method that decodes a JSON-created object into a ScriptMetadata 
		and returns it.
		"""
		newMetadata= ScriptMetadata();
		newMetadata.title= safeStr(input['Title']);
		newMetadata.author= safeStr(input['Author']);
		newMetadata.description= safeStr(input['Description']);
		if 'Version' in input:
			newMetadata.version= safeStr(input['Version']);
		else:
			newMetadata.version= '1.0'
		return newMetadata;