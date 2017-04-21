import simplejson as json;
import pygame
import spyral
import gzip;
import random

from pgu import gui;

from constants import *;
import actor;
import backdrop;
import frame;
import action;
from scriptMetadata import ScriptMetadata;
from director import Director;
import subtitler;

try:
    from sugar.datastore import datastore
except:
    class datastore(object):
        class DSObject(object):
            def __init__(self):
                self.metadata = {}
        @staticmethod
        def create():
            return DSObject()
        @staticmethod
        def write(ds_object):
            pass
        @staticmethod
        def find(query, sorting=None):
            return [DSObject(),DSObject(),DSObject()]

#_ = lambda x: x

class Script(object):
    """
    A *Script* is the essiential object of Broadway. It holds all the *Action*s,
    *Frame*s, *Actor*s, *ScriptMetadata*, and the *Backdrop*. It also holds 
    references to the *Director* and *Subtitler*. The custom PGU widget 
    *ScriptArea* manipulates the Script quite extensively. 
    
    HACK: The Script is also aware of all the named PGU widgets, so that it can
    handle the disabling and enabling of them. This should be delegated to
    someone else.
    
    Two very important data structures are *actions* and *frames*, which are
    lists of *Action*s and *Frame*s respectively. There is always one more frame
    than action. An empty script still has at least one frame, indicating the
    initial state. Applying an Action to a frame produces a new frame; all
    frames represent the state after each action is applied.
    
    For a script of length N, you can see the transition as follows.
    Frame 0 -> Action 0 -> Frame 1 -> Action 1 -> ... -> Action N -> Frame N+1
    
    TODO: Subtitler should probably belong to the Director directly. In fact,
    the Director should probably be more responsible for some of the things that
    the Script does with the Theater in general.
    """
    def __init__(self):
        """
        Initializes the Script
        """
        self.actors= [];
        self.backdrop= None;
        self.actions= [];
        self.frames= [frame.Frame()];
        self.metadata= ScriptMetadata();
        self.subtitler= subtitler.Subtitler();
        self.director= Director(self, self.subtitler);
        self.theater= None; #This is a Spyral Group to hold the actors, backdrop
        self.controls= gui.Form(); #Records all the PGU controls
        self.disabledControls= None; #Used to store the previous state of the controls when the're disabled
        self.skipControls= []; #Used to choose certain controls to be skipped when disabling.
        
        self.filepath= None; #Where this script is currently saved
        self.journal= False  #Whether we're saving this script to the journal or not
        self.unsaved= False; #Whether changes have been made to this script since it's been saved.
    
    def refreshTheater(self):
        """
        Forces the theater to redraw itself by calling spyrals redraw function.
        This can be used to clear up artifacts created by PGU that Spyral
        doesn't know about it. Those two just can't play nicely with each other.
        """
        spyral.director.get_camera().redraw();
    
    def scriptChanged(self):
        """
        This is called to explictly mention that the script is changed, i.e.
        by changing Script Metadata, adding an actor, etc.
        """
        self.unsaved= True;
    
    def setTheater(self, theater):
        """
        Used to change the theater (at which point the subtitler is automatically
        added to it).
        """
        self.theater= theater;
        theater.add(self.subtitler);
    
    def setRecorder(self, recorder):
        self.recorder= recorder
    
    def disableControls(self, skip= []):
        """
        Disable all controls, except for those in the skip list. Keeps a record
        of the original state of the controls so that they can be restored
        correctly later.
        """
        self.skipControls= skip;
        if self.disabledControls is None:
            self.disabledControls= {};
            for aWidget in self.controls.results():
                if aWidget not in self.skipControls:
                    self.disabledControls[aWidget]= self.controls[aWidget].disabled;
                    self.controls[aWidget].disabled= True;
    
    def enableControls(self, skip= []):
        """
        Reset all controls to their previous state, as previously recorded 
        before they were disabled. Skips any in the skip list.
        """
        if self.disabledControls is not None:
            for aWidget in self.controls.results():
                if aWidget in self.disabledControls and aWidget not in self.skipControls:
                    self.controls[aWidget].disabled= self.disabledControls[aWidget];
            self.disabledControls= None;
            self.skipControls= [];
    
    def setBackdrop(self, backdrop):
        '''
        Change the current backdrop
        '''
        if self.backdrop is not None:
            self.backdrop.kill();
        self.backdrop= backdrop;
        self.theater.add(self.backdrop);
    
    def getRandomTwist(self):
        """
        Uses the actors and backdrop to get a random twist
        """
        return self.backdrop.getRandomTwist(self.actors);
    
    def getLongestTwist(self):
        """
        Finds the longest twist possible, for sizing purposes.
        """
        return self.backdrop.getLongestTwist();
    
    def default(self):
        '''
        Set the Script to it's defaults
        '''
        #Backdrop
        self.setBackdrop(backdrop.Backdrop(defaults['backdrop']));
        #Frames
        self.frames= [frame.Frame()];
        #Actors
        self.killActors();
        self.actors= [];
        narrator= actor.Actor('narrator',_('Narrator'), narrator= True);
        #otherActor= actor.Actor('cheerleader (blue)', 'Becky', narrator= False);
        self.addActor(narrator);
        #self.addActor(otherActor);
        #Actions
        self.actions= [];
        focusNarrator= action.Action(narrator, verbs.FOCUS, None);
        self.insertAction(focusNarrator, 0);
        #Metadata
        self.metadata.reset();
        #Internal
        self.filepath= None
        self.unsaved= False
    
    def setState(self, time, character, state):
        '''
        Change the state of a character at a time
        '''
        actions= state.makeActions(character);
        for anAction in actions:
            self.applyAction(time, anAction);
    
    def applyAction(self, frame, newAction):
        """
        Advance throught the script, starting at the *frame*, and apply the
        *newAction* until you come across the same type of action associated
        with that subject.
        """
        if frame == 0:
            self.frames[frame][newAction.subject].applyAction(newAction);
            frame+= 1;
        while ((frame < len(self.frames)) and not
                (self.actions[frame-1].isSameType(newAction))):
            self.frames[frame][newAction.subject].applyAction(newAction);
            frame+= 1;
            
    def applyActionRecursively(self, time, newAction):
        '''
        Recursively apply the action through the list of frames until
        either the end or a similar action is reached.
        
        This function is now deprecated. Probably doesn't work anymore either.
        '''
        if time == 0:
            self.frames[time][newAction.subject].applyAction(newAction);
            self.applyAction(time+1, newAction);
        elif time-1 >= len(self.actions): # Equal to (time >= len(self.frames))
            return;
        elif self.actions[time-1].isSameType(newAction):
            return;
        else:
            self.frames[time][newAction.subject].applyAction(newAction);
            self.applyAction(time+1, newAction);
    
    def insertAction(self, newAction, time):
        '''
        Adds an action at a time. Time corresponds to a position in the actor 
        list.
        '''
        self.actions.insert(time, newAction);
        copyFrame= self.frames[time].copy();
        self.frames.insert(time+1, copyFrame);
        self.frames[time+1][newAction.subject].applyAction(newAction);##
        self.applyAction(time+2, newAction);
        
            
    def removeAction(self, time):
        ''' 
        Removes an action at a time. Time corresponds to a position in the
        actor list.
        '''
        changed= self.actions.pop(time);
        self.frames.pop(time+1);
        previous= self.frames[time][changed.subject];
        changed.objects= previous.getFromAction(changed);
        self.applyAction(time+1, changed);
        
    
    def changeAction(self, newAction, time):
        """
        Changes an action at a time. Time corresponds to a position in the actor
        list.
        """
        self.removeAction(time);
        self.insertAction(newAction, time);
    
    def changeActor(self, time, actor):
        """
        Changes the actor who performs each of the subsequent actions, until
        another FOCUS change is reached.
        """
        while time < len(self.actions):
            newAction= self.actions[time];
            if newAction.verb != verbs.FOCUS:
                newAction= action.Action(actor, newAction.verb, newAction.objects);
                self.changeAction(newAction, time);
                time+= 1;
            else: break;
        
    
    def addActor(self, actor):
        '''
        Add an actor to the script
        '''
        self.actors.append(actor);
        for aFrame in self.frames:
            aFrame[actor]= actor.state;
        #The first actor, the narrator, is not drawn
        if self.actors:
            actor.add(self.theater);
    
    def killActors(self):
        """
        Remove an actor from the Theater.
        
        Note that the author of Broadway does NOT encourage killing actors when
        you're done with them. That's probably really illegal and stuff.
        """
        for anActor in self.actors:
            anActor.kill();
        
    
    def removeActor(self, actor):
        '''
        Remove an actor and all it's actions from the script
        '''
        # Remove from actors list
        self.actors.remove(actor);
        # Remove from theater
        if len(self.actors):
            actor.kill();
            print [x.rect for x in self.theater.sprites()];
            #self.theater.remove(actor);
        i= 0;
        # Remove from actions
        while i < len(self.actions):
            if actor == self.actions[i].subject:
                self.removeAction(i);
            else:
                i+= 1;
        # Remove from frame
        for aFrame in self.frames:
            del aFrame[actor];
        
    
    def getFocusedActor(self, time):
        '''
        Walk backward through the actions till a FOCUS event is found
        '''
        if time < 0:
            return self.actors[0];
        elif time >= len(self.actions):
            time= len(self.actions)-1;
        while self.actions[time].verb != verbs.FOCUS and time > 0:
            time-= 1;
        return self.actions[time].subject;
    
    def chooseInterval(self, amount):
        """ Determine a reasonable interval to grab frames for export"""
        if amount == "Tons": return 1
        elif amount == "None": return -1
        elif len(self.frames) < 25:
            if amount == "Many": 5
            else: return 8
        elif amount == "Many": return 8
        else: return 16
    
    def export(self, arguments):
        """
        Given a file path and export type (value), creates an exported copy of this
        script.
        """
        path, fancy, amount = arguments
        if fancy == 'Plain':
            try:
                textFile = open(path, 'w')
                textFile.write(self.toPrettyText())
                textFile.close()
            except Exception, e:
                print e, "Couldn't export file for some reason."
        elif fancy == 'Fancy':
            self.refreshTheater()
            spyral.director.get_camera().draw(True)
            self.recorder.startShuttering(self.chooseInterval(amount))
            for time, action in enumerate(self.actions):
                self.director.goto(time, None)
                # Hack in the possibility for a saying action to have the actor's mouth open
                action = self.director.getCurrentAction()
                if action.verb == verbs.SAY:
                    action.subject.changeFaceState(True)
                self.theater.draw()
                self.refreshTheater()
                changes= spyral.director.get_camera().draw(True)
                self.recorder.addShutter(changes)
                action.subject.changeFaceState(False)
            else:
                self.director.forwardAll()
                self.theater.draw()
                self.refreshTheater()
                changes= spyral.director.get_camera().draw(True)
                self.recorder.addShutter(changes, True)
            frames= self.recorder.stopShuttering()
            try:
                htmlFile = open(path, 'w')
                htmlFile.write(self.toHtml(frames))
                htmlFile.close()
            except Exception, e:
                print e, "Couldn't export file for some reason"
            self.recorder.clearShutter()
    
    def toMpeg(self):
        print "Testing mpeg"
    
    def toText(self):
        '''
        Returns a textual representation of the script, along with a
        mapping between the Frame times and the text position
        '''
        text= "";
        previousChar= None;
        map= [];
        for i in xrange(len(self.actions)):
            if self.actions[i].verb == verbs.SAY: #speaking is rendered as text
                str= self.actions[i].objects;
            else: #other actions have special rendering
                str= self.actions[i].toText()
            text+= str;
            map.extend([i for aChar in str]);
        if text[-1] == '\n':
            text= text[:-1];
            map.pop();
        if text[0] == '\n':
            text= text[1:];
            map.pop(0);
        return text, map;
    
    def toPrettyText(self):
        """
        Returns a textual representation of this script that is suitable for showing to the user
        """
        text= self.metadata.toText()+"\n"
        for action in self.actions:
            text+= action.toPrettyText()
        return text
    
    def toHtml(self, frames):
        """
        Returns an HTML version of the script.
        """
        data= {'title': self.metadata.title, 'author': self.metadata.author, 'description' : self.metadata.description}
        imageSkeleton= """<img alt="Scene" style="margin:auto;display:block;margin-top: 4px;margin-bottom: 4px;border:1px solid black;" src="data:image/jpeg;base64,%(imageData)s"/>"""
        data['body']= ""
        for index, anAction in enumerate(self.actions):
            if index in frames:
                try:
                    imageFile = open(frames[index], 'rb')
                    image= imageFile.read()
                    imageFile.close()
                    imageData= image.encode('base64', 'strict')
                    data['body'] += imageSkeleton % {'imageData' : imageData}
                except Exception, e:
                    print "Problem adding images to HTML", e
            data['body'] += anAction.toHTML()
        else:
            try:
                imageFile = open(frames[len(self.frames)], 'rb')
                image= imageFile.read()
                imageFile.close()
                imageData= image.encode('base64', 'strict')
                data['body'] += imageSkeleton % {'imageData' : imageData}
            except Exception, e:
                print "Problem adding final image to HTML", e
        try:
            skeletonFile = open(r'games/broadway/themes/notepad.html', 'r')
            skeleton= skeletonFile.read()
            skeletonFile.close()
        except Exception, e:
            print "Problem loading the HTML file skeleton", e
        return (skeleton % data).replace("***", "%3D")
    
    def setFrame(self, time):
        """
        Sets each actor the state stored in the frames at *time*.
        """
        for anActor in self.actors:
            anActor.setState(self.frames[time][anActor]);
        
    def saveFile(self, filename):
        """
        Writes the current script out to a file.
        """
        try:
            file= gzip.open(filename, 'wb');
            #file= open(filename, 'w')
            data= json.dumps(self.encodeJSON());
            file.write(data);
            file.close();
            self.filepath= filename;
            self.unsaved= False;
        except Exception, inst:
            print "Save Failed"
            #print inst, inst.args
            self.unsaved= True;
    
    def loadFile(self, filename):
        """
        Reads in data from a file to make a new script.
        """
        try:
            file= gzip.open(filename, 'rb');
            data= file.read()
            self.decodeJSON(json.loads(data));
            file.close();
            self.filepath= filename;
            self.unsaved= False;
            self.director.reset();
            return
        except Exception, inst:
            print "Loading with compression failed, trying without compression"
        try:
            file= open(filename, 'r');
            data= file.read()
            self.decodeJSON(json.loads(data));
            file.close();
            self.filepath= filename;
            self.unsaved= False;
            self.director.reset();
        except Exception, inst:
            print "Loading without compression failed"
    
    def newFile(self, dummyArgument):
        """
        Marks this file as unsaved and reset it to it's defaults.
        """
        self.default();
        self.filepath= None;
        self.unsaved= True;
        self.director.reset();
    
    def encodeJSON(self):
        """ 
        Encodes the object in a JSON-friendly format (dictionary) and returns it.
        """
        output= {};
        output['Meta']= self.metadata.encodeJSON();
        output['Backdrop']= self.backdrop.encodeJSON();
        output['Actors']= [anActor.encodeJSON() for anActor in self.actors];
        output['Initial Frame']= self.frames[0].encodeJSON();
        output['Actions']= [anAction.encodeJSON() for anAction in self.actions];
        return output;
    
    def decodeJSON(self, input):
        """
        Decodes a JSON-created object and modifies the script based on it.
        """
        self.metadata= ScriptMetadata.decodeJSON(input['Meta']);
        self.setBackdrop(backdrop.Backdrop.decodeJSON(input['Backdrop']));
        self.killActors();
        self.actors= [];
        actorMap= {};
        for encodedActor in input['Actors']:
            decodedActor, oldActorId= actor.Actor.decodeJSON(encodedActor);
            oldActorId= int(oldActorId);
            actorMap[oldActorId]= decodedActor;
            self.addActor(decodedActor);
        self.frames= [frame.Frame.decodeJSON(input['Initial Frame'], actorMap)];
        i= 0;
        self.actions= [];
        for encodedAction in input['Actions']:
            decodedAction= action.Action.decodeJSON(encodedAction, actorMap);
            self.insertAction(decodedAction, i);
            i+= 1;
    
    def getFirstActor(self):
        if self.actions:
            return self.actions[0].subject;
        else:
            return self.actors[0];


if __name__ == '__main__':
    script= Script();
    a1= actor.Actor('Phil');
    a2= actor.Actor('Tom');
    script.addActor(a1);
    script.removeActor(a1);
    script.addActor(a1);
    script.addActor(a2);
    script.insertAction(action.Action(a1, verbs.FOCUS, None),0);
    script.insertAction(action.Action(a1, verbs.SAY, "Hello World"),1);
    script.insertAction(action.Action(a2, verbs.FOCUS, None),len(script.actions));
    #script.insertAction(action.Action(a2, verbs.SAY, "Another Line"),3);
    print script.actions;
    print script.frames;
    print script.toText();