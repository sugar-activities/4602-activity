"""These widgets are all grouped together because they are non-interactive widgets.
"""

import pygame

from const import *
import widget

class Spacer(widget.Widget):
	"""A invisible space.
	
	<pre>Spacer(width,height)</pre>
	
	"""
	def __init__(self,width,height,**params):
		params.setdefault('focusable',False)
		widget.Widget.__init__(self,width=width,height=height,**params)
		

class Color(widget.Widget):
	"""A block of color.
	
	<p>The color can be changed at run-time.</p>
	
	<pre>Color(value=None)</pre>
	
	<strong>Example</strong>
	<code>
	c = Color()
	c.value = (255,0,0)
	c.value = (0,255,0)
	</code>
	"""
	
	
	def __init__(self,value=None,**params):
		params.setdefault('focusable',False)
		if value != None: params['value']=value
		widget.Widget.__init__(self,**params)
	
	def paint(self,s):
		if hasattr(self,'value'): s.fill(self.value)
	
	def __setattr__(self,k,v):
		if k == 'value' and type(v) == str: v = pygame.Color(v)
		_v = self.__dict__.get(k,NOATTR)
		self.__dict__[k]=v
		if k == 'value' and _v != NOATTR and _v != v: 
			self.send(CHANGE)
			self.repaint()

class Label(widget.Widget):
	"""A text label.
	
	<pre>Label(value)</pre>
	
	<dl>
	<dt>value<dd>text to be displayed
	</dl>
	
	<strong>Example</strong>
	<code>
	w = Label(value="I own a rubber chicken!")
	
	w = Label("3 rubber chickens")
	</code>
	"""
	def __init__(self,value,**params):
		params.setdefault('focusable',False)
		params.setdefault('cls','label')
		widget.Widget.__init__(self,**params)
		self.value = value
		self.font = self.style.font
		self.style.width, self.style.height = self.font.size(self.value)
	
	def paint(self,s):
		s.blit(self.font.render(self.value, 1, self.style.color),(0,0))
	
	def __setattr__(self,k,v):
		_v = self.__dict__.get(k,NOATTR)
		self.__dict__[k]=v
		if k == 'value' and _v != NOATTR and _v != v: 
			self.send(CHANGE)
			self.repaint()

class WidthLabel(widget.Widget):
	def __init__(self,value, width, **params):
		params.setdefault('focusable',False)
		params.setdefault('cls','label')
		widget.Widget.__init__(self,**params)
		self.value = value
		self.font = self.style.font
		self.width= width;
		self.doLines(width);
		#dummyWidth, self.style.height = self.font.size(self.value)
		
	#def resize(self,width=None,height=None):
		#if (width != None) and (height != None):
		#	self.rect = pygame.Rect(self.rect.x, self.rect.y, width, height)
		#return self.rect.w, self.rect.h
	
	# Splits up the text found in the control's value, and assigns it into the lines array
	def doLines(self, max_line_w):
		self.style.width= max_line_w;
		self.line_h = 10 #this doesn't seem to have any purpose...
		self.lines = [] # Create an empty starter list to start things out.
		
		inx = 0
		line_start = 0
		while inx >= 0:
			# Find the next breakable whitespace
			# HACK: Find a better way to do this to include tabs and system characters and whatnot.
			prev_word_start = inx # Store the previous whitespace
			spc_inx = self.value.find(' ', inx+1)
			nl_inx = self.value.find('\n', inx+1)
			
			if (min(spc_inx, nl_inx) == -1):
				inx = max(spc_inx, nl_inx)
			else:
				inx = min(spc_inx, nl_inx)
				
			# Measure the current line
			lw, self.line_h = self.font.size( self.value[ line_start : inx ] )
			
			# If we exceeded the max line width, then create a new line
			if (lw > max_line_w):
				#Fall back to the previous word start
				self.lines.append(self.value[ line_start : prev_word_start + 1 ])
				line_start = prev_word_start + 1
				# TODO: Check for extra-long words here that exceed the length of a line, to wrap mid-word
				
			# If we reached the end of our text
			if (inx < 0):
				# Then make sure we added the last of the line
				if (line_start < len( self.value ) ):
					self.lines.append( self.value[ line_start : len( self.value ) ] )
			# If we reached a hard line break
			elif (self.value[inx] == "\n"):
				# Then make a line break here as well.
				newline = self.value[ line_start : inx + 1 ]
				newline = newline.replace("\n", " ") # HACK: We know we have a newline character, which doesn't print nicely, so make it into a space. Comment this out to see what I mean.
				self.lines.append( newline )
				
				line_start = inx + 1
			else:
				# Otherwise, we just continue progressing to the next space
				pass
		self.style.height= len(self.lines)* self.line_h;
	
	def paint(self,s):
		# Blit each of the lines in turn
		self.doLines(self.width);
		cnt = 0
		for line in self.lines:
			line_pos = (0, cnt  * self.line_h)
			if (line_pos[1] >= 0) and (line_pos[1] < self.rect.h):
				s.blit( self.font.render(line, 1, self.style.color), line_pos )
			cnt += 1
		#s.blit(self.font.render(self.value, 1, self.style.color),(0,0))
	
	def __setattr__(self,k,v):
		_v = self.__dict__.get(k,NOATTR)
		self.__dict__[k]=v
		if k == 'value' and _v != NOATTR and _v != v: 
			self.send(CHANGE)
			self.repaint()

class Image(widget.Widget):
	"""An image.
	
	<pre>Image(value)</pre>
	
	<dl>
	<dt>value<dd>a file name or a pygame.Surface
	</dl>
	
	"""
	def __init__(self,value,**params):
		params.setdefault('focusable',False)
		widget.Widget.__init__(self,**params)
		if type(value) == str: value = pygame.image.load(value).convert_alpha()
		
		ow,oh = iw,ih = value.get_width(),value.get_height()
		sw,sh = self.style.width,self.style.height
		
		if sw and not sh:
			iw,ih = sw,ih*sw/iw
		elif sh and not sw:
			iw,ih = iw*sh/ih,sh
		elif sw and sh:
			iw,ih = sw,sh
		
		if (ow,oh) != (iw,ih):
			value = pygame.transform.scale(value,(iw,ih))
		self.style.width,self.style.height = iw,ih
		self.value = value
	
	def kill(self):
		widget.Widget.kill(self);
		if self.value:
			self.value= None;
	
	def paint(self,s):
		s.blit(self.value,(0,0))