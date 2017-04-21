# Pygame Imports
import pygame
from pygame.locals import *

# Spyral Import
import spyral

# PGU Imports
from pgu import gui
from scriptarea import ScriptArea

# Broadway Imports
from broadway import hacks
from constants import *;
import actor

import panel

class WritePanel(panel.Panel):
    # Write story, change character, pose, look, position, direction
    name= _("Write")
    def __init__(self, script):
        panel.Panel.__init__(self);
        self.script= script;
        self.scriptArea= ScriptArea(self.script, 
                                    width= geom['scriptArea'].width, 
                                    height= geom['scriptArea'].height,
                                    name='write-scriptArea-script');        
        self.selectablesDocumentTable= None;
        self.focusDocument= None;
        self.waitingOnMouse= False;
    
    def build(self):
        panel.Panel.build(self);
        self.groups= [];
        self.plotTwist= self.script.getRandomTwist();
        self.add(self.scriptArea, *geom['scriptArea'].topleft);
        self.scriptArea.refreshScript();
        self.script.director.reset();
        self.on= True;
        self.playButton= gui.Button(_("Test"), name='write-button-test');
        self.playButton.connect(gui.CLICK, self.playHighlighted);
        self.add(self.playButton, geom['panel'].width-60, geom['scriptPanel'].top+15);
        self.buildFocusSelecter();
    
    def tearDown(self):
        panel.Panel.kill(self);
        self.groups= [];
    
    def stopHighlighted(self):
        self.playButton.value= _("Test");
        self.on= True;
        self.script.enableControls();
        
    def playHighlighted(self):
        if self.on:
            self.playButton.value= _("Stop");
            start, end= self.scriptArea.getSelectedTime();
            if start == end:
                self.script.director.startAt(start, callback= self.stopHighlighted);
            else: 
                self.script.director.startRange(start, end, callback= self.stopHighlighted);
            self.script.disableControls(['write-button-test']);
            self.on= False;
        else:
            self.stopHighlighted();
            self.script.director.stop();
    
    def buildPoseSelecter(self):
        actor= self.script.controls['write-group-focus'].value;
        poses= actor.poses;
        pose= actor.state.pose;
        
        poseSelecter= gui.Select(name='write-select-pose', value=pose, cols=3);
        poseSelecter.connect(gui.SELECT, self.changePose);
        for aPose in poses:
            prettyPose= _(aPose.replace('_',' ').title());
            poseSelecter.add(prettyPose, aPose);
        
        self.selectablesDocumentLeft.add(gui.Label(_("Change Pose: ")));
        self.selectablesDocumentLeft.add(poseSelecter);
        self.spaceSelectableDocumentLeft();
        
    def changeLook(self):
        newLook= self.script.controls['write-select-look'].value;
        self.scriptArea.insertCue(verbs.FEEL, newLook);
        self.scriptArea.insertLetter(' ');
        self.scriptArea.moveRight();
        self.scriptArea.focus();
        self.script.scriptChanged();
    
    def buildLookSelecter(self):
        actor= self.script.controls['write-group-focus'].value;
        looks= actor.looks;
        look= actor.state.look;
        
        lookSelecter= gui.Select(name='write-select-look', value=look, cols=4);
        lookSelecter.connect(gui.SELECT, self.changeLook);
        for aLook in looks:
            prettyLook= _(aLook.replace('_',' ').title())
            lookSelecter.add(prettyLook, aLook);
        
        self.selectablesDocumentLeft.add(gui.Label(_("Look: ")));
        self.selectablesDocumentLeft.add(lookSelecter);
        self.spaceSelectableDocumentLeft();
        
    def changePose(self):
        newPose= self.script.controls['write-select-pose'].value;
        self.scriptArea.insertCue(verbs.DO, newPose);
        self.scriptArea.insertLetter(' ');
        self.scriptArea.moveRight();
        self.scriptArea.focus();
        self.script.scriptChanged();
    
    def buildDirectionSelecter(self):
        actor= self.script.controls['write-group-focus'].value;
        direction= actor.state.direction;

        self.selectablesDocumentRight.add(gui.Label(_("Face: ")));
        for aDirection in directions:
            prettyDirection= aDirection.replace('_',' ').title();
            positionButton= gui.Button(_(prettyDirection), name='write-button-direction-'+prettyDirection);
            positionButton.connect(gui.CLICK, self.changeDirection, aDirection);
            self.selectablesDocumentRight.add(positionButton);
        self.spaceSelectableDocumentRight();
    
    def changeDirection(self, direction):
        self.scriptArea.insertCue(verbs.FACE, direction);
        #HACK: Insert a space to keep from breaking lines stupidly
        self.scriptArea.insertLetter(' ');
        self.scriptArea.moveRight();
        self.scriptArea.focus();
        self.script.scriptChanged();
    
    def buildIdeaGenerator(self):
        ideaButton= gui.Button(_("New Idea"), name='write-button-newTwist');
        ideaButton.connect(gui.CLICK, self.generateNewIdea);
        self.selectablesDocumentLeft.add(ideaButton);
        
        self.selectablesDocumentLeft.add(gui.Spacer(20,5));
        
        useButton= gui.Button(_("Use Idea"), name='write-button-useTwist');
        useButton.connect(gui.CLICK, self.useIdea);
        self.selectablesDocumentLeft.add(useButton);
        
        self.spaceSelectableDocumentLeft();
        
        self.selectablesDocumentTable.tr();
        
        self.selectablesDocumentTable.td(gui.Label(value=_("Current Idea:")));
        self.selectablesDocumentTable.tr();
        
        longestPlotTwist= self.script.getLongestTwist();
        ideaLabel= gui.WidthLabel(value=longestPlotTwist,
                             width= geom['scriptPanel'].width,
                             name='write-label-twist');
        self.selectablesDocumentTable.td(ideaLabel);
        ideaLabel.value= self.plotTwist;
    
    def generateNewIdea(self, _widget):
        self.plotTwist= self.script.getRandomTwist();
        self.script.controls['write-label-twist'].value= self.plotTwist;
        
    def useIdea(self):
        plotTwistText= self.script.controls['write-label-twist'].value;
        self.script.disableControls();
        self.scriptArea.insertString(plotTwistText);
        self.script.enableControls();
        self.scriptArea.focus();
        self.script.scriptChanged();
    
    def buildMovers(self):
        actor= self.script.controls['write-group-focus'].value;
        position= actor.state.position;
    
        self.selectablesDocumentRight.add(gui.Label(value=getMoveString(position),
                                                name='write-label-position'));
        for aDirection in directions:
            prettyDirection= aDirection.replace('_',' ').title();
            positionButton= gui.Button(_(prettyDirection), name='write-button-direction-'+prettyDirection);
            positionButton.connect(gui.CLICK, self.changePosition, aDirection);
            self.selectablesDocumentRight.add(positionButton);
        self.spaceSelectableDocumentRight();
        
        positionButton= gui.Button(_("Move"), name='write-button-move');
        positionButton.connect(gui.CLICK, self.changePositionAbsolutely);
        self.selectablesDocumentRight.add(positionButton);
        self.spaceSelectableDocumentRight();
    
    def spaceSelectableDocumentRight(self):
        self.selectablesDocumentRight.br(1);
        self.selectablesDocumentRight.add(gui.Spacer(4,15));
        self.selectablesDocumentRight.br(1);
    def spaceSelectableDocumentLeft(self):
        self.selectablesDocumentLeft.br(1);
        self.selectablesDocumentLeft.add(gui.Spacer(4,15));
        self.selectablesDocumentLeft.br(1);
    
    def changePositionAbsolutely(self):
        pygame.mouse.set_cursor(*pygame.cursors.broken_x);
        self.waitingOnMouse= True;
    
    def handleGlobalMouse(self, position, button):
        if self.waitingOnMouse:
            pygame.mouse.set_cursor(*pygame.cursors.arrow);
            if geom['theater'].collidepoint(position) and button == 1:
                self.scriptArea.insertCue(verbs.MOVE, position);
                self.scriptArea.insertLetter(' ');
                self.scriptArea.moveRight();
                self.scriptArea.focus();
                self.script.scriptChanged();
            self.waitingOnMouse= False;
        else:
            newFocus= None;
            for anActor in self.script.actors:
                if anActor.rect.collidepoint(position) and button == 1:
                    newFocus= anActor;
            if newFocus is not None:
                self.script.controls['write-group-focus'].change(newFocus);
                self.scriptArea.changeActor(newFocus);
                self.killSelectablesDocument();
                self.buildSelectablesDocument();
                self.scriptArea.focus();
    
    def changePosition(self, direction):
        actor= self.script.controls['write-group-focus'].value;
        position= actor.state.position;
        if type(position) is str:
            self.scriptArea.insertCue(verbs.ENTER, 
                                      self.getMovePosition(direction));
        else:
            self.scriptArea.insertCue(verbs.EXIT, direction);
        self.scriptArea.insertLetter(' ');
        self.scriptArea.moveRight();
        self.scriptArea.focus();
        self.script.scriptChanged();
    
    def getMovePosition(self, direction):
        if direction == 'left':
            return marks['houseLeft'];
        else:
            return marks['houseRight'];
    
    def buildFocusSelecter(self):
        if self.focusDocument in self.widgets:
            self.groups= [];
            self.focusDocument.clear();
            self.remove(self.focusDocument);
            if self.focusDocument in self.owningWidgets:
                self.owningWidgets.remove(self.focusDocument);
            self.killSelectablesDocument();
            self.remove(self.focusDocument);
        actors= self.script.actors;
        focusGroup= gui.Group('write-group-focus', self.script.getFirstActor());
        focusGroup.connect(gui.CHANGE, self.changeFocus);
        self.groups.append(focusGroup);
        
        focusDocument= gui.Document();
        focusDocument.add(gui.Label(_("Change speaker:")));
        focusDocument.br(1);
        length= 15-len(actors);
        for anActor in actors:
            focusToolTable= gui.Table();
            focusToolTable.tr();
            focusToolTable.td(gui.Image(anActor.thumb));
            focusToolTable.tr();
            focusToolTable.td(gui.Label(anActor.shortName(length)));
            focusTool= gui.Tool(focusGroup, 
                                focusToolTable, 
                                anActor,
                                name='write-tool-focus-'+anActor.name);
            focusDocument.add(focusTool);
            focusDocument.add(gui.Spacer(4,1));
                    
        self.add(focusDocument, *geom['scriptPanel'].topleft);
        
        self.focusDocument= focusDocument;
        self.buildSelectablesDocument();
    
    def changeFocus(self):
        newActor= self.script.controls['write-group-focus'].value;
        self.scriptArea.changeActor(newActor);
        self.killSelectablesDocument();
        self.buildSelectablesDocument();
        self.script.controls['panel-image-background'].repaint();
        self.script.scriptChanged();
    
    def killSelectablesDocument(self):
        self.selectablesDocumentTable.kill();
        self.remove(self.selectablesDocumentTable);
        if self.selectablesDocumentTable in self.widgets:
            self.owningWidgets.remove(self.selectablesDocumentTable);
    
    def buildSelectablesDocument(self):
        #self.script.disableControls();
        newActor= self.script.controls['write-group-focus'].value;
        self.selectablesDocumentTable= gui.Table(width= geom['scriptPanel'].width,
                                                 height= geom['scriptPanel'].height / 2);
        self.selectablesDocumentTable.tr();
        self.selectablesDocumentLeft= gui.Document(width= geom['scriptPanel'].width/2);
        self.selectablesDocumentTable.td(self.selectablesDocumentLeft);
        self.selectablesDocumentRight= gui.Document(width= geom['scriptPanel'].width/2);
        self.selectablesDocumentTable.td(self.selectablesDocumentRight);
        self.add(self.selectablesDocumentTable,
                geom['scriptPanel'].left,
                geom['scriptPanel'].top+ 75);
        if newActor == self.script.actors[0]:
            self.buildIdeaGenerator();
        else:
            self.buildLookSelecter();
            self.buildPoseSelecter();
            self.buildDirectionSelecter();
            self.buildMovers();
        #self.script.enableControls();
        self.scriptArea.focus();
