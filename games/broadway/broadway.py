# System Imports
import random
import time
import os, sys, glob
import locale

# Top-most globals
import simplejson as json;
settingsData= json.load(open('games/broadway/settings.txt', 'r'))
hacks= {};
hacks['mute']= settingsData['Mute'];
hacks['recording']= False
hacks['teacher']= settingsData['Teacher']
hacks['subtitle']= settingsData['Subtitle']
hacks['server']= settingsData['Server']
hacks['language']= settingsData['Language']
hacks['xo']= not bool(sys.platform == 'linux2')

# Localization
import gettext;

gtlanguage = gettext.translation('broadway', 'games/broadway/po', languages=[hacks['language']])
gtlanguage.install()
_ = gettext.gettext

#import cProfile
#from guppy import hpy; hp = hpy();


# Pygame Imports
import pygame
from pygame.locals import *

# Spyral Import
import spyral

# PGU Imports
from pgu import text
from pgu import gui
from pgu import html

# System setting manipulations
os.environ['SDL_VIDEO_CENTERED'] = '1'
#os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (25, -75)

# First Broadway Imports
from auxiliary import *;
from constants import *;


pgu['theme']= gui.Theme('libraries/pgu/gui.theme');
fonts['normal']= pygame.font.SysFont('Vera.ttf', 30);
fonts['italic']= pygame.font.SysFont('VeraIt.ttf', 30);

# Last Broadway Imports
import script;
import panel
import tab
import actor;
from recorder import Recorder


class Broadway(spyral.scene.Scene):
	def __init__(self):
		"""Initializes cameras"""
		spyral.scene.Scene.__init__(self)
		self.rootCamera = spyral.director.get_camera()
		self.screenCamera=  self.rootCamera.make_child();
		self.theaterCamera= self.rootCamera.make_child(virtual_size= geom['theater'].size,
													real_size= geom['theater'].size,
													offset= geom['theater'].topleft,
													layers=['upstage','stage','faces','downstage']);
		self.recorder= Recorder()
		self.preventEscapeLock = False
	def on_enter(self):
		"""Create the Theater"""
		# The theater is the Sypral Group responsible for holding the
		# backdrop, actors, and subtitler. It is held by the Script.
		self.theater = spyral.sprite.Group(self.theaterCamera)
		
		bg = spyral.util.new_surface(geom['screen'].size)
		bg.fill(colors['bg'])
		self.screenCamera.set_background(bg)
		
		self.script= script.Script();
		self.script.setTheater(self.theater);
		self.script.setRecorder(self.recorder)
		self.script.default();
		
		self.gui = gui.App(theme=pgu['theme'])
		self.guiContainer = gui.Container(align=-1, 
										  valign=-1)
		if geom['frame'] != geom['screen']:
			images['main-background']= spyral.util.load_image(images['main-background']);
			croppedFrame= spyral.util.new_surface(geom['screen'].size);
			croppedFrame.blit(images['main-background'], geom['frame'], area=geom['screen']);
			images['main-background']= croppedFrame;
		self.guiContainer.add(gui.Image(images['main-background']),
                              *geom['screen'].topleft);
		self.guiContainer.add(gui.Image(images['main-tab']),
							  *geom['tab'].topleft);
		
		
		
		# Tab is used to switch between the different panels
		self.tab= tab.Tab(self.script);
		
		# Add the tab and panel holder to the screen
		self.guiContainer.add(self.tab, *geom['tab'].topleft);
		self.guiContainer.add(self.tab.panelHolder, *geom['panel'].topleft);
		
		self.script.gui = self.gui
		
		self.gui.init(self.guiContainer);
		
		#self.recorder.startRecording()
				
	def render(self):
		"""
		The render function should call .draw() on the scene's group(s) and
		camera(s). Unless your game logic should be bound by framerate,
		logic should go elsewhere.
		"""
		self.theater.draw()
		if self.recorder.recording == 'Video':
			changes = self.rootCamera.draw(True)
			self.recorder.addFrame(changes)
		else:
			self.rootCamera.draw(False)
		
		dirtyGui= self.gui.update(pygame.display.get_surface());
		if dirtyGui:
			pygame.display.update(dirtyGui);
	
	def confirmQuit(self, okayCallback):
		self.script.disableControls()
		def quit():
			self.script.enableControls()
			self.script.refreshTheater()
			self.preventEscapeLock= False
		d= gui.ConfirmDialog(_("Confirm Quit"), [_("You have unsaved changes!"),
												 _("If you quit now, you'll lose them forever!"),
												 _("Are you sure you want to quit?")])
		d.connect(gui.CLOSE, quit);
		d.okayButton.connect(gui.CLICK, okayCallback)
		self.preventEscapeLock= True
		d.open();
	
	def update(self, tick):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				# Check if quit
				if self.script.unsaved:
					self.confirmQuit(spyral.director.pop)
				else:
					spyral.director.pop()
			elif event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					if self.script.unsaved:
						self.confirmQuit(spyral.director.pop)
					else:
						spyral.director.pop()
				elif self.tab.activePanel.name == "Write" and not self.preventEscapeLock:
					self.tab.activePanel.scriptArea.focus()
			elif event.type == VIDEOEXPOSE:
				self.gui.repaintall()
				self.render()
			elif event.type == MOUSEBUTTONDOWN:
				fixedPosition= self.theaterCamera.world_to_local(event.pos);
				if fixedPosition:
					self.tab.activePanel.handleGlobalMouse(fixedPosition, event.button);
			self.gui.event(event)
		
		self.script.director.handleAction();
	
		self.theater.update()

def main():
	spyral.director.push(Broadway())

def mainSugarless():
	spyral.director.init(geom['screen'].size, fullscreen = False, max_fps = 30, caption='Broadway')
	spyral.director.push(Broadway())
	spyral.director.run()
	
if __name__ == "__main__":
	main()