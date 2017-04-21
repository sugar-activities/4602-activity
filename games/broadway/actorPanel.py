# Pygame Imports
import pygame
from pygame.locals import *

# Spyral Import
import spyral

# PGU Imports
from pgu import gui

# Broadway Imports
from broadway import hacks
from constants import *;
import actor;
import action;

import panel


class ActorPanel(panel.Panel):
    # Add/remove/modify actors
    # change name, voice, costume, pose, look, position, direction
    name= _("Actor")
    def __init__(self, script):
        panel.Panel.__init__(self);
        self.script= script;
        self.waitingOnMouse= False;
    
    def build(self):
        panel.Panel.build(self);
        self.groups= [];
        self.editablesDocumentLeft= None;
        self.editablesDocumentRight= None;
        self.focusDocument= None;
        self.buildFocusSelecter();
        minusButton= gui.Button(_("Remove Actor"), name='actor-button-remove', style={'margin':10, 'padding':5});
        minusButton.connect(gui.CLICK, self.removeActor);
        self.add(minusButton, geom['panel'].width - minusButton.getWidth(), 20);
        self.owningWidgets.append(minusButton);
    
    def changeFocus(self, value= None):
        if value == None:
            value= self.script.controls['actor-group-focus'].value;
        else:
            self.script.controls['actor-group-focus'].value= value;
        if value == _("Add actor"):
            self.addActor();
        else:
            self.killEditableDocument();
            self.buildEditablesDocument();
    
    def addActor(self):
        newActor= actor.Actor(defaults['actor'],defaults['actorName']);
        self.script.addActor(newActor);
        newActor.state.position= defaults['positions'][len(self.script.actors)-2];
        newActor.changeBodyPosition();
        self.buildFocusSelecter(newActor);
        self.script.scriptChanged();
    
    def removeActor(self):
        newActor= self.script.controls['actor-group-focus'].value;
        if newActor != self.script.actors[0]:
            self.script.controls['actor-group-focus'].value= self.script.actors[0];
            positionInList= self.script.actors.index(newActor);
            self.script.controls['actor-tool-focus-'+str(positionInList)].value= None;
            self.script.controls['actor-button-test'].disconnect(gui.CLICK);
            self.script.removeActor(newActor);
            self.buildFocusSelecter();
            self.script.scriptChanged();
    
    def killEditableDocument(self):
        self.editablesDocumentLeft.kill();
        self.remove(self.editablesDocumentLeft);
        if self.editablesDocumentLeft in self.owningWidgets:
            self.owningWidgets.remove(self.editablesDocumentLeft);
        self.editablesDocumentRight.kill();
        self.remove(self.editablesDocumentRight);
        if self.editablesDocumentRight in self.owningWidgets:
            self.owningWidgets.remove(self.editablesDocumentRight);
    
    def buildEditablesDocument(self):
        newActor= self.script.controls['actor-group-focus'].value;
        self.editablesDocumentLeft= gui.Document();
        self.editablesDocumentRight= gui.Document();
        self.add(self.editablesDocumentLeft,10,95);
        self.add(self.editablesDocumentRight,510,95);
        if newActor != self.script.actors[0]:
            self.buildNameInput();
            self.buildSkinSelecter();
        self.buildVoiceSelecter();
        if newActor != self.script.actors[0]:
            self.buildLookSelecter();
            self.buildPoseSelecter();
            self.buildDirectionSelecter();
            self.buildMovers();
        self.owningWidgets.append(self.editablesDocumentLeft);
        self.owningWidgets.append(self.editablesDocumentRight);
    
    ####################################
    
    def buildPoseSelecter(self):
        focusedActor= self.script.controls['actor-group-focus'].value;
        poses= focusedActor.poses;
        pose= self.script.frames[0][focusedActor].pose;
        
        poseSelecter= gui.Select(name='actor-select-pose', value=pose, cols=3);
        poseSelecter.connect(gui.SELECT, self.changePose);
        for aPose in poses:
            prettyPose= _(aPose.replace('_',' ').title())
            poseSelecter.add(prettyPose, aPose);
        
        self.editablesDocumentRight.add(gui.Label(_("Initial Pose: ")));
        self.editablesDocumentRight.add(poseSelecter);
        self.spaceEditablesDocumentRight();
    
    def changePose(self):
        pose= self.script.controls['actor-select-pose'].value;
        focusedActor= self.script.controls['actor-group-focus'].value;
        doAction= action.Action(focusedActor,
                                  verbs.DO,
                                  pose);
        self.script.applyAction(0,doAction);
        focusedActor.state.pose= pose;
        focusedActor.changeBodyPose();
        self.script.scriptChanged();
        
    def changeLook(self):
        look= self.script.controls['actor-select-look'].value;
        focusedActor= self.script.controls['actor-group-focus'].value;
        feelAction= action.Action(focusedActor,
                                  verbs.FEEL,
                                  look);
        self.script.applyAction(0,feelAction);
        focusedActor.state.look= look;
        focusedActor.changeFaceExpression();
        self.script.scriptChanged();
    
    #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    
    def buildLookSelecter(self):
        focusedActor= self.script.controls['actor-group-focus'].value;
        looks= focusedActor.looks;
        look= self.script.frames[0][focusedActor].look;
        
        lookSelecter= gui.Select(name='actor-select-look', value=look, cols=4);
        lookSelecter.connect(gui.SELECT, self.changeLook);
        for aLook in looks:
            prettyLook= _(aLook.replace('_',' ').title())
            lookSelecter.add(prettyLook, aLook);
        
        self.editablesDocumentRight.add(gui.Label(_("Initial Look: ")));
        self.editablesDocumentRight.add(lookSelecter);
        self.spaceEditablesDocumentRight();
    
    def buildDirectionSelecter(self):
        focusedActor= self.script.controls['actor-group-focus'].value;
        direction= self.script.frames[0][focusedActor].direction;
        
        self.editablesDocumentRight.add(gui.Label(_("Initial Face: ")));
        for aDirection in directions:
            prettyDirection= _(aDirection.replace('_',' ').title());
            positionButton= gui.Button(prettyDirection, name='actor-button-direction-'+prettyDirection);
            positionButton.connect(gui.CLICK, self.changeDirection, aDirection);
            self.editablesDocumentRight.add(positionButton);
        self.spaceEditablesDocumentRight();
    
    def changeDirection(self, direction):
        focusedActor= self.script.controls['actor-group-focus'].value;
        faceAction= action.Action(focusedActor,
                                  verbs.FACE,
                                  direction);
        self.script.applyAction(0,faceAction);
        focusedActor.state.direction= direction;
        focusedActor.changeBodyDirection();
        self.script.scriptChanged();
        
    ####################################
    
    def buildMovers(self):
        focusedActor= self.script.controls['actor-group-focus'].value;
        position= self.script.frames[0][focusedActor].position;
        offscreen= type(position) is str;
        
        positionButton= gui.Button(_("Move"), name='actor-button-move');
        positionButton.connect(gui.CLICK, self.changePositionAbsolutely);
        self.editablesDocumentRight.add(positionButton);
        
        self.editablesDocumentRight.add(gui.Label(_(" or start offscreen ")));
        
        positionSwitch= gui.Switch(value=offscreen, name='actor-switch-offscreen');
        positionSwitch.connect(gui.CLICK, self.changePosition);
        self.editablesDocumentRight.add(positionSwitch);
        self.spaceEditablesDocumentRight();
    
    def changePositionAbsolutely(self):
        pygame.mouse.set_cursor(*pygame.cursors.broken_x);
        self.waitingOnMouse= True;
        self.script.scriptChanged();
    
    def changePosition(self):
        offscreen= self.script.controls['actor-switch-offscreen'].value;
        if offscreen:
            position= defaults['position'];
        else:
            position= 'left';
        focusedActor= self.script.controls['actor-group-focus'].value;
        moveAction= action.Action(focusedActor,
                                  verbs.MOVE,
                                  position);
        self.script.applyAction(0,moveAction);
        focusedActor.state.position= position;
        focusedActor.changeBodyPosition();
        self.script.scriptChanged();
    
    def handleGlobalMouse(self, position, button):
        if self.waitingOnMouse:
            pygame.mouse.set_cursor(*pygame.cursors.arrow);
            if button == 1:
                focusedActor= self.script.controls['actor-group-focus'].value;
                moveAction= action.Action(focusedActor,
                                          verbs.MOVE,
                                          position);
                self.script.applyAction(0,moveAction);
                focusedActor.state.position= position;
                focusedActor.changeBodyPosition();
                self.script.controls['actor-switch-offscreen'].value= False;
            self.waitingOnMouse= False;
        else:
            newFocus= None;
            for anActor in self.script.actors:
                #print anActor.rect, position;
                if anActor.rect.collidepoint(position) and button == 1:
                    newFocus= anActor;
            if newFocus is not None:
                self.script.controls['actor-group-focus'].change(newFocus);
                self.killEditableDocument();
                self.buildEditablesDocument();
    
    def buildSkinSelecter(self):
        newActor= self.script.controls['actor-group-focus'].value;
        skinSelecter= gui.Select(name='actor-select-skin', value=newActor.directory, cols=4);
        skinSelecter.connect(gui.SELECT, self.changeSkin);
        for aSkin in actors:
            if aSkin != "narrator":
                prettyActor= _(aSkin.replace('_',' ').title())
                skinSelecter.add(prettyActor, aSkin)
        self.editablesDocumentLeft.add(gui.Label(_("Actor: ")))
        self.editablesDocumentLeft.add(skinSelecter);
        self.spaceEditablesDocumentLeft();
    
    def changeSkin(self):
        currentActor= self.script.controls['actor-group-focus'].value;
        currentActor.changeImages(self.script.controls['actor-select-skin'].value);
        self.script.controls['actor-select-skin']._close(None);
        self.buildFocusSelecter(currentActor);
        self.script.scriptChanged();
    
    def buildNameInput(self):
        newActor= self.script.controls['actor-group-focus'].value;
        nameInput= gui.Input(name='actor-input-name', value=newActor.name,size=30);
        nameInput.connect(gui.BLUR, self.changeName);
        self.editablesDocumentLeft.add(gui.Label(_("Name: ")));
        self.editablesDocumentLeft.add(nameInput);
        self.spaceEditablesDocumentLeft();
    
    def changeName(self):
        currentActor= self.script.controls['actor-group-focus'].value;
        currentActor.name= self.script.controls['actor-input-name'].value;
        self.buildFocusSelecter(currentActor);
        self.script.scriptChanged();
    
    def buildVoiceSelecter(self):
        newActor= self.script.controls['actor-group-focus'].value;
        voiceSelecter= gui.Select(name='actor-select-voice', value=newActor.voice, cols=8);
        voiceSelecter.connect(gui.SELECT, self.changeVoice);
        for aVoice in voices:
            voiceSelecter.add(_(aVoice.visibleName), aVoice);
        self.editablesDocumentLeft.add(gui.Label(_("Voice: ")));
        self.editablesDocumentLeft.add(voiceSelecter);
        speakButton= gui.Button(_("Test"), name='actor-button-test');
        speakButton.connectWeakly(gui.CLICK, newActor.quickSpeak, defaults['voice-test']);
        self.editablesDocumentLeft.space((10,1));
        self.editablesDocumentLeft.add(speakButton);
        self.spaceEditablesDocumentLeft();
    
    def changeVoice(self):
        newActor= self.script.controls['actor-group-focus'].value;
        newVoice= self.script.controls['actor-select-voice'].value;
        newActor.voice= newVoice;
        self.script.scriptChanged();
    
    def spaceEditablesDocumentLeft(self):
        self.editablesDocumentLeft.br(1);
        self.editablesDocumentLeft.add(gui.Spacer(4,5));
        self.editablesDocumentLeft.br(1);
    def spaceEditablesDocumentRight(self):
        self.editablesDocumentRight.br(1);
        self.editablesDocumentRight.add(gui.Spacer(4,5));
        self.editablesDocumentRight.br(1);
    
    def buildFocusSelecter(self, focus=None):
        if self.focusDocument is not None:
            self.groups= [];
            self.focusDocument.clear();
            self.remove(self.focusDocument);
            if self.focusDocument in self.owningWidgets:
                self.owningWidgets.remove(self.focusDocument);
            self.killEditableDocument();
            
        actors= self.script.actors;
        if focus is not None:
            focusGroup= gui.Group('actor-group-focus', focus);
        else:
            focusGroup= gui.Group('actor-group-focus', actors[0]);
        focusGroup.connect(gui.CHANGE, self.changeFocus);
        self.groups.append(focusGroup);

        focusDocument= gui.Document();
        length= 20-len(actors);
        i= 0;
        for anActor in actors:
            focusToolTable= gui.Table();
            focusToolTable.tr();
            focusToolTable.td(gui.Image(anActor.thumb));
            focusToolTable.tr();
            focusToolTable.td(gui.Label(anActor.shortName(length)));
            focusTool= gui.Tool(focusGroup, 
                                focusToolTable, 
                                anActor,
                                name='actor-tool-focus-'+str(i));
            focusDocument.add(focusTool);
            focusDocument.add(gui.Spacer(4,1));
            i+= 1;
        if len(actors) < limits['actors']:
            plusLabel= gui.Label(_("Add actor"));
            plusTool= gui.Tool(focusGroup, 
                                plusLabel, 
                                _("Add actor"),
                                style={'margin':10, 'padding':5},
                                name= 'actor-focus-plusTool');
            focusDocument.add(plusTool);
        self.add(focusDocument, 20,20);
        self.focusDocument= focusDocument;
        self.buildEditablesDocument();
        self.owningWidgets.append(focusDocument);