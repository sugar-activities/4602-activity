from gettext import gettext as _
import sys
import gtk
import pygame
import os
import sugar.activity.activity
import sugar.graphics.toolbutton

sys.path.insert(0, os.path.abspath("libraries"))
import sugargame.canvas
import games
import spyral

# Modify this to change the name of your game
game = 'broadway'

class Activity(sugar.activity.activity.Activity):
    def __init__(self, handle):
        super(Activity, self).__init__(handle)
        self.paused = False
        
        self._pygamecanvas = sugargame.canvas.PygameCanvas(self)
        self.set_canvas(self._pygamecanvas)
        self._pygamecanvas.grab_focus()
        
        def run():
            launch = games.load_module(game).launcher_info['launch_func']
            spyral.director.init((1200,900), fullscreen = False, max_fps = 30, caption=game)
            launch()
            spyral.director.run_sugar()
            
        self._pygamecanvas.run_pygame(run)

    def read_file(self, file_path):
        pass

    def write_file(self, file_path):
        pass

def main():
    launch = games.load_module(game).launcher_info['launch_func']
    spyral.director.init((0,0), fullscreen = False, max_fps = 30, caption=game)
    launch()
    try:
        spyral.director.run()
    except KeyboardInterrupt:
        pygame.quit()

if __name__ == '__main__':
    main()