"""
"""
import pygame
from pygame.locals import *

from const import *
import widget

import sys, traceback;

from broadway import *;
import action, script;


class ScriptArea(widget.Widget):
	"""A multi-line text input designed to work with a Script
	
	<pre>TextRich(value="",width = 120, height = 30, size=20)</pre>
	
	<dl>
	<dt>value<dd>initial text
	<dt>size<dd>size for the text box, in characters
	</dl>
	
	<strong>Example</strong>
	<code>
	w = ScriptArea(value="Cuzco the Goat",size=20)
	
	w = ScriptArea("Marbles")
	
	w = ScriptArea("Groucho\nHarpo\nChico\nGummo\nZeppo\n\nMarx", 200, 400, 12)
	</code>
	
	"""
	def __init__(self,value="",width = 120, height = 30, size=20, script= None, **params):
		params.setdefault('cls','input')
		params.setdefault('width', width)
		params.setdefault('height', height)
		
		widget.Widget.__init__(self,**params)
		self.script= script				# The script associated with the TextRich
		self.value = value				# The value of the TextRich
		self.scriptMap= []				# Maps position to a CState
		self.pos = len(str(value))		# The position of the cursor
		self.posSelected = self.pos		# The stored end of the cursor (for text selection)
		self.changingSelection= False	# Whether or not the user is highlighting text
		self.haveSelection= False		# Whether or not the user is highlighting text
		self.vscroll = 0				# The number of lines that the TextRich is currently scrolled
		self.font = self.style.font		# The font used for rendering the text
		self.cursor_w = 2 				# Cursor width (NOTE: should be in a style)
		w,h = self.font.size("e"*size)
		self.charWidth, self.charHeight= self.font.size("e");
		if not self.style.height: self.style.height = h
		if not self.style.width: self.style.width = w
		self.refreshScript();
	
	def resize(self,width=None,height=None):
		if (width != None) and (height != None):
			self.rect = pygame.Rect(self.rect.x, self.rect.y, width, height)
		# HACK: A bizarre bug with the Select widget requires this to be minus 12 from both dimensions
		# I have no idea why, but otherwise the box continues to grow.
		# It only occurs when you CHANGE the currently selected option in a Select box.
		return self.rect.w-12, self.rect.h-12;
		
	def paint(self,s):
		
		# TODO: What's up with this 20 magic number? It's the margin of the left and right sides, but I'm not sure how this should be gotten other than by trial and error.
		max_line_w = self.rect.w - 20
				
		# Update the line allocation for the box's value
		self.doLines(max_line_w)
		
		# Make sure that the vpos and hpos of the cursor is set properly
		self.updateCursorPos()
		self.updateCursorPosSelected();

		# Make sure that we're scrolled vertically such that the cursor is visible
		if (self.vscroll < 0):
			self.vscroll = 0
		if (self.vpos < self.vscroll):
			self.vscroll = self.vpos
		elif ((self.vpos - self.vscroll + 1) * self.line_h > self.rect.h):
			self.vscroll = - (self.rect.h / self.line_h - self.vpos - 1)

		startLine= min(self.vpos, self.vposSelected);
		endLine= max(self.vpos, self.vposSelected);
		
		if startLine == endLine:
			startLinePos= min(self.hpos, self.hposSelected);
			endLinePos= max(self.hpos, self.hposSelected);
		elif self.vpos == startLine:
			startLinePos= self.hpos;
			endLinePos= self.hposSelected;
		else:
			startLinePos= self.hposSelected;
			endLinePos= self.hpos;

		# Blit each of the lines in turn
		currentLine = 0
		for line in self.lines:
			line_pos = (0, (currentLine - self.vscroll) * self.line_h)
			if (line_pos[1] >= 0) and (line_pos[1] < self.rect.h):
				if self.haveSelection:
					if startLine == currentLine:
						start= startLinePos
					else:
						start= 0;
					if endLine == currentLine:
						end= endLinePos;
					else:
						end= len(line);
					if startLine <= currentLine and currentLine <= endLine:
						x, ignore= self.font.size(line[0:start]);
						w, h= self.font.size(line[start:end]);
						s.fill(Color(150,150,255), Rect(x,line_pos[1], w,h));
				s.blit( self.font.render(line, 1, self.style.color), line_pos )
			currentLine += 1
		
		# If the TextRich is focused, then also show the cursor
		#if self.container.myfocus is self:
		r = self.getCursorRect()
		s.fill(self.style.color,r)
	
	# This function updates self.vpos and self.hpos based on self.pos
	def updateCursorPos(self):
		self.vpos = 0 # Reset the current line that the cursor is on
		self.hpos = 0
		
		line_cnt = 0
		char_cnt = 0

		for line in self.lines:
			line_char_start = char_cnt # The number of characters at the start of the line
			
			# Keep track of the character count for words
			char_cnt += len(line)
			
			# If our cursor count is still less than the cursor position, then we can update our cursor line to assume that it's at least on this line
			if (char_cnt > self.pos):
				self.vpos = line_cnt
				self.hpos = self.pos - line_char_start

				break # Now that we know where our cursor is, we exit the loop

			line_cnt += 1
		
		if (char_cnt <= self.pos) and (len(self.lines) > 0):
			self.vpos = len(self.lines) - 1
			self.hpos = len(self.lines[ self.vpos ] )
	
	# This function updates self.vposSelected and self.hposSelected based on self.posSelected
	def updateCursorPosSelected(self):
		self.vposSelected = 0 # Reset the current line that the cursor is on
		self.hposSelected = 0
		
		line_cnt = 0
		char_cnt = 0

		for line in self.lines:
			line_char_start = char_cnt # The number of characters at the start of the line
			
			# Keep track of the character count for words
			char_cnt += len(line)
			
			# If our cursor count is still less than the cursor position, then we can update our cursor line to assume that it's at least on this line
			if (char_cnt > self.posSelected):
				self.vposSelected = line_cnt
				self.hposSelected = self.posSelected - line_char_start

				break # Now that we know where our cursor is, we exit the loop

			line_cnt += 1
		
		if (char_cnt <= self.posSelected) and (len(self.lines) > 0):
			self.vposSelected = len(self.lines) - 1
			self.hposSelected = len(self.lines[ self.vposSelected ] )

	# Returns a rectangle that is of the size and position of where the cursor is drawn	
	def getCursorRect(self):
		lw = 0
		if (len(self.lines) > 0):
			lw, lh = self.font.size( self.lines[ self.vpos ][ 0:self.hpos ] )
			
		r = pygame.Rect(lw, (self.vpos - self.vscroll) * self.line_h, self.cursor_w, self.line_h)
		return r
	
	# This function sets the cursor position according to an x/y value (such as by from a mouse click)
	def setCursorByXY(self, (x, y)):
		self.vpos = ((int) (y / self.line_h)) + self.vscroll
		if (self.vpos >= len(self.lines)):
			self.vpos = len(self.lines) - 1
			
		try:
			currentLine = self.lines[ self.vpos ]
		except IndexError:
			currentLine = ''
		
		for cnt in range(0, len(currentLine) ):
			self.hpos = cnt
			lw, lh = self.font.size( currentLine[ 0:self.hpos + 1 ] )
			if (lw > x):
				break
		
		lw, lh = self.font.size( currentLine )
		if (lw < x):
			self.hpos = len(currentLine);
			
		self.setCursorByHVPos()
		
	# This function sets the cursor position by the horizontal/vertical cursor position.	
	def setCursorByHVPos(self):
		line_cnt = 0
		char_cnt = 0
		
		for line in self.lines:
			line_char_start = char_cnt # The number of characters at the start of the line
			
			# Keep track of the character count for words
			char_cnt += len(line)

			# If we're on the proper line
			if (line_cnt == self.vpos):
				# Make sure that we're not trying to go over the edge of the current line
				if ( self.hpos >= len(line) ):
					if line_char_start + self.hpos >= len(self.value):
						self.hpos = len(line);
					else:
						self.hpos = len(line) -1
				# Set the cursor position
				self.pos = line_char_start + self.hpos
				break	# Now that we've set our cursor position, we exit the loop
				
			line_cnt += 1
	
	# Splits up the text found in the control's value, and assigns it into the lines array
	def doLines(self, max_line_w):
		self.line_h = 10
		self.lines = [] # Create an empty starter list to start things out.
		
		i = 0
		line_start = 0
		while i >= 0:
			# Find the next breakable whitespace
			# HACK: Find a better way to do this to include tabs and system characters and whatnot.
			prev_word_start = i # Store the previous whitespace
			spc_inx = self.value.find(' ', i+1)
			nl_inx = self.value.find('\n', i+1)
			
			if (min(spc_inx, nl_inx) == -1):
				i = max(spc_inx, nl_inx)
			else:
				i = min(spc_inx, nl_inx)
				
			# Measure the current line
			lineWidth, self.line_h = self.font.size( self.value[ line_start : i ] )
			
			# If we exceeded the max line width, then create a new line
			if (lineWidth > max_line_w):
				#Fall back to the previous word start
				self.lines.append(self.value[ line_start : prev_word_start + 1 ].replace("\t"," "))
				line_start = prev_word_start + 1
				# TODO: Check for extra-long words here that exceed the length of a line, to wrap mid-word
				
			# If we reached the end of our text
			if (i < 0):
				# Then make sure we added the last of the line
				if (line_start < len( self.value ) ):
					self.lines.append( self.value[ line_start : len( self.value ) ].replace("\t"," ") )
			# If we reached a hard line break
			elif (self.value[i] == "\n"):
				# Then make a line break here as well.
				newline = self.value[ line_start : i + 1 ]
				newline = newline.replace("\n", " ") # HACK: We know we have a newline character, which doesn't print nicely, so make it into a space. Comment this out to see what I mean.
				newline = newline.replace("\t", " ") # HACK: We know we have a newline character, which doesn't print nicely, so make it into a space. Comment this out to see what I mean.
				self.lines.append( newline )
				
				line_start = i + 1
			else:
				# Otherwise, we just continue progressing to the next space
				pass
		
	def _setvalue(self,v):
		self.__dict__['value'] = v
		self.send(CHANGE)
	
	def __setattr__(self,k,v):
		if k == 'value':
			if v == None: v = ''
			v = str(v)
			self.pos = len(v)
		_v = self.__dict__.get(k,NOATTR)
		self.__dict__[k]=v
		if k == 'value' and _v != NOATTR and _v != v: 
			self.send(CHANGE)
			self.repaint()
		
	def avoidBrackets(self):
		open= self.value.rfind('[', 0, self.pos);
		close= self.value.rfind('\t', 0, self.pos);
		if open > close or (self.pos < len(self.value) and self.value[self.pos] == '['):
			close= self.value.find('\t', self.pos, len(self.value));
			self.pos= close+1;

	def avoidAngles(self):
		open= self.value.rfind('<', 0, self.pos);
		close= self.value.rfind('>', 0, self.pos);
		if open > close:
			close= self.value.find('>', self.pos, len(self.value));
			if self.pos - open < close - self.pos:
				self.pos= open;
			else:
				self.pos= close+1;
				
	def avoidTokensVertically(self):
		self.avoidBrackets();
		self.avoidAngles();
		
	def moveLeft(self):
		if self.pos <= 0:
			return;
		if self.value[self.pos-2:self.pos] == ']\t':
			prevLine= self.value.rfind('\n',0,self.pos-1);
			if prevLine != -1:
				self.pos= prevLine;
		elif self.value[self.pos-1] == '>':
			prevToken= self.value.rfind('<',0,self.pos-1);
			self.pos= prevToken;
		else:
			self.pos-= 1;
			
	def moveLeftFast(self):
		startLine = self.value.rfind(']', 0, self.pos)+2
		startWord= self.value.rfind(' ', 0, self.pos-2)+1;
		startAct= self.value.rfind('<', 0, self.pos-1);
		endAct= self.value.rfind('>', 0, self.pos-1)+1;
		if startAct < startWord and startWord < endAct:
			starts= [startLine, startAct, endAct];
		else:
			starts= [startLine, startWord, startAct, endAct];
		starts= filter(lambda x: x > 0 and x != self.pos, starts);
		if starts:
			self.pos= max(starts);
			
	def moveRight(self):
		if self.pos >= len(self.value):
			return;
		if self.value[self.pos] == '\n':
			nextLine= self.value.find(']\t',self.pos, len(self.value));
			if nextLine != -1:
				self.pos= nextLine+2;
		elif self.value[self.pos] == '<':
			nextToken= self.value.find('>', self.pos, len(self.value));
			self.pos= nextToken+1;
		else:
			self.pos+= 1;
			
	def moveRightFast(self):
		endLine = self.value.find('\n', self.pos, length+1);
		if endLine == -1:
			endLine= length;
		endWord= self.value.find(' ', self.pos, length+1)+1;
		startAct= self.value.find('<', self.pos, length+1);
		endAct= self.value.find('>', self.pos, length+1)+1;
		if startAct < endWord and endWord < endAct:
			starts= [endLine, startAct, endAct];
		else:
			starts= [endLine, endWord, startAct, endAct];
		starts= filter(lambda x: x > 0 and x != self.pos, starts);
		if starts:
			self.pos= min(starts);
			
	def avoidTokens(self, moused):
		actionStart= self.value.rfind('<',0, self.pos);
		actionEnd= self.value.rfind('>',0, self.pos);
		nameStart= self.value.rfind('[',0, self.pos);
		nameEnd= self.value.rfind(']',0,self.pos);
		if actionStart != -1:
			if actionStart >= actionEnd:
				self.pos= actionStart;
		if nameStart != -1:
			if nameStart >= nameEnd and nameEnd != -1:
				if moused:
					nameEnd= self.value.find(']', self.pos, len(self.value));
					self.pos= max(self.pos, nameEnd+2);
				else:
					self.pos= nameEnd+2;
			else:
				if nameEnd == -1:
					nameEnd= self.value.find(']', self.pos, len(self.value));
				self.pos= max(self.pos, nameEnd+2);
		else:
			self.pos= self.value.find(']')+2;
	
	def getTime(self, pos):
		if len(self.scriptMap) == 0:
			return 0;
		elif pos >= len(self.scriptMap):
			return self.scriptMap[-1]+1;
		else:
			return self.scriptMap[pos];
		
	def insertLetter(self, letter):
		pos= self.pos;
		time= self.getTime(pos);
		subject= self.script.getFocusedActor(time);
		newAction= action.Action(subject, verbs.SAY, letter);
		if self.isStartToken(pos) and self.isEndToken(pos):
			#Insert somewhere without speech
			self.insertData(pos, time, letter, newAction);
		else:
			#Insert at the end, middle, or beginning of speech
			begin, end= self.getTextRange(pos);
			beginText= self.value[begin:pos];
			endText= self.value[pos:end];
			text= "".join(beginText,letter,endText);
			textAction= action.Action(subject, verbs.SAY, text);
			time= self.getTime(begin);
			self.removeData(begin, end, time);
			self.insertData(begin, time, text, textAction);

	def isStartToken(self, pos):
		if pos >= len(self.value):
			return True;
		elif pos > 0 and pos < len(self.value):
			return self.value[pos] == '<' or self.value[pos] == '\n';
		else:
			return False;
			
	def isEndToken(self, pos):
		if pos > 0 and pos <= len(self.value):
			return self.value[pos-1] == '>' or self.value[pos-1] == '\t';
		else:
			return False;
	
	def printScriptMap(self):
		print "#"*60;
		k= 0;
		for aChar in self.value:
			print aChar, self.scriptMap[k], self.script.actions[self.scriptMap[k]];
			k+= 1;

	def changeCharacter(self, object):
		pos= self.pos;
		time= self.getTime(pos);
		oldAction= self.script.actions[time];
		oldSubject= self.script.getFocusedActor(time);
		newSubject= object.value;
		newAction= action.Action(newSubject, verbs.FOCUS, None);
		token= newAction.toText();
		if self.isStartToken(pos) or self.isEndToken(pos):
			self.insertData(pos, time, token, newAction);
			self.script.changeActor(time+1, newSubject);
		else:
			begin, end= self.getTextRange(pos);
			beginText= self.value[begin:pos];
			endText= self.value[pos:end];
			beginAction= Action(oldSubject, verbs.SAY, beginText);
			endAction= Action(oldSubject, verbs.SAY, endText);
			beginTime= self.getTime(begin);
			self.removeData(begin, end, beginTime);
			self.insertData(begin, beginTime, endText, endAction);
			self.insertData(begin, beginTime, token, newAction);
			self.insertData(begin, beginTime, beginText, beginAction);
			self.script.changeActor(time+2, newSubject);
		self.moveRight();
		self.updateState();

	def removeData(self, begin, end, time):
		self.script.removeAction(time);
		self.removeValue(begin, end);
		self.removeScriptMap(begin, time, end-begin);

	def insertData(self, pos, time, token, action):
		self.script.insertAction(action, time);
		self.insertValue(pos, token);
		self.insertScriptMap(pos, time, len(token));
	
	def insertScriptMap(self, pos, time, amount):
		for i in range(amount):
			self.scriptMap.insert(pos, time);
		end= len(self.scriptMap);
		i= pos;
		while i < end:
			self.scriptMap[i]+= 1;
			i+= 1;

	def removeScriptMap(self, pos, time, amount):
		for i in range(amount):
			self.scriptMap.pop(pos);
		end= len(self.scriptMap);
		if pos < end and self.scriptMap[pos] != time:
			i= pos;
			while i < end:
				self.scriptMap[i]-= 1;
				i+= 1;

	def insertValue(self, pos, newValue):
		self._setvalue("".join(self.value[:pos], newValue, self.value[pos:]));
	
	def removeValue(self, begin, end):
		self._setvalue("".join(self.value[:begin], self.value[end:]));
	
	def insertToken(self, verb, object):
		pos= self.pos;
		time= self.getTime(pos);
		subject= self.script.getFocusedActor(time);
		if type(object) is tuple or type(object) is str:
			newAction= action.Action(subject, verb, object);
		else:
			newAction= action.Action(subject, verb, object.value);
		actionText= newAction.toText();
		if self.isStartToken(pos) or self.isEndToken(pos):
			self.insertData(pos, time, actionText, newAction);
		else:
			begin, end= self.getTextRange(pos);
			beginText= self.value[begin:pos];
			endText= self.value[pos:end];
			beginAction= action.Action(subject, verbs.SAY, beginText);
			endAction= action.Action(subject, verbs.SAY, endText);
			beginTime= self.getTime(begin);
			self.removeData(begin, end, beginTime);
			self.insertData(begin, beginTime, endText, endAction);
			self.insertData(begin, beginTime, actionText, newAction);
			self.insertData(begin, beginTime, beginText, beginAction);
		self.moveRight();
		self.updateState();
		self.focus();
		return True;
	
	def deleteToken(self):
		pos= self.pos;
		time= self.getTime(pos);
		subject= self.script.getCharacter(time);
		length= len(self.value);
		if pos < length and self.value[pos] == '<':
			#If at the start of a <token>
			end= self.value.find('>',pos, length);
			self.removeData(pos, end+1, time);
			if not (self.isStartToken(pos) and self.isEndToken(pos)):
				#If we're not between two <token>s
				begin, end= self.getTextRange(pos);
				text= self.value[begin:end];
				time= self.getTime(begin);
				if text:
					textAction= action.Action(subject, verbs.SAY, text);
					if pos-begin > 0: #If there is text to remove on the left
						self.removeData(begin, pos, time);
					if end-pos > 0: #If there is text to remove on the right
						self.removeData(begin, end-(pos-begin), time);
					self.insertData(begin, time, text, textAction);
				else:
					self.removeData(begin, pos, time);
					self.removeData(begin, end-(pos-begin), time);
			#recombine two say statements if needed
		elif pos < length and self.value[pos] == '\n':
			#If at the end of a line (deleting a FOCUS)
			end= self.value.find('\t', pos, length);
			self.removeData(pos, end+1, time);
			time= self.getTime(pos)+1;
			if time <= self.scriptMap[-1]:
				#If we're not at the very end of the script
				newSubject= self.script.getFocusedCharacter(time);
				self.script.changeActor(subject, time);
			if not (self.isStartToken(pos) and self.isEndToken(pos)):
				#If 
				begin, end= self.getTextRange(pos);
				text= self.value[begin:end];
				time= self.getTime(begin);
				if text:
					textAction= Action(subject=subject, verb=Action.SAY, objects=text);
					if pos-begin >0: #If there is text to remove on the left
						self.removeData(begin, pos, time);
					if end-pos > 0: #If there is text to remove on the right
						self.removeData(begin, end-(pos-begin), time);
					self.insertData(begin, time, text, textAction);
				else:
					self.removeData(begin, pos, time);
					self.removeData(begin, end-(pos-begin), time);
		else:
			begin, end= self.getTextRange(pos);
			beginText= self.value[begin:pos];
			endText= self.value[pos+1:end];
			text= beginText+endText;
			if text:
				textAction= Action(subject=subject, verb=Action.SAY, objects=text);
				time= self.getTime(begin);
				self.removeData(begin, end, time);
				self.insertData(begin, time, text, textAction);
			else:
				time= self.getTime(begin);
				self.removeData(begin, end, time);
			
	def getTextRange(self, position):
		preTextC= self.value.rfind('>', 0, position)+1;
		preTextB= self.value.rfind('\t', 0, position)+1;
		preText= max(preTextB, preTextC);
		postTextC= self.value.find('<', position, len(self.value));
		postTextB= self.value.find('\n', position, len(self.value));
		if postTextB == -1:
			postTextB= len(self.value);
		if postTextC == -1:
			postTextC= len(self.value);
		postText= min(postTextB, postTextC);
		return preText, postText;
		
	def getStateTime(self, position= None):
		if position == None:
			position= self.pos;
		if position >= len(self.value):
			statePos= self.scriptMap[-1];
		else:
			statePos= self.scriptMap[position]-1;
		return statePos;
		
	def updateState(self):
		self.script.setCStates(self.getStateTime());
		
	def speakerChange(self, position):
		if position >= 0 and position < len(self.value):
			time= self.getStateTime(position);
			action= self.script.actionList[time];
			return action.verb == Action.FOCUS;
		else:
			return False;
			
	def validBackspaceable(self):
		# Not at first speaker, unless there are other speakers afterwards
		if self.atStart():
			if self.beforeEnd() and self.speakerChange(self.pos+1):
				return True;
			else:
				return False;
		else:
			return not self.beforeStart();
			
	def validDeletable(self):
		# Not at very end
		return self.beforeEnd();
		
	def validInsertable(self):
		# Not before first speaker
		return not self.beforeStart();
		
	def validLocation(self):
		# Not before first speaker
		return not self.beforeStart();
		
	def atStart(self):
		return self.pos == self.value.find('\t')+1;
		
	def beforeStart(self):
		return self.pos < self.value.find('\t')+1;
	
	def afterStart(self):
		return self.pos > self.value.find('\t')+1;
	
	def beforeEnd(self):
		return self.pos < len(self.value);
		
	def moveToStart(self):
		self.pos= self.value.find('\t')+1;
		
	def event(self,e):
		used = None
		if e.type == KEYDOWN:	
			mods= pygame.key.get_mods();
			self.changingSelection= mods & KMOD_SHIFT;
			
			if self.changingSelection and not self.haveSelection:
				self.haveSelection= True;
				self.posSelected= self.pos;
			
			length= len(self.value);
			
			if e.key == K_BACKSPACE:
				if self.haveSelection:
					self.posSelected,self.pos= sorted([self.pos, self.posSelected]);
					while self.posSelected < self.pos:
						self.moveLeft();
						self.deleteToken();
					self.updateState();
				#Ensure we're not beginning the first line
				elif self.validBackspaceable():
					self.moveLeft();
					self.deleteToken();
					self.updateState();
					if self.beforeStart():
						self.moveToStart();
			elif e.key == K_DELETE:
				if self.haveSelection:
					self.posSelected,self.pos= sorted([self.pos, self.posSelected]);
					while self.posSelected < self.pos:
						self.moveLeft();
						self.deleteToken();
					self.updateState();
				#elif self.pos < len(self.value):
				elif self.validDeletable():
					self.deleteToken();
					self.updateState();
			elif e.key == K_HOME: 
				# Find the previous newline
				self.pos = self.value.rfind(']', 0, self.pos)+2
				self.updateState();
			elif e.key == K_END:
				# Find the previous newline
				newPos = self.value.find('\n', self.pos, len(self.value) )
				if (newPos >= 0):
					self.pos = newPos
				if newPos == -1:
					self.pos= len(self.value);
				self.updateState();
			elif e.key == K_LEFT:
				if self.afterStart():
					if mods & KMOD_CTRL:
						self.moveLeftFast();
						self.avoidTokens(False);
					else:
						self.moveLeft();
					self.updateState();
					used= True;
			elif e.key == K_RIGHT:
				if mods & KMOD_CTRL:
					self.moveRightFast();
					self.avoidTokens(False);
				else:
					self.moveRight();
				self.updateState();
				used = True
			elif e.key == K_UP:
				self.vpos -= 1
				self.setCursorByHVPos()
				self.avoidTokensVertically();
				if self.beforeStart():
					self.moveToStart();
				self.updateState();
			elif e.key == K_DOWN:
				self.vpos += 1
				self.setCursorByHVPos()
				self.avoidTokensVertically();
				self.updateState();
			elif e.key == K_PAGEUP:
				self.vpos -= 5;
				self.setCursorByHVPos()
				self.avoidTokensVertically();
				if self.beforeStart():
					self.moveToStart();
				self.updateState();
			elif e.key == K_PAGEDOWN:
				self.vpos += 5;
				self.setCursorByHVPos()
				self.avoidTokensVertically();
				self.updateState();
			else:
				#c = str(e.unicode)
				try:
					if (e.key == K_RETURN):
						#c = "\n"
						c= '';
					elif (e.key == K_TAB):
						c= '';
						#print "*"*50;
						#print self.script.printDetailed();
						#c = "  "
					elif (e.key == K_F1):
						print "*"*50;
						print self.printScriptMap();
					else:
						c = (e.unicode).encode('latin-1')
					if c in ['[',']','<','>']:
						c= '';
					if c:
						#self._setvalue(self.value[:self.pos] + c + self.value[self.pos:])
						self.insertLetter(c);
						self.pos += len(c)
				except: #ignore weird characters
					pass
					
			if not self.changingSelection and self.haveSelection:
				#print "left shift released"
				self.haveSelection= False;
				
			self.repaint()
			
		elif e.type == MOUSEBUTTONDOWN:
			self.setCursorByXY(e.pos)
			self.avoidTokensVertically();
			if self.beforeStart():
				self.moveToStart();
			self.repaint()
			self.updateState();
		elif e.type == MOUSEBUTTONUP:
			mods= pygame.key.get_mods();
			self.haveSelection= mods & KMOD_SHIFT;
		elif e.type == FOCUS:
			self.repaint()
		elif e.type == BLUR:
			self.repaint()
		
		self.pcls = ""
		if self.container.myfocus is self: self.pcls = "focus"
		
		return used
	
	def refreshScript(self):
		if self.script is not None:
			self.value, self.scriptMap= self.script.toString();
			self.pos= self.value.find('\t')+1;
		else:
			self.value= "";
			self.scriptMap= [];
			
# The first version of this code was done by Clint Herron, and is a modified version of input.py (by Phil Hassey).
# It is under the same license as the rest of the PGU library.
