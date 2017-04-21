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

try:
    from sugar.datastore import datastore
except:
    class datastore(object):
        class DSObject(object):
            def __init__(self, name="", metadata= None):
                self.metadata = {'title' : name}
            def get_file_path(self):
                return "games/broadway/samples/An Example Story.bdw"
            def set_file_path(self, path):
                pass
        @staticmethod
        def create():
            return datastore.DSObject()
        @staticmethod
        def write(ds_object):
            pass
        @staticmethod
        def find(query, sorting=None):
            names = ["Sample Story", "The Beach", "Ignore me I am Debugging"]
            return [datastore.DSObject(name) for name in names], 0
            

class FilePanel(panel.Panel):
    """
    This panel holds the saving/loading/new buttons, the metadata editing area,
    and the credits label.
    """
    name= _("File")
    
    def __init__(self, script):
        """
        
        """
        panel.Panel.__init__(self);
        self.script= script;
        self.testingTable= None;
        
    def autogenerateMetadata(self):
        return {"title"      : self.script.metadata.title,
                "activity"   : "org.laptop.community.broadway",
                "mime_type"  : "application/broadway",
                "description": self.script.metadata.description}
                
    
    def doNothing(self):
        pass;
    
    def build(self):
        panel.Panel.build(self);
        fileButtonsTable= gui.Table(width= 120,
                                    height= geom['panel'].height);
        
        buttons= [( _("Quit"), "file-button-quit", self.quit),
                  ( _("New"), "file-button-new", self.openNewDialog),
                  ( _("Open"), "file-button-load", self.openLoadDialog),
                  ( _("Save"), "file-button-save", self.openSaveDialog),
                  ( _("Save As"), "file-button-saveAs", self.openSaveAsDialog),
                  ( _("Export"), "file-button-export", self.checkIfScriptNamed)];
        for aButton in buttons:
            properName, internalName, function= aButton;
            aButton= gui.Button(properName, name=internalName, style={'width': 90, 'height': 30});
            aButton.connect(gui.CLICK, function);
            fileButtonsTable.tr();
            fileButtonsTable.td(aButton, align=0);
            if properName == _("Save"):
                self.saveButton= aButton;
        self.add(fileButtonsTable,0,0);
        self.owningWidgets.append(fileButtonsTable);
        
        logoImage= gui.Image(images['main-logo']);
        logoImage.connect(gui.CLICK, self.openCreditsDialog);
        self.add(logoImage, 160, 70);
        self.owningWidgets.append(logoImage);
        
        #creditsButton= gui.Button(_("Credits"), name= 'file-button-credits', style={'width': 80, 'height': 40});
        #creditsButton.connect(gui.CLICK, self.openCreditsDialog);
        #self.add(creditsButton, 255, 175);
        #self.owningWidgets.append(creditsButton);
        
        fileDocument= gui.Document(width=geom['panel'].width // 2, align=-1);
        
        fileDocument.add(gui.Label(_("Title: ")), align=-1);
        titleInput= gui.Input(name='file-input-title', value=self.script.metadata.title,size=30);
        titleInput.connect(gui.CHANGE, self.modifyScriptMetadata, 'title');
        fileDocument.add(titleInput, align= 1);
        
        fileDocument.space((10,40));
        fileDocument.br(1);
        
        fileDocument.add(gui.Label(_("Author(s): ")), align=-1);
        authorInput= gui.Input(name='file-input-author', value=self.script.metadata.author,size=30);
        authorInput.connect(gui.CHANGE, self.modifyScriptMetadata, 'author');
        fileDocument.add(authorInput, align=1);
        fileDocument.space((10,40));
        fileDocument.br(1);
        
        fileDocument.add(gui.Label(_("Description: ")), align=-1);
        fileDocument.br(1);
        descriptionArea= gui.TextArea(name='file-textArea-description', 
                                      value=self.script.metadata.description,
                                      width=geom['panel'].width // 2 - 11,
                                      height= geom['panel'].height // 3);
        descriptionArea.connect(gui.CHANGE, self.modifyScriptMetadata, 'description');
        fileDocument.add(descriptionArea, align= -1);
        fileDocument.space((10,10));
        
        self.add(fileDocument,500,30);
        
        self.owningWidgets.append(fileDocument);

        
        # languageSelector= gui.Select(name='file-button-language', value=language, cols=2);
        ## languageSelector.connect(gui.SELECT, self.changePose);
        # for aLanguage in languages:
            # prettyLanguage= aLanguage.replace('_',' ');
            # languageSelector.add(prettyLanguage, aLanguage);
        # languageSelector.connect(gui.SELECT, self.changeLanguage)
        
        #self.add(languageSelector, 730, 170);
        #self.owningWidgets.append(languageSelector);
        
        self.script.controls["file-button-save"].disabled= not self.script.unsaved;
        
    def quit(self):
        pygame.event.post(pygame.event.Event(pygame.QUIT, {}))
    
    def openCreditsDialog(self):
        """
        This will probs be changed to a nice Broadway logo, and then have a
        dialog box pop-up for the credits. For now, whatevs.
        """
        d= gui.InfoDialog(_("Credits"), information['credits']);
        d.connect(gui.CLOSE, self.script.refreshTheater);
        d.open();
    
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
        
    
    def checkIfScriptNamed(self):
        if self.script.metadata.title and self.script.metadata.author:
            self.openExportDialog()
        else:
            if self.script.metadata.title:
                message = _("an Author")
            elif self.script.metadata.author:
                message = _("a Title")
            else:
                message = _("an Author or Title")
            self.confirmActionDialog(_("Save without %(message)s?") % {"message" : message},
                                    [ _("You haven't given your script %(message)s.") % {"message" : message},
                                      _("Are you sure you want to export it?")],
                                    okayFunction= self.openExportDialog);
    
    def openExportDialog(self, d=None):
        if d is not None: d.close()
        main = gui.Table()
        
        # Some Image Amount code so we can reference it early
        imageAmountSelector= gui.Select(name='file-select-export-amount', value=_("Few"), cols=1);
        def activateImageAmount(_widget):
            imageAmountSelector.disabled= (_widget.value == "Plain")
        
        # Export Type
        main.tr()        
        main.td(gui.Label(_("Export Type: "), style={'margin': 4}))
        exportTypeSelector= gui.Select(name='file-select-export-fancy', value=_("Fancy"), cols=1);
        exportTypeSelector.connect(gui.SELECT, activateImageAmount);
        exportTypeSelector.add(_("Plain (just text)"), "Plain")
        exportTypeSelector.add(_("Fancy (pictures)"), "Fancy")
        main.td(exportTypeSelector)
        
        # Image Amount
        main.tr()
        main.td(gui.Label(_("Image Amount: "), style={'margin': 4}))
        imageAmountSelector.add(_("Tons"), "Tons")
        imageAmountSelector.add(_("Many"), "Many")
        imageAmountSelector.add(_("Few"),  "Few")
        imageAmountSelector.add(_("None"), "None")
        main.td(imageAmountSelector)
        
        # Location
        main.tr()
        main.td(gui.Label(_("Location: "), style={'margin': 4}))
        locationSelector= gui.Select(name='file-select-export-location', value=_("Here"), cols=1);
        locationSelector.add(_("Here"), "Here")
        if hacks['server']:
            locationSelector.add(_("Teacher"), "Teacher")
        main.td(locationSelector)
        
        # Okay/Cancel
        main.tr()
        okayButton= gui.Button(_("Okay"), name='file-button-export-okay', style={'margin': 10})
        main.td(okayButton)
        cancelButton= gui.Button(_("Cancel"), name='file-button-export-cancel', style={'margin': 10})
        main.td(cancelButton)
    
        # exportOptions = gui.Document()
        # exportButtons= [(gui.Button(_("Text"), name= 'file-button-export-text', style={'margin':4}), 'text', ['.txt']),
                        # (gui.Button(_("HTML"), name= 'file-button-export-html', style={'margin':4}), 'html', ['.html'])]
        ##, (gui.Button(_("Video"), name= 'file-button-export-text', style={'margin':4}), 'video', ['.mpeg'])
        d= gui.Dialog(gui.Label(_("Export")), main)
        # for aButton, value, valueType in exportButtons:
            # exportOptions.add(aButton)
            # aButton.connect(gui.CLICK, self.export, value, valueType, d)
        d.connect(gui.CLOSE, self.script.refreshTheater);
        
        cancelButton.connect(gui.CLICK, d.close)
        okayButton.connect(gui.CLICK, self.export, d)
        
        d.open()
    
    def export(self, _widget, dialog):
        fancy = self.script.controls["file-select-export-fancy"].value
        amount = self.script.controls["file-select-export-amount"].value
        location = self.script.controls["file-select-export-location"].value
        
        if fancy == "Fancy" and location == "Teacher" and amount == "Tons":
            d= gui.ConfirmDialog(_("Continue Upload?"), [_("Uploading a script with these settings might take a long time."),
                                                         _("Continue the upload anyway?")])
            def continueAnyway():
                d.close()
                dialog.close()
                self.exportActual(fancy, amount, location)
            d.connect(gui.CLOSE, self.script.refreshTheater);
            d.okayButton.connect(gui.CLICK, continueAnyway)
            d.open();
        else:
            dialog.close()
            self.exportActual(fancy, amount, location)
    
    def exportActual(self, fancy, amount, location):
        pecial_button= None
        if hacks['xo']:
            t= gui.Table()
            t.tr()
            if self.script.journal:
                t.td(gui.Image("games/broadway/images/dialog-folders.png"))
                t.tr()
                t.td(gui.Label(_("Folders")))
            else:
                t.td(gui.Image("games/broadway/images/dialog-journal.png"))
                t.tr()
                t.td(gui.Label(_("Journal")))
            special_button = gui.Button(t)
            def closeAndExportAs():
                dialog.close()
                self.script.refreshTheater()
                self.script.journal = not self.script.journal
                self.exportActual(fancy, amount, location)
            special_button.connect(gui.CLICK, closeAndExportAs)
        self.script.refreshTheater()
        if location == "Here":
            if fancy == "Fancy":
                valueType = ['.html']
                mimeType = "text/html"
            else:
                valueType = ['.txt']
                mimeType = "text/plain"
            if self.script.journal:
                exportName = self.script.metadata.title
                dialog = gui.JournalDialog(_("Export a script"),
                                           exportName,
                                           True,
                                           special_button=special_button)
                dialog.loadJournalItems(datastore.find({'mime_type' : mimeType})[0])
            else:
                exportName = filenameStrip(self.script.metadata.title) + valueType[0]
                dialog = gui.FileDialog(_("Export as %(fanciness)s") % {"fanciness" : _(fancy)},
                                   _("Okay"), 
                                   path=directories['export-folder'], 
                                   filter=valueType,
                                   default = exportName,
                                   favorites = defaults['favorites'],
                                   special_button=special_button)
            dialog.open()
            dialog.connect(gui.CLOSE, self.script.refreshTheater);
            dialog.connect(gui.CHANGE, self.exportFile, fancy, amount, dialog);
        else:
            teachers = getTeacherList()
            if teachers:
                dialog = gui.TeacherDialog()
                dialog.loadTeachers(teachers)
                dialog.connect(gui.CLOSE, self.script.refreshTheater);
                dialog.connect(gui.CHANGE, self.upload, fancy, amount, dialog);
                dialog.open()
            else:
                dialog= gui.ConfirmDialog(_("Connection Error"), [_("You are not connected to the internet."),
                                                             _("Connect and then click Okay below.")])
                def tryAgain():
                    dialog.close()
                    self.exportActual(fancy, amount, location)
                dialog.connect(gui.CLOSE, self.script.refreshTheater);
                dialog.okayButton.connect(gui.CLICK, tryAgain)
                dialog.open();
    
    def upload(self, _widget, fancy, amount, dialog):
        teacher = _widget.value
        try:
            dialog.close()
        except: pass
        try:
            self.script.saveFile(directories['temp']+"temp.bdw")
        except Exception, e:
            print "Failed to save bdw file.", e
        try:
            if fancy == "Fancy":
                self.script.export((directories['temp']+"tempExport", fancy, amount))
            elif fancy == "Plain":
                self.script.export((directories['temp']+"tempExport", fancy, amount))
        except Exception, e:
            print "Failed to export file.", e
        try:
            success= uploadToTeacher(teacher, self.script.metadata.title, fancy, directories['temp']+"temp.bdw", directories['temp']+"tempExport")
        except Exception, e:
            print "Failed to upload file.", e
            d= gui.ConfirmDialog(_("Upload Error"), [_("There was a problem uploading the script."),
                                                         _("Do you want to try again?")])
            def tryAgain():
                d.close()
                self.upload(_widget, fancy, amount, d)
            d.connect(gui.CLOSE, self.script.refreshTheater);
            d.okayButton.connect(gui.CLICK, tryAgain)
            d.open();
        
    def exportFile(self, _widget, fancy, amount, dialog):
        fullPath= _widget.value;
        dialog.close()
        if self.script.journal:
            dsObject= datastore.create()
            print dir(dsObject.metadata)
            dsObject.metadata.get_dictionary().update(self.autogenerateMetadata())
            dsObject.metadata['title']= fullPath.actualValue
            if fancy == "Fancy":
                dsObject.metadata['mime_type'] = 'text/html'
            else:
                dsObject.metadata['mime_type'] = 'text/plain'
            fullPath = directories['instance'] + 'temp.bdw'
            self.script.export((directories['instance'] + 'temp.bdw', fancy, amount));
            dsObject.set_file_path(fullPath)
            datastore.write(dsObject)
        else:
            fileName, fileExtension= os.path.splitext(fullPath);
            if fancy == "Fancy" and fileExtension != ".html":
                fullPath+= ".html"
            elif fancy == "Plain" and fileExtension != ".txt":
                fullPath+= ".txt"
            if os.path.isfile(fullPath):
                self.confirmActionDialog(_("Overwrite?"),
                                        [ _("This file already exists:"),
                                          os.path.basename(fullPath),
                                          _("Are you sure you want to overwrite it?")],
                                        okayFunction= self.script.export, 
                                        arguments=(fullPath,fancy, amount));
            else:
                self.script.export((fullPath, fancy, amount));
    
    def modifyScriptMetadata(self, property, _widget):
        #HACK: I'm sick of writing a different function for each property.
        setattr(self.script.metadata,property,_widget.value);
        self.script.scriptChanged();
        self.script.controls["file-button-save"].disabled= not self.script.unsaved;
        self.script.controls["file-button-save"].repaint();
    
    def changeLanguage(self):
        newLanguage= self.script.controls["file-button-language"].value
        global language
        language= newLanguage
        changeLanguage(newLanguage, languageCodes[languages.index(language)])
        sourceTab = self.sourceTab
        #sourceTab.changePanel()
        sourceTab.reload()
    
    def openNewDialog(self):
        self.newFile();
    def openLoadDialog(self):
        dialog = None
        special_button= None
        if hacks['xo']:
            t= gui.Table()
            t.tr()
            if self.script.journal:
                t.td(gui.Image("games/broadway/images/dialog-folders.png"))
                t.tr()
                t.td(gui.Label(_("Folders")))
            else:
                t.td(gui.Image("games/broadway/images/dialog-journal.png"))
                t.tr()
                t.td(gui.Label(_("Journal")))
            special_button = gui.Button(t)
            def closeAndLoad():
                dialog.close()
                self.script.refreshTheater()
                self.script.filepath = None
                self.script.journal = not self.script.journal
                self.openLoadDialog()
            special_button.connect(gui.CLICK, closeAndLoad)
        if self.script.journal:
            if self.script.filepath:
                loadName = self.script.filepath.metadata['title']
            elif self.script.metadata.title:
                loadName = self.script.metadata.title
            else:
                loadName = ""
            dialog = gui.JournalDialog(_("Open a script"),
                                  loadName,
                                  False,
                                  special_button=special_button)
            dialog.loadJournalItems(datastore.find({"mime_type" :"application/broadway"})[0])
        else:
            if self.script.filepath:
                loadName = os.path.basename(self.script.filepath)
            else:
                loadName = ""
            dialog = gui.FileDialog(_("Open a script"),
                               _("Okay"), 
                               path=directories['sample-scripts'], 
                               filter=[information['filetype']],
                               default= loadName,
                               favorites = defaults['favorites'],
                               special_button = special_button)
        dialog.open()
        dialog.connect(gui.CLOSE, self.script.refreshTheater);
        dialog.connect(gui.CHANGE, self.loadFile);
    def openSaveDialog(self):
        if self.script.filepath is not None:
            if self.script.journal:
                dsObject= self.script.filepath
                self.script.saveFile(directories['instance'] + 'temp.bdw')
                dsObject.set_file_path(self.script.filepath)
                datastore.write(dsObject)
            else:
                self.script.saveFile(self.script.filepath)
            self.script.controls["file-button-save"].disabled= not self.script.unsaved
            self.script.controls["file-button-save"].blur()
            self.script.controls["file-button-save"].repaint()
        else:   
            self.openSaveAsDialog();
    
    def openSaveAsDialog(self):
        dialog = None
        special_button= None
        if hacks['xo']:
            t= gui.Table()
            t.tr()
            if self.script.journal:
                t.td(gui.Image("games/broadway/images/dialog-folders.png"))
                t.tr()
                t.td(gui.Label(_("Folders")))
            else:
                t.td(gui.Image("games/broadway/images/dialog-journal.png"))
                t.tr()
                t.td(gui.Label(_("Journal")))
            special_button = gui.Button(t)
            def closeAndSaveAs():
                dialog.close()
                self.script.refreshTheater()
                self.script.filepath = None
                self.script.journal = not self.script.journal
                self.openSaveAsDialog()
            special_button.connect(gui.CLICK, closeAndSaveAs)
        if self.script.journal:
            if self.script.filepath:
                saveName = self.script.filepath.metadata['title']
            elif self.script.metadata.title:
                saveName = self.script.metadata.title
            else:
                saveName = ""
            dialog = gui.JournalDialog(_("Save a script"),
                                  saveName,
                                  True,
                                  special_button=special_button)
            dialog.loadJournalItems(datastore.find({"mime_type" : "application/broadway"})[0])
        else:
            if self.script.filepath:
                saveName = os.path.basename(self.script.filepath)
            else:
                saveName = filenameStrip(self.script.metadata.title) + information['filetype']
            dialog = gui.FileDialog(_("Save a script"),
                                    _("Okay"), 
                                    path=directories['export-folder'], 
                                    filter=[information['filetype']],
                                    default= saveName,
                                    favorites = defaults['favorites'],
                                    special_button = special_button)
        dialog.open()
        dialog.connect(gui.CLOSE, self.script.refreshTheater);
        dialog.connect(gui.CHANGE, self.saveFile);
    
    
    def confirmActionDialog(self, title, message, okayFunction=None, cancelFunction=None, arguments= None):
        d= gui.ConfirmDialog(title, message)
        d.connect(gui.CLOSE, self.script.refreshTheater);
        if okayFunction is not None: 
            def okayAndCloseFunction(arguments):
                okayFunction(arguments);
                d.close();
                self.script.controls["file-button-save"].disabled= not self.script.unsaved;
                self.script.controls["file-button-save"].repaint();
                self.refreshPanel();
            d.okayButton.connect(gui.CLICK, okayAndCloseFunction, arguments);
        else:
            d.okayButton.connect(gui.CLICK, d.close);
        if cancelFunction is not None: 
            def cancelAndCloseFunction(arguments):
                cancelFunction(arguments);
                d.close();
                self.script.controls["file-button-save"].disabled= not self.script.unsaved;
                self.script.controls["file-button-save"].repaint();
                self.refreshPanel();
            d.cancelButton.connect(gui.CLICK, cancelAndCloseFunction, arguments);
        else:
            d.cancelButton.connect(gui.CLICK, d.close);
        d.open()
    
    def saveFile(self, _widget):
        fullPath= _widget.value;
        if self.script.journal:
            if type(fullPath.actualValue) == str:
                dsObject= datastore.create()
                print dir(dsObject.metadata)
                dsObject.metadata.get_dictionary().update(self.autogenerateMetadata())
                dsObject.metadata['title']= fullPath.actualValue
                self.script.saveFile(directories['instance'] + 'temp.bdw')
                dsObject.set_file_path(self.script.filepath)
                datastore.write(dsObject)
                self.script.filepath = dsObject
            else:
                dsObject= fullPath.actualValue
                self.script.saveFile(directories['instance'] + 'temp.bdw')
                dsObject.set_file_path(self.script.filepath)
                datastore.write(dsObject)
                self.script.filepath = fullPath.actualValue
            self.refreshPanel();
        else:
            fileName, fileExtension= os.path.splitext(fullPath);
            if fileExtension != information['filetype']:
                fullPath+= information['filetype'];
            if os.path.isfile(fullPath):
                self.confirmActionDialog(_("Overwrite?"),
                                        [ _("This file already exists:"),
                                          os.path.basename(fullPath),
                                          _("Are you sure you want to overwrite it?")],
                                        okayFunction= self.script.saveFile, 
                                        arguments=fullPath);
            else:
                self.script.saveFile(fullPath);
    
    def loadFile(self, _widget):
        fullPath= _widget.value;
        if self.script.unsaved:
            self.confirmActionDialog(_("Lose Unsaved Changes?"),
                                    [ _("You have unsaved changes!"),
                                      _("Are you sure you want to load a  script?")],
                                    okayFunction= self.script.loadFile, 
                                    arguments=fullPath);
        else:
            if self.script.journal:
                if type(fullPath.actualValue) == str:
                    d= gui.InfoDialog(_("Error"), _("That title doesn't exist."));
                    d.connect(gui.CLOSE, self.script.refreshTheater);
                    d.open();
                else:
                    self.script.loadFile(fullPath.actualValue.get_file_path());
                    self.refreshPanel();
                    self.script.filepath = fullPath.actualValue
            else:
                self.script.loadFile(fullPath);
                self.refreshPanel();
                
    
    def newFile(self):
        if self.script.unsaved:
            self.confirmActionDialog(_("Lose Unsaved Changes?"),
                                    [ _("You have unsaved changes!"),
                                      _("Are you sure you want to start a new script?")],
                                    okayFunction= self.script.newFile);
        else:
            self.script.default();
            self.refreshPanel();
