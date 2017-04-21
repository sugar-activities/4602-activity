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
import action;

class Panel(gui.Container):
    name= _("Generic Panel")
    """
    A Panel is a PGU *Container* that can be swapped by a *Tab*. There are five
    tabs in Broadway. This class is meant to be subclassed.
    """
    def __init__(self):
        """
        Initializes the Panel
        """
        gui.Container.__init__(self);
        self.owningWidgets= [];
        self.groups= [];
    
    def build(self):
        """
        Virtual function that is called when the Panel is first given focus. Should be
        used to (re)build any components in the panel.
        """
        self.add(gui.Image(images['main-panel'], name='panel-image-background'), 0,0);
    
    def tearDown(self):
        """
        Function that is called when the Panel is losing focus. Should be used
        to remove any built components.
        """
        for aWidget in self.owningWidgets:
            aWidget.kill();
        self.owningWidgets= [];
        self.groups= [];
        self.kill();
    
    def handleGlobalMouse(self, position, button):
        """
        Virtual function that can be overriden to handle customized input
        from the mouse when it is clicked anywhere on the screen.
        """
        pass;
    
    def refreshPanel(self):
        self.tearDown();
        self.build();
    
    

