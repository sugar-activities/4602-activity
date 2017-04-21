"""
"""

import simplejson as json;

import random

import pygame
from pygame.locals import *

from constants import *
import pgu.gui.widget as widget
from pgu import gui;

import sys, traceback;

from constants import *;
import action, script, actor;

#_ = lambda x: x


class ScriptArea(widget.Widget):
    """A multi-line text input specifically designed to work with a Script
    Based on the TextArea Widget.
    
    TextRich(script, value="",width = 120, height = 30, size=20)
    """
    def __init__(self,script, value="",width = 120, height = 30, **params):
        """
        Initializes the *ScriptArea*
        
        | *script* the *Script* object that this script modifies.
        | *value* the initial string that is displayed in the ScriptArea.
        This is probably legacy data.
        | *width* the pixel width of the scriptarea (don't forget padding!)
        | *height* the pixel height of the scriptarea (don't forget padding!)
        """
        size=20
        
        params.setdefault('cls','input')
        params.setdefault('width', width)
        params.setdefault('height', height)
        
        widget.Widget.__init__(self,**params)
        self.script= script                   # The script associated with the TextRich
        self.value = value                   # The value of the TextRich
        self.scriptMap= []                   # Maps position to a CState
        self.pos = len(str(value))           # The position of the cursor
        self.posSelected = self.pos           # The stored end of the cursor (for text selection)
        self.changingSelection= False       # Whether or not the user is highlighting text
        self.haveSelection= False           # Whether or not the user is highlighting text
        self.vscroll = 0                   # The number of lines that the TextRich is currently scrolled
        self.font = self.style.font           # The font used for rendering the text
        self.cursor_w = 2                    # Cursor width (NOTE: should be in a style)
        self.linesBlitted= []               # How many lines have been drawn to the screen
        w,h = self.font.size("e"*size)
        self.charWidth, self.charHeight= self.font.size("e");
        if not self.style.height: self.style.height = h
        if not self.style.width: self.style.width = w
        self.refreshScript();
        self.shiftWasDown = pygame.key.get_mods() & gui.KMOD_SHIFT
        
        self.scrollWidth= 16;
    
    #def resize(self,width=None,height=None):
    #    if (width != None) and (height != None):
    #        self.rect = pygame.Rect(self.rect.x, self.rect.y, width, height)
        # HACK: A bizarre bug with the Select widget requires this to be minus 12 from both dimensions
        # I have no idea why, but otherwise the box continues to grow.
        # It only occurs when you CHANGE the currently selected option in a Select box.
    #    return self.rect.w-12, self.rect.h-12;
        
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
        self.linesBlitted= [];
        for line in self.lines:
            line_pos = (self.scrollWidth, (currentLine - self.vscroll) * self.line_h)
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
                        x+= self.scrollWidth;
                        w, h= self.font.size(line[start:end]);
                        s.fill((150,150,255), Rect(x,line_pos[1], w,h));
                s.blit( self.font.render(line, 1, self.style.color), line_pos )
                self.linesBlitted.append(currentLine);
            currentLine += 1
        
        # Draw the scrollbar
        self.drawScrollBar(s);
        
        # If the TextRich is focused, then also show the cursor
        #if self.container.myfocus is self:
        r = self.getCursorRect()
        s.fill(self.style.color,r)
    
    def getScrollRect(self):
        startLine= min(self.linesBlitted);
        endLine= max(self.linesBlitted);
        linesLength= (endLine - startLine) + 1;
        if self.lines:
            heightRatio= linesLength * self.rect.h / float(len(self.lines));
            y= startLine * self.rect.h / float(len(self.lines)) ;
        else:
            y= 0;
            heightRatio= 1;
        x,y = (0,y);
        w,h = (self.scrollWidth, heightRatio);
        return Rect(x,y,w,h)
    
    def drawScrollBar(self, s):
        if self.linesBlitted:
            r= self.getScrollRect()
            s.fill((150,150,150), r);
    
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
        
        lw+= self.scrollWidth;
        r = pygame.Rect(lw, (self.vpos - self.vscroll) * self.line_h, self.cursor_w, self.line_h)
        return r
    
    # This function sets the cursor position according to an x/y value (such as by from a mouse click)
    def setCursorByXY(self, (x, y)):
        x-= self.scrollWidth;
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
                break    # Now that we've set our cursor position, we exit the loop
                
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
                newline = newline.replace("\t", " ") # HACK: Same with tabs
                self.lines.append( newline )
                
                line_start = i + 1
            else:
                # Otherwise, we just continue progressing to the next space
                pass
        
    def _setvalue(self,v):
        self.__dict__['value'] = v
        self.send(gui.CHANGE)
    
    def __setattr__(self,k,v):
        if k == 'value':
            if v == None: v = ''
            v = str(v)
            self.pos = len(v)
        _v = self.__dict__.get(k,gui.NOATTR)
        self.__dict__[k]=v
        if k == 'value' and _v != gui.NOATTR and _v != v: 
            self.send(gui.CHANGE)
            self.repaint()
        
    def avoidBrackets(self):
        """
        Forces the current position to move to the closest spot not enclosed
        by brackets ("[]")
        """
        open= self.value.rfind('[', 0, self.pos);
        close= self.value.rfind('\t', 0, self.pos);
        if open > close or (self.pos < len(self.value) and self.value[self.pos] == '['):
            close= self.value.find('\t', self.pos, len(self.value));
            self.pos= close+1;

    def avoidAngles(self):
        """
        Forces the current position to move to the closest spot not enclosed
        by angle brackets ("<>")
        """
        open= self.value.rfind('<', 0, self.pos);
        close= self.value.rfind('>', 0, self.pos);
        if open > close:
            close= self.value.find('>', self.pos, len(self.value));
            if self.pos - open < close - self.pos:
                self.pos= open;
            else:
                self.pos= close+1;
                
    def avoidCuesVertically(self):
        """
        Move the cursor to a spot that is not enclosed by either angle or
        regular brackets.
        """
        self.avoidBrackets();
        self.avoidAngles();
        
    def moveLeft(self):
        """
        Move the cursor one space left, wrapping it around the line if needed,
        and avoiding any acts if needed.
        """
        if self.pos <= 0:
            return;
        if self.value[self.pos-2:self.pos] == ']\t':
            prevLine= self.value.rfind('\n',0,self.pos-1);
            if prevLine != -1:
                self.pos= prevLine;
        elif self.value[self.pos-1] == '>':
            prevCue= self.value.rfind('<',0,self.pos-1);
            self.pos= prevCue;
        else:
            self.pos-= 1;
            
    def moveLeftFast(self):
        """
        Move the cursor to the first space it finds to the left, skipping any
        acts or newlines.
        """
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
            nextLine= self.value.find('\t',self.pos, len(self.value));
            if nextLine != -1:
                self.pos= nextLine+1;
        elif self.value[self.pos] == '<':
            nextCue= self.value.find('>', self.pos, len(self.value));
            self.pos= nextCue+1;
        else:
            self.pos+= 1;
            
    def moveRightFast(self):
        length= len(self.value);
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
            
    def avoidCues(self, moused):
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
    
    def getTimeForDelete(self, pos):
        if len(self.scriptMap) == 0:
            return 0;
        elif pos >= len(self.scriptMap):
            return self.scriptMap[-1]+1;
        else:
            return self.scriptMap[pos];
    
    def getTimeForInsert(self, pos):
        if len(self.scriptMap) == 0:
            return 0;
        elif pos >= len(self.scriptMap):
            return self.scriptMap[-1];
        else:
            return self.scriptMap[pos-1];
        
    def insertString(self, text):
        pos= self.pos;
        self.pos+= len(text);
        time= self.getTimeForInsert(pos);
        subject= self.script.getFocusedActor(time);
        if self.isNoSpeech(pos):
            #Insert somewhere without speech
            newAction= action.Action(subject, verbs.SAY, text);
            self.insertData(pos, time+1, text, newAction);
        else:
            #Insert at the end, middle, or beginning of speech
            begin, end= self.getTextRange(pos);
            beginText= self.value[begin:pos];
            endText= self.value[pos:end];
            text= beginText + text + endText;
            textAction= action.Action(subject, verbs.SAY, text);
            time= self.getTimeForDelete(begin);
            self.removeData(begin, end, time);
            self.insertData(begin, time, text, textAction);
        
    def insertLetter(self, letter):
        pos= self.pos;
        time= self.getTimeForInsert(pos);
        subject= self.script.getFocusedActor(time);
        if self.isNoSpeech(pos):
            #Insert somewhere without speech
            newAction= action.Action(subject, verbs.SAY, letter);
            self.insertData(pos, time+1, letter, newAction);
        else:
            #Insert at the end, middle, or beginning of speech
            begin, end= self.getTextRange(pos);
            beginText= self.value[begin:pos];
            endText= self.value[pos:end];
            text= beginText + letter + endText;
            textAction= action.Action(subject, verbs.SAY, text);
            time= self.getTimeForDelete(begin);
            self.removeData(begin, end, time);
            self.insertData(begin, time, text, textAction);
    
    def isStartCue(self, pos):
        ''' If we are at the start of a Cue, followed by a cue.
            pos is safe. '''
        if self.isBeforeEnd(pos):
            this= self.value[pos];
            return this in ['<','\n'];
    def isStartSpeech(self, pos):
        ''' If we are the first letter of a speech, followed by a cue.
            pos is safe. '''
        if self.isBeforeEnd(pos):
            this= self.value[pos];
            if this not in ['<','>','\n','\t']:
                previous= self.value[pos-1];
                return previous in ['>', '\t'];
        else:
            return False;
    def isEndSpeech(self, pos):
        ''' If we are the last letter of a speech, followed by a cue.
            pos is safe. '''
        if self.isBeforeEnd(pos):
            this= self.value[pos];
            if this in ['<', '\n']:
                previous= self.value[pos-1];
                return previous not in ['<','>','\n','\t'];
            else:
                return False;
        else:
            if self.isBeforeEnd(previous):
                previous= self.value[pos-1];
                return previous not in ['<','>','\n','\t'];
            else:
                return False;
                
    def isMiddleSpeech(self, pos):
        ''' If we are in the middle of a speech. That is, there is speech on
            both sides of it.
            pos is safe. '''
        if self.isBeforeEnd(pos):
            this= self.value[pos];
            if this not in ['<','>','\n','\t']:
                previous= self.value[pos-1];
                return previous not in ['<', '>', '\n', '\t'];
        return False;
    def isNoSpeech(self, pos):
        ''' If we are not in the middle, the end, or the start of a speech.
            That is, there are cues on either side.
            pos is safe. '''
        if self.isBeforeEnd(pos):
            this= self.value[pos];
            if this in ['<','\n']:
                previous= self.value[pos-1];
                return previous in ['>', '\t'];
            else:
                return False;
        else:
            previous= self.value[pos-1];
            return previous in ['>', '\t'];
    
    def isBeforeEnd(self, pos):
        return pos < len(self.value);
    
    def printScriptMap(self):
        print "#"*60;
        k= 0;
        for aChar in self.value:
            if aChar == '\t':
                aChar= '->';
            if aChar == '\n':
                aChar= '#';
            if k >= len(self.scriptMap):
                print k, aChar, "outside of scriptMap";
            elif self.scriptMap[k] >= len(self.script.actions):
                print k, aChar, self.scriptMap[k], "outside of actions";
            else:
                print k, aChar, self.scriptMap[k], str(self.script.actions[self.scriptMap[k]]);
            k+= 1;
        print "#"*60;

    def changeActor(self, newSubject):
        pos= self.pos;
        time= self.getTimeForInsert(pos);
        oldSubject= self.script.getFocusedActor(time);
        if type(newSubject) is not actor.Actor:
            newSubject= newSubject.value;
        newAction= action.Action(newSubject, verbs.FOCUS, None);
        cue= newAction.toText();
        if self.isMiddleSpeech(pos):
            #get text range
            begin, end= self.getTextRange(pos);
            beginText= self.value[begin:pos];
            endText= self.value[pos:end];
            beginAction= action.Action(oldSubject, verbs.SAY, beginText);
            endAction= action.Action(oldSubject, verbs.SAY, endText);
            beginTime= self.getTimeForDelete(begin);
            # remove old text, add in first part, change, and second part
            self.removeData(begin, end, beginTime);
            self.insertData(begin, beginTime, endText, endAction);
            self.insertData(begin, beginTime, cue, newAction);
            self.insertData(begin, beginTime, beginText, beginAction);
            self.script.changeActor(beginTime, newSubject);
        else:
            self.insertData(pos, time+1, cue, newAction);
            self.script.changeActor(time+2, newSubject);
        self.moveRight();
        self.updateState();

    def removeData(self, begin, end, time):
        self.script.removeAction(time);
        self.removeValue(begin, end);
        self.removeScriptMap(begin, time, end-begin);

    def insertData(self, pos, time, cue, newAction):
        self.script.insertAction(newAction, time);
        self.insertValue(pos, cue);
        self.insertScriptMap(pos, time, len(cue));
    
    def insertScriptMap(self, pos, time, amount):
        for i in range(amount):
            self.scriptMap.insert(pos, time);
        end= len(self.scriptMap);
        i= pos+amount;
        while i < end:
            self.scriptMap[i]+= 1;
            i+= 1;

    def removeScriptMap(self, pos, time, amount):
        for i in range(amount):
            self.scriptMap.pop(pos);
        end= len(self.scriptMap);
        i= pos;
        while i < end:
            self.scriptMap[i]-= 1;
            i+= 1;

    def insertValue(self, pos, newValue):
        self._setvalue(self.value[:pos] + newValue + self.value[pos:]);
    
    def removeValue(self, begin, end):
        self._setvalue(self.value[:begin] + self.value[end:]);
    
    def insertCue(self, verb, object):
        pos= self.pos;
        time= self.getTimeForInsert(pos);
        subject= self.script.getFocusedActor(time);
        newAction= action.Action(subject, verb, object);
        cueText= newAction.toText();
        if not self.isMiddleSpeech(pos):
            self.insertData(pos, time+1, cueText, newAction);
        else:
            begin, end= self.getTextRange(pos);
            beginText, endText = self.value[begin:pos], self.value[pos:end];
            beginAction= action.Action(subject, verbs.SAY, beginText);
            endAction= action.Action(subject, verbs.SAY, endText);
            beginTime= self.getTimeForDelete(begin);
            self.removeData(begin, end, beginTime);
            self.insertData(begin, beginTime, endText, endAction);
            self.insertData(begin, beginTime, cueText, newAction);
            self.insertData(begin, beginTime, beginText, beginAction);
        self.moveRight();
        self.updateState();
        self.focus();
        return True;
    
    def backspaceCue(self):
        """Returns true if it deleted a CUE, else False if it deleted a Letter or nothing."""
        if self.atStart():
            if self.beforeEnd():
                if self.speakerChange(self.pos):
                    self.removeData(0,self.pos+1, 0);
                    self.pos= self.value.find('\t')+1;
                    return True;
        else:
            self.moveLeft();
            return self.deleteCue();
        return False;
    
    def deleteCue(self):
        """Returns true if it deleted a CUE, else False if it deleted a Letter or nothing."""
        pos= self.pos;
        time= self.getTimeForDelete(pos);
        subject= self.script.getFocusedActor(time);
        length= len(self.value);
        if self.isStartCue(pos): #Cue
            if self.value[pos] == '\n': #FOCUS
                end= self.value.find('\t', pos, length)+1;
                insertTime= self.getTimeForInsert(pos);
                newSubject= self.script.getFocusedActor(insertTime);
                self.removeData(pos, end, time);
                if self.isBeforeEnd(pos): #Give any other actions to this actor
                    self.script.changeActor(time, newSubject);
            else: #non-FOCUS
                end= self.value.find('>',pos, length)+1;
                self.removeData(pos, end, time);
            if self.isMiddleSpeech(pos):
                #Recombine stray speeches
                begin, end= self.getTextRange(pos);
                time= self.getTimeForDelete(begin);
                text= self.value[begin:end];
                textAction= action.Action(subject, verbs.SAY, text);
                self.removeData(begin, pos, time);
                self.removeData(begin, end-(pos-begin), time);
                self.insertData(begin, time, text, textAction);
            return True;
        elif self.isBeforeEnd(pos): #Letter
            begin, end= self.getTextRange(pos);
            beginText= self.value[begin:pos];
            endText= self.value[pos+1:end]; #skip the letter at pos
            text= beginText+endText;
            time= self.getTimeForDelete(begin);
            if text:
                #There is some text
                textAction= action.Action(subject, verbs.SAY, text);
                self.removeData(begin, end, time);
                self.insertData(begin, time, text, textAction);
            else:
                self.removeData(begin, end, time);
            return False;
        else:
            print "D'oh";
            return False;
            
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
        """Updates all the controls that are attached to the script based
        on the current postion of the cursor."""
        controls= self.script.controls;
        time= self.getTimeForDelete(self.pos);
        subject= self.script.getFocusedActor(time);
        subjectThatJustActed= self.script.getFocusedActor(time-1);
        self.script.setFrame(time);
        if 'write-group-focus' in controls:
            if controls['write-group-focus'].value != subjectThatJustActed:
                controls['write-group-focus'].change(subjectThatJustActed);
                self.container().killSelectablesDocument();
                self.container().buildSelectablesDocument();
        if 'write-select-pose' in controls:
            controls['write-select-pose'].value= subject.state.pose;
        if 'write-select-look' in controls:
            controls['write-select-look'].value= subject.state.look;
        if 'write-button-direction-' in controls:
            controls['write-button-direction-'].value= subject.state.direction;
        if 'write-label-position' in controls:
            controls['write-label-position'].value= getMoveString(subject.state.position);
        
    def speakerChange(self, pos):
        ''' Returns if there is a speaker change at this position. 
            pos is unsafe '''
        time= self.getTimeForDelete(pos);
        if time >= 0 and time <= self.scriptMap[-1]:
            newAction= self.script.actions[time];
            return newAction.verb == verbs.FOCUS;
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
    
    def getActionStart(self, pos):
        """Returns the start index of this speech."""
        this= self.value[pos-1];
        if (this in ['>','\t','\n','<']) or pos == len(self.value):
            return pos;
        else:
            preTextC= self.value.rfind('>', 0, pos)+1;
            preTextB= self.value.rfind('\t', 0, pos)+1;
            preText= max(preTextB, preTextC);
            return preText;
    def getActionEnd(self, pos):
        """Returns the end index of this speech."""
        this= self.value[pos-1];
        if (this in ['\n','<']) or pos == len(self.value):
            return pos;
        else:
            postTextC= self.value.find('<', pos, len(self.value));
            postTextB= self.value.find('\n', pos, len(self.value));
            if postTextB == -1:
                postTextB= len(self.value);
            if postTextC == -1:
                postTextC= len(self.value);
            postText= min(postTextB, postTextC);
            return postText;
    
    def getSelectedTime(self):
        if self.haveSelection:
            start, end= sorted([self.pos, self.posSelected]);
            start= self.getActionStart(start);
            end= self.getActionEnd(end);
            return self.getTimeForInsert(start), self.getTimeForInsert(end);
        else:
            start= self.getActionStart(self.pos);
            return self.getTimeForInsert(start), self.getTimeForInsert(start);
    
    def getEndTime(self):
        return self.getTimeForDelete(len(self.value));
    
    moveKeys = frozenset((gui.K_UP, gui.K_DOWN, gui.K_LEFT, gui.K_RIGHT,
                          gui.K_HOME, gui.K_END, gui.K_PAGEUP, gui.K_PAGEDOWN,
                          gui.K_NUMLOCK, gui.K_CAPSLOCK, gui.K_SCROLLOCK,
                          gui.K_RSHIFT, gui.K_LSHIFT, gui.K_RCTRL, gui.K_LCTRL,
                          gui.K_RALT, gui.K_LALT, gui.K_RMETA, gui.K_LMETA,
                          gui.K_LSUPER, gui.K_RSUPER, gui.K_MODE))
    
    def event(self,e):
        used = None
        if e.type == gui.KEYDOWN:    
            mods = pygame.key.get_mods()
            shiftIsDown= mods & gui.KMOD_SHIFT
            shiftClicked = not self.shiftWasDown and shiftIsDown
            shiftUnclicked = self.shiftWasDown and not shiftIsDown;
            self.shiftWasDown = shiftIsDown
            
            # if shift was clicked, we have a selection
            if shiftClicked:
                self.posSelected = self.pos
                self.haveSelection = True
            
            if shiftIsDown and not self.haveSelection and e.key in ScriptArea.moveKeys:
                self.posSelected = self.pos
                self.haveSelection = True
            
            if e.key == gui.K_BACKSPACE:
                if self.haveSelection:
                    self.posSelected,self.pos= sorted([self.pos, self.posSelected]);
                    self.script.scriptChanged();
                    while self.posSelected < self.pos:
                        self.moveLeft();
                        self.deleteCue();
                    self.updateState();
                # Delete more than one if you need
                if mods & gui.KMOD_CTRL:
                    self.posSelected = self.pos
                    self.moveLeftFast();
                    self.avoidCues(False);
                    self.posSelected,self.pos= sorted([self.pos, self.posSelected]);
                    self.script.scriptChanged();
                    while self.posSelected < self.pos:
                        self.moveLeft();
                        self.deleteCue();
                    self.updateState();
                #Ensure we're not beginning the first line
                elif self.validBackspaceable():
                    isCue= self.backspaceCue();
                    self.script.scriptChanged();
                    #Note: Updating the state is expensive, 
                    # only do so if we affected a cue
                    if isCue: 
                        self.updateState();
                    if self.beforeStart():
                        self.moveToStart();
            elif e.key == gui.K_DELETE:
                if self.haveSelection:
                    self.posSelected,self.pos= sorted([self.pos, self.posSelected]);
                    while self.posSelected < self.pos:
                        self.moveLeft();
                        self.deleteCue();
                    self.script.scriptChanged();
                    self.updateState();
                elif mods & gui.KMOD_CTRL:
                    self.posSelected = self.pos
                    self.moveRightFast();
                    self.avoidCues(False);
                    self.posSelected,self.pos= sorted([self.pos, self.posSelected]);
                    while self.posSelected < self.pos:
                        self.moveLeft();
                        self.deleteCue();
                    self.script.scriptChanged();
                    self.updateState();
                #elif self.pos < len(self.value):
                elif self.validDeletable():
                    isCue= self.deleteCue();
                    self.script.scriptChanged();
                    if isCue:
                        self.updateState();
            elif e.key == gui.K_HOME: 
                # Find the home
                if mods & gui.KMOD_CTRL:
                    self.pos = self.value.find(']', 0, self.pos)+2
                # Find the previous newline
                else:
                    self.pos = self.value.rfind(']', 0, self.pos)+2
                self.updateState();
            elif e.key == gui.K_END:
                # Find the end
                if mods & gui.KMOD_CTRL:
                    self.pos= len(self.value);
                # Find the previous newline
                else:
                    newPos = self.value.find('\n', self.pos, len(self.value) )
                    if (newPos >= 0):
                        self.pos = newPos
                    if newPos == -1:
                        self.pos= len(self.value);
                self.updateState();
            elif e.key == gui.K_LEFT:
                if self.afterStart():
                    if mods & gui.KMOD_CTRL:
                        self.moveLeftFast();
                        self.avoidCues(False);
                    else:
                        self.moveLeft();
                    self.updateState();
                    used= True;
            elif e.key == gui.K_RIGHT:
                if mods & gui.KMOD_CTRL:
                    self.moveRightFast();
                    self.avoidCues(False);
                else:
                    self.moveRight();
                self.updateState();
                used = True
            elif e.key == gui.K_UP:
                self.vpos -= 1
                self.setCursorByHVPos()
                self.avoidCuesVertically();
                if self.beforeStart():
                    self.moveToStart();
                self.updateState();
            elif e.key == gui.K_DOWN:
                self.vpos += 1
                self.setCursorByHVPos()
                self.avoidCuesVertically();
                self.updateState();
            elif e.key == gui.K_PAGEUP:
                self.vpos -= 5;
                self.setCursorByHVPos()
                self.avoidCuesVertically();
                if self.beforeStart():
                    self.moveToStart();
                self.updateState();
            elif e.key == gui.K_PAGEDOWN:
                self.vpos += 5;
                self.setCursorByHVPos()
                self.avoidCuesVertically();
                self.updateState();
            else:
                #c = str(e.unicode)
                try:
                    if (e.key == gui.K_RETURN):
                        otherActors = self.script.actors[:]
                        pos= self.pos;
                        time= self.getTimeForInsert(pos);
                        currentActor = self.script.getFocusedActor(time);
                        otherActors.remove(currentActor)
                        if otherActors:
                            self.changeActor(random.choice(otherActors))
                            self.updateState()
                            self.script.scriptChanged();
                        c= '';
                    elif (e.key == gui.K_TAB):
                        c= '';
                    else:
                        c = (e.unicode).encode('latin-1')
                    if c in ['[',']','<','>']:
                        c= '';
                    if c:
                        if self.haveSelection:
                            self.posSelected,self.pos= sorted([self.pos, self.posSelected]);
                            while self.posSelected < self.pos:
                                self.moveLeft();
                                self.deleteCue();
                            self.updateState();
                        self.insertLetter(c);
                        self.pos += len(c)
                        self.script.scriptChanged();
                except Exception, e: #ignore weird characters
                    print e;
            
            # shift is up and we're not pressing the shift key
            if self.haveSelection:
                if (shiftIsDown and e.key not in ScriptArea.moveKeys) or not shiftIsDown:
                    self.haveSelection = False
                    
            self.repaint()
            
        elif e.type == gui.MOUSEBUTTONDOWN:
            # Handle any scrolling as necessary
            if e.pos[0] < self.scrollWidth:
                x,y,w,h = self.getScrollRect()
                if e.pos[1] < y:
                    self.vpos -= 10;
                elif e.pos[1] > y+h:
                    self.vpos += 10;
                self.setCursorByHVPos()
            # Otherwise just use the mouse location
            else:
                self.setCursorByXY(e.pos)
                if not self.haveSelection:
                    self.posSelected = self.pos
                    self.haveSelection = True
                elif not (pygame.key.get_mods() & gui.KMOD_SHIFT):
                    self.haveSelection = False
            self.avoidCuesVertically();
            if self.beforeStart():
                self.moveToStart();
            self.repaint()
            self.updateState();
        elif e.type == gui.MOUSEMOTION:
            if pygame.mouse.get_pressed()[0]:
                if not self.haveSelection:
                    self.posSelected = self.pos
                    self.haveSelection = True
                self.setCursorByXY(e.pos)
                self.avoidCuesVertically();
                if self.beforeStart():
                    self.moveToStart();
                self.repaint()
                self.updateState();
        elif e.type == gui.MOUSEBUTTONUP:
            self.setCursorByXY(e.pos)
            self.avoidCuesVertically();
            if self.beforeStart():
                self.moveToStart();
            self.repaint()
            self.updateState();
        elif e.type == gui.FOCUS:
            self.repaint()
        elif e.type == gui.BLUR:
            self.repaint()
        
        self.pcls = ""
        if self.container and self.container().myfocus and self.container().myfocus() is self: self.pcls = "focus"
        
        return used
    
    def refreshScript(self):
        if self.script is not None:
            self.value, self.scriptMap= self.script.toText();
            self.pos= self.value.find('\t')+1;
            self.posSelected = self.pos        # The stored end of the cursor (for text selection)
        else:
            self.value= "";
            self.scriptMap= [];
            
# The first version of this code was done by Clint Herron, and is a modified version of input.py (by Phil Hassey).
# It is under the same license as the rest of the PGU library.
