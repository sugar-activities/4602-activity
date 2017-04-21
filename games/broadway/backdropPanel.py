import string;

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
import backdrop;

import panel

class BackdropPanel(panel.Panel):
    # Choose a backdrop
    name= _("Backdrop")
    def __init__(self, script):
        panel.Panel.__init__(self);
        self.script= script;
        
        self.groups= None;
        self.backdropIndex= 0;
        self.backdropsOnscreen= min(5, len(backdrops));
    
    def gotoBackdropPage(self, to):
        #self.tearDown();
        self.groups= None;
        self.owningWidgets= [];
        self.clear();
        #checkAllWidgets(self, self);
        to= min(to, len(backdrops)-self.backdropsOnscreen);
        to= max(to, 0);
        self.backdropIndex= to;
        self.build();
            
    
    def build(self):
        panel.Panel.build(self);
        backdropDocument= gui.Document(width=geom['panel'].width, align=0);
        back= self.script.backdrop;
        
        backdropGroup= gui.Group('backdrop-group-backdrops', back);
        backdropGroup.connect(gui.CHANGE, self.changeBackdrop);    
        
        start= self.backdropIndex;
        end= min(len(backdrops), self.backdropIndex + self.backdropsOnscreen);
        
        for aBackdrop in backdrops[start:end]:
            thumbPath= os.path.join('games/broadway/backdrops',aBackdrop+'_thumb.png');
            filePath= aBackdrop;
            backdropToolTable= gui.Table();
            backdropToolTable.tr();
            backdropToolTable.td(gui.Image(thumbPath));
            backdropToolTable.tr();
            backdropToolTable.td(gui.Label(_(string.capwords(aBackdrop))));
            backdropTool= gui.Tool(backdropGroup, 
                                backdropToolTable, 
                                filePath,
                                style={'margin':4},
                                name='backdrop-tool-backdrops-'+aBackdrop);
            backdropDocument.add(backdropTool);
            backdropDocument.add(gui.Spacer(4,6));
        
        #Custom Backdrop from local source
        customBackdropButton = gui.Button(_("Your's"),
                                      name='backdrop-button-backdrops-custom', 
                                      style={'width': 80, 'height': 32})
        customBackdropButton.connect(gui.CLICK, self.externalBackdrop)
        
        #Custom Backdrop from online source (teacher)
        teacherBackdropButton = gui.Button(_("Teacher's"),
                                        name='backdrop-button-backdrops-teacher', 
                                        style={'width': 80, 'height': 32},
                                        disabled = not hacks['server'])
        teacherBackdropButton.connect(gui.CLICK, self.teacherBackdrop)
        
        backdropGroup.connect(gui.CHANGE, self.changeBackdrop)
        self.groups= backdropGroup
        
        navigationButtons= gui.Table(width=geom['panel'].width);
        navigationButtons.tr();
        maxSize= (len(backdrops) - self.backdropsOnscreen - 1);
        size= geom['panel'].width * 3/4 / (1+ (maxSize / float(self.backdropsOnscreen)));
        progressBar= gui.HSlider(value= self.backdropIndex,
                                 min= 0,
                                 max= maxSize,
                                 size= size,
                                 step= 1,
                                 disabled= True,
                                 width= geom['panel'].width * 3/4,
                                 style= {'padding': 4,
                                         'margin' : 10});
        navigationButtons.td(progressBar, colspan= 5);
        navigationButtons.tr();
        homeButton= gui.Button(gui.Image(images['go-first']));
        homeButton.connect(gui.CLICK, self.gotoBackdropPage, 0);
        navigationButtons.td(homeButton);
        previousButton= gui.Button(gui.Image(images['go-back']));
        previousButton.connect(gui.CLICK, self.gotoBackdropPage, self.backdropIndex-self.backdropsOnscreen);
        navigationButtons.td(previousButton);
        if start == end:
            label= _("No backdrops loaded");
        elif (end - start) == 1:
            label= _("Backdrop %(index)d") % {"index": (start+1)}
        else:
            label= _("Backdrops %(start_index)d to %(end_index)d") % {"start_index": start+1, 
                                                                      "end_index": end}
        navigationButtons.td(gui.Label(label));
        forwardButton= gui.Button(gui.Image(images['go-next']));
        forwardButton.connect(gui.CLICK, self.gotoBackdropPage, self.backdropIndex+self.backdropsOnscreen);
        navigationButtons.td(forwardButton);
        endButton= gui.Button(gui.Image(images['go-last']));
        endButton.connect(gui.CLICK, self.gotoBackdropPage, len(backdrops));
        navigationButtons.td(endButton);
            
        self.add(backdropDocument, 0, 30);
        self.add(navigationButtons, 0, geom['panel'].height // 2 + 25);
        self.add(customBackdropButton, 10, 50)
        self.add(teacherBackdropButton, 10, 100)
        self.owningWidgets.append(customBackdropButton)
        self.owningWidgets.append(teacherBackdropButton)
        self.owningWidgets.append(backdropDocument);
        self.owningWidgets.append(navigationButtons);
    
    def changeBackdrop(self):
        back= self.script.controls['backdrop-group-backdrops'].value;
        self.script.setBackdrop(backdrop.Backdrop(back));
        self.script.scriptChanged();
    
    def externalBackdrop(self):
        d = gui.FileDialog(_("Load a Picture"),
                           _("Okay"), 
                           path=directories['images'], 
                           filter=['.png','.bmp','.jpg','.jpeg','.gif'],
                           favorites = defaults['favorites'])
        d.open()
        d.connect(gui.CLOSE, self.script.refreshTheater);
        d.connect(gui.CHANGE, self.loadBackdrop);
    
    def teacherBackdrop(self):
        teachers = getTeacherList()
        if teachers:
            d = gui.TeacherDialog()
            d.loadTeachers(teachers)
            d.connect(gui.CLOSE, self.script.refreshTheater);
            d.connect(gui.CHANGE, self.loadTeacherBackdrop);
            d.open()
        else:
            d= gui.ConfirmDialog(_("Connection Error"), [_("You are not connected to the internet."),
                                                         _("Connect and then click Okay below.")])
            def tryAgain():
                d.close()
                self.teacherBackdrop()
            d.connect(gui.CLOSE, self.script.refreshTheater);
            d.okayButton.connect(gui.CLICK, tryAgain)
            d.open();
            
    def loadTeacherBackdrop(self, _widget):
        username= _widget.value
        try:
            downloadTeachersImage(username)
        except Exception, e:
            print "Could not connect.",e
            d= gui.ConfirmDialog(_("Connection Error"), [_("You are not connected to the internet."),
                                                         _("Connect and then click Okay below.")])
            def tryAgain():
                d.close()
                self.teacherBackdrop()
            d.connect(gui.CLOSE, self.script.refreshTheater);
            d.okayButton.connect(gui.CLICK, tryAgain)
            d.open();
            
        self.script.setBackdrop(backdrop.Backdrop(images['teacher-backdrop'], external=True));
        self.script.scriptChanged();
        
        #exportOptions = gui.Document()
        #exportButtons= [(gui.Button(_("Text"), name= 'file-button-export-text', style={'margin':4}), 'text', ['.txt']),
                        #(gui.Button(_("HTML"), name= 'file-button-export-html', style={'margin':4}), 'html', ['.html'])]
        #, (gui.Button(_("Video"), name= 'file-button-export-text', style={'margin':4}), 'video', ['.mpeg'])
        # d= gui.Dialog(gui.Label(_("Export")), exportOptions)
        # for aButton, value, valueType in exportButtons:
            # exportOptions.add(aButton)
            # aButton.connect(gui.CLICK, self.export, value, valueType, d)
        # d.connect(gui.CLOSE, self.script.refreshTheater);
        # d.open()

    def loadBackdrop(self, _widget):
        fullPath= _widget.value;
        self.script.setBackdrop(backdrop.Backdrop(fullPath, external=True));
        self.script.scriptChanged();
        #for x in getAllInstances(backdrop.Backdrop):
            #checkBackrefs(x,str(id(x)),[self]);