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

import panel

class TheaterPanel(panel.Panel):
    # Blank while playing
    name= _("Theater")
    def __init__(self, script):
        panel.Panel.__init__(self);
        self.script= script;
        self.director= self.script.director;
    
    def stopScript(self):
        self.playButton.value= gui.Image(images['media-play']);
        self.playButton.activated= False;
        self.script.enableControls();
        
    def playScript(self):
        if self.playButton.activated:
            self.stopScript();
            self.script.director.stop();
        else:
            self.playButton.value= gui.Image(images['media-pause']);
            self.playButton.activated= True;
            if self.script.director.isDone():
                self.script.director.reset();
                self.progressSlider.value= 0;
            position= self.progressSlider.value;
            self.script.director.startAt(position, 
                                         callback= self.stopScript, 
                                         continualCallback= self.updateProgressBar);
            self.script.disableControls(['write-button-test']);
            self.on= False;
    
    def buildProgressSliderArguments(self):
        initial= self.director.timeProgress;
        start= 0;
        end= len(self.script.actions);
        if end < 1: end= 1;
        width= geom['panel'].width / 2;
        height= 16;
        size= max(16, width / (1+end));
        return {'value' : initial,
                'min': start, 
                'max': end,
                'size': size, 
                'width': width, 
                'height': height,
                'style': {'padding': 4}};
    
    def updateProgressBar(self, timeProgress, actionProgress):
        self.progressSlider.value= timeProgress;
    
    def changeProgressBar(self):
        self.director.goto(self.progressSlider.value, None);

    def build(self):
        # Play Button
        # Pause Button
        # Rewind, Forward
        # Slider
        panel.Panel.build(self);
        theaterTable= gui.Table(height= geom['panel'].height,
                                width= geom['panel'].width * 3/4);
        theaterTable.tr();
        
        rewindAllButton= gui.Button(gui.Image(images['media-first']), style={'padding':5})
        rewindButton= gui.Button(gui.Image(images['media-backward']), style={'padding':5});
        self.playButton= gui.Button(gui.Image(images['media-play']), style={'padding':5});
        forwardButton= gui.Button(gui.Image(images['media-forward']), style={'padding':5});
        forwardAllButton= gui.Button(gui.Image(images['media-last']), style={'padding':5});
        
        self.script.director.reset();
        self.progressSlider= gui.HSlider(**self.buildProgressSliderArguments());
        self.progressSlider.connect(gui.CLICK, self.changeProgressBar);
        
        rewindAllButton.connect(gui.CLICK, self.director.rewindAll, self.updateProgressBar);
        rewindButton.connect(gui.CLICK, self.director.rewind, self.updateProgressBar);
        self.playButton.connect(gui.CLICK, self.playScript);
        forwardButton.connect(gui.CLICK, self.director.forward, self.updateProgressBar);
        forwardAllButton.connect(gui.CLICK, self.director.forwardAll, self.updateProgressBar);
        
        self.playButton.activated= False;

        theaterTable.td(gui.Spacer(1,1), align= 0);
        theaterTable.td(rewindAllButton, align= 0);
        theaterTable.td(rewindButton, align= 0);
        theaterTable.td(self.playButton, align= 0);
        theaterTable.td(forwardButton, align= 0);
        theaterTable.td(forwardAllButton, align= 0);
        theaterTable.td(gui.Spacer(1,1), align= 0);
        
        
        theaterTable.tr();
        theaterTable.td(self.progressSlider, colspan=7, align= 0);
        
        theaterTable.tr();
        theaterTable.td(gui.Label(_("Subtitles:  ")),
                        colspan= 2, align=1);
        subtitleSwitch= gui.Switch(value=hacks['subtitle'], name='theater-switch-subtitles');
        subtitleSwitch.connect(gui.CLICK, self.subtitleSwitchState);
        theaterTable.td(subtitleSwitch, colspan= 1, align=-1);
        theaterTable.td(gui.Spacer(1,1), colspan= 1);
        theaterTable.td(gui.Label(_("Mute:  ")),
                        colspan= 1, align=1);
        muteSwitch= gui.Switch(value=hacks['mute'], name='theater-switch-mute');
        muteSwitch.connect(gui.CLICK, self.muteSwitchState);
        theaterTable.td(muteSwitch, colspan= 2, align= -1);
        
        theaterDocument= gui.Document(width= geom['panel'].width,
                                      height= geom['panel'].height,
                                      align= 0);
        theaterDocument.add(theaterTable);
        self.add(theaterDocument, 0,10);
    
    def subtitleSwitchState(self):
        self.director.subtitler.on= not self.script.controls['theater-switch-subtitles'].value;
        hacks['subtitle']= self.director.subtitler.on
        changeSetting('Subtitle', self.director.subtitler.on)
    
    def muteSwitchState(self):
        hacks['mute']= not self.script.controls['theater-switch-mute'].value;
        changeSetting('Mute', hacks['mute'])
    
    #def changeBackdrop(self):
    #    back= self.script.controls['backdrop'].value;
    #    self.script.setBackdrop(backdrop.Backdrop(back));
    