### Minigame Test Launcher
## This file implements a minimal launcher which immediately allows you to
## launch into a specific minigame (via a commandline option), or see the
## usual minigame launcher, with a test user predefined, so that the tedious
## process of logging in and out can be avoided

import sys
import os
sys.path.insert(0, os.path.abspath("libraries"))

import games
import pygame
from optparse import OptionParser
import cProfile

import spyral

if __name__ == '__main__':	
	try:
		from games.broadway import broadway
		broadway.mainSugarless()
	except KeyboardInterrupt:
		pygame.quit()