import pygame
import spyral

from constants import *;
import auxiliary;

#_ = lambda x: x

class Subtitler(spyral.sprite.Sprite):
	"""
	The *Subtitler* is responsible for drawing subtitles on the screen. 
	Subtitles could be spoken text or simple a description of an action taking
	place. The speaker's name is displayed above the current line.
	
	An attempt is made at breaking the text into chunks and displaying different
	chunks at different times, but it's not very sophisticated. Don't expect
	anything resembling perfect synchronization.
	"""
	def __init__(self):
		"""
		Initializes the *Subtitler*.
		"""
		spyral.sprite.Sprite.__init__(self)
		self.on= True;
		self.currentAction= None;
		self.currentProgress= None;
		self.visible= False;

	def splitText(self, text, index):
		"""
		Returns two strings from the original, representing it split at a point.
		"""
		return text[:index], text[index:];
	
	def breakText(self, text):
		"""
		Given some text, returns a list of strings representing the text broken
		up into ready-to-render sizes. Doesn't do anything smart like look for
		spaces :/
		"""
		lines= [];
		currentLength= 1;
		while text and currentLength < len(text):
			newText= text[:currentLength+1];
			newWidth, newHeight= self.font.size(newText);
			if (newWidth > geom['subtitle'].width):
				line, text= self.splitText(text, currentLength);
				lines.append(line);
			else:
				currentLength+= 1;
		if text: lines.append(text);
		return lines;
	
	def checkFontCode(self, code):
		"""
		Based on the given code, returns the correct font. It made a heck of
		a lot more sense before I changed the way information was given to the
		*Subtitler*. Now it's just redundant and stupid.
		"""
		if code == subtitleCode['italic']:
			return fonts['italic'];
		else:
			return fonts['normal'];
		
	def newAction(self, action):
		"""
		Called when a new *Action* is being performed, which signals the
		*Subtitler* to modify itself for rendering based on the *action*.
		"""
		self.currentAction= action;
		self.currentProgress= -1;
		code, self.name, text= action.toSubtitle();
		self.font= self.checkFontCode(code);
		self.lines= self.breakText(text);
		
	def stopAction(self):
		"""
		Called when an "Action" is ended, which signals the *Subtitler* to
		clean itself up and not leave behind any artifacts.
		"""
		self.pos= marks['offstage'];
		self.visible= False;
		self.lines= [];
		
	def renderText(self, text):
		"""
		Return a surface with the string drawn on it in the correct color.
		"""
		text= self.font.render(text, True, colors['white'], colors['black']);
		return text, text.get_size();
		
	
	def renderSubtitle(self, name, text):
		"""
		Create a surface of the appropriate size with the *name* and *text*
		rendered on it, centered appropriately.
		"""
		text, (textWidth, textHeight)= self.renderText(text);
		name, (nameWidth, nameHeight)= self.renderText(name);
		backingWidth= max(textWidth, nameWidth);
		backingHeight= textHeight + nameHeight;
		backingSize= Rect(0,0,backingWidth, backingHeight);
		backing= spyral.util.new_surface(backingSize.size);
		nameX= backingWidth/2 - nameWidth/2;
		backing.blit(name, (nameX, 0));
		textX= backingWidth/2 - textWidth/2;
		backing.blit(text, (textX, nameHeight));
		return backing, backingSize;
		
	def continueAction(self, progress):
		"""
		Called when an action is occurring, in order to update the *Subtitler*
		on the *progress* of the current action, in the event that, e.g., the 
		speech has progressed enough and the next segment of it should be 
		rendered.
		"""
		self.visible= bool(self.lines)  and self.on;
		if self.visible:
			newProgress= min(len(self.lines)-1, int(progress * len(self.lines)));
			if (self.currentProgress != newProgress):
				self.currentProgress= newProgress;
				text= self.lines[self.currentProgress];
				self.image, self.rect= self.renderSubtitle(self.name, text);
				self.rect.midbottom= geom['subtitle'].topleft;
		if not self.on:
			self.stopAction();