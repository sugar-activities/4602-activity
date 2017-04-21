import string;

# Pygame Imports
import pygame
from pygame.locals import *

# Spyral Import
import spyral

# PGU Imports
from pgu import text
from pgu import gui
from pgu import html
from scriptarea import ScriptArea

# Broadway Imports
from broadway import hacks
from constants import *;
import backdrop;
import actor;
import action

import panel
import filePanel
import backdropPanel
import actorPanel
import writePanel
import theaterPanel

class Tab(gui.Table):
    """
    The tab holds five buttons that let you switch between panels.
    """
    def __init__(self, script):
        gui.Table.__init__(self,
                           width= geom['tab'].width,
                           height= geom['tab'].height);
        
        self.script= script;
        
        panels= [filePanel.FilePanel, backdropPanel.BackdropPanel, 
                 actorPanel.ActorPanel, writePanel.WritePanel, 
                 theaterPanel.TheaterPanel];
        curPanel= 0;
        
        self.activePanel= panels[curPanel](self.script);
        self.activePanel.build();
        self.panelHolder= gui.Container(width= geom['panel'].width,
                                        height= geom['panel'].height);
        self.panelHolder.add(self.activePanel, 0, 0);
        
        self.tabGroup= gui.Group('tab-group-panels', panels[curPanel]);
        self.tabGroup.connect(gui.CHANGE, self.changePanel);
        
        buttonHeight= geom['tab'].height / len(panels) * 3 / 5;
        buttonWidth= geom['tab'].width * 3 / 5;
        self.panelLabels= {}
        for aPanel in panels:
            self.tr();
            panelLabel= gui.Label(aPanel.name,
                                  name='tab-label-panels-'+aPanel.name);
            self.panelLabels[aPanel] = panelLabel
            aPanel.sourceTab= self
            panelTool= gui.Tool(self.tabGroup, panelLabel, aPanel, 
                                width=buttonWidth,
                                height=buttonHeight,
                                name='tab-tool-panels-'+aPanel.name);
            self.td(panelTool, style={'padding': 10})

    def changePanel(self):
        self.activePanel.tearDown();
        self.activePanel.removeAll();
        self.panelHolder.remove(self.activePanel);
        self.activePanel= self.tabGroup.value(self.script);
        self.activePanel.sourceTab= self
        self.activePanel.build();
        self.panelHolder.add(self.activePanel, 0, 0);
        
    def reload(self):
        for aPanel, aPanelLabel in self.panelLabels.items():
            aPanelLabel.value = translate(aPanel.name)