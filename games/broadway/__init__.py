import broadway
import logging
logging.basicConfig(filename='log.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

launcher_info = {
    # The name to be printed in the menu
    "name" : "Broadway",
    # A shortname, to launch from the shell
    "short_name" : "broadway",
    # A function which should launch the game
    "launch_func": broadway.main,
    # The path to a preview image, 200x150px ideally.
    # Right now this is unused
    "preview" : "games/pong/images/preview.png"
    }
