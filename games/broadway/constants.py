import simplejson as json;
import time
import os, sys

import pygame;
from pygame.locals import *;

from broadway import hacks
from auxiliary import *;
import voice;

#_ = lambda x: x

TICKS_PER_SECOND = 30  # Frames Per Second
GAME_TITLE= 'Broadway';
GAME_RUNNING= True;

information= {};
information['name']= 'Broadway';
information['author']= 'Austin Cory Bart';
information['version']= 2.1;
information['filetype']= '.bdw';
information['description']= '';
information['credits']= _("Broadway by Austin Cory Bart\nGraphics by Margaret Spagnolo and various\nPGU by Phill Hassey and Peter Rogers\nSpyral by Robert Deaton\nPygame from various\nEspeak from various\nIcons from various\nBased on Hollywood, by Theatrix\nSpecial thanks to Dr.s Pollock, Harvey, Mouza, Glancey, and Burns.");

directions= ['left','right'];
verbs= Enumerate('SAY FEEL MOVE DO FACE EXIT ENTER START FOCUS');
tones= {'female' : ['f1','f2','f3','f4','f5'],
		 'male' : ['m1','m2','m3','m4','m4'], #m5 has an error or something
		 'other' : ['whisper', 'croak']};
pitches= {'low': 0, 'normal': 50, 'high': 99};
speed= {'slow': 100, 'normal': 150, 'fast': 180};
voices= [voice.Voice('Female 1', tones['female'][3], pitches['normal'], speed['normal']),
		 voice.Voice('Female 2', tones['female'][1], pitches['low'], speed['normal']),
		 voice.Voice('Female 3', tones['female'][1], pitches['high'], speed['normal']),
		 voice.Voice('Female 4', tones['female'][2], pitches['normal'], speed['normal']),
		 voice.Voice('Female 5', tones['female'][3], pitches['high'], speed['normal']),
		 voice.Voice('Female Fast', tones['female'][2], pitches['high'], speed['fast']),
		 voice.Voice('Female Slow', tones['female'][4], pitches['low'], speed['slow']),
		 voice.Voice('Whisper', tones['other'][0], pitches['normal'], speed['normal']),
		 voice.Voice('Male 1', tones['male'][3], pitches['normal'], speed['normal']),
		 voice.Voice('Male 2', tones['male'][0], pitches['low'], speed['normal']),
		 voice.Voice('Male 3', tones['male'][1], pitches['high'], speed['normal']),
		 voice.Voice('Male 4', tones['male'][2], pitches['normal'], speed['normal']),
		 voice.Voice('Male 5', tones['male'][3], pitches['high'], speed['normal']),
		 voice.Voice('Male Fast', tones['male'][2], pitches['high'], speed['fast']),
		 voice.Voice('Male Slow', tones['male'][4], pitches['low'], speed['slow']),
		 voice.Voice('Croaker', tones['other'][1], pitches['normal'], speed['normal']),
		];

class cues:
	BEGIN= 0;
	END= 1;
phases= Enumerate('BEGIN CONTINUE END');
empty= tuple();

pgu= {};
fonts= {};


images= {};
images['warning-icon']= os.path.join('games/broadway/images','dialog-warning.png');
images['main-background']= os.path.join('games/broadway/images', 'frame.png');
images['main-logo']= os.path.join('games/broadway/images', 'broadwayLogo-smaller.png');
images['main-panel']= os.path.join('games/broadway/images', 'panel.png');
images['main-tab']= os.path.join('games/broadway/images', 'tab.png');
images['go-first']= os.path.join('games/broadway/images','go-first.png');
images['go-back']= os.path.join('games/broadway/images','go-back.png');
images['go-next']= os.path.join('games/broadway/images','go-next.png');
images['go-last']= os.path.join('games/broadway/images','go-last.png');
images['list-add']= os.path.join('games/broadway/images','list-add.png');
images['media-first']= os.path.join('games/broadway/images','media-home.png');
images['media-backward']= os.path.join('games/broadway/images','media-backward.png');
images['media-forward']= os.path.join('games/broadway/images','media-forward.png');
images['media-last']= os.path.join('games/broadway/images','media-end.png');
images['media-play']= os.path.join('games/broadway/images','media-play.png');
images['media-pause']= os.path.join('games/broadway/images','media-pause.png');
images['teacher-backdrop']= os.path.join('games/broadway','teacher.jpeg');


times= {};
times['second']= 1;
times['half-second']= .5;
times['minute']= 60;
times['hour']= 3600;

colors= {};
colors['bg'] = (0x00, 0x00, 0x00);
colors['font'] = (0xFF, 0xFF, 0xFF);
colors['red'] = (0xFF, 0x00, 0x00);
colors['green'] = (0x00, 0xFF, 0x00);
colors['blue'] = (0x00, 0x00, 0xFF);
colors['white'] = (0xFF, 0xFF, 0xFF);
colors['black'] = (0x00, 0x00, 0x00);

geom= {};
pygame.display.init()
screen_height = pygame.display.Info().current_h
pygame.display.quit()
if screen_height < 900: offset= -35;
else: offset= 0;
geom['screen'] = Rect(0, 0, 1200, 900 )
#
# *-----------*-----*
# | Theater   | Tab |
# |           |     |
# *-----------*-----*
# | Panel           |
# *-----------------*
#
geom['frame']= Rect(0, 0+offset,  1200, 900);
geom['theater'] = Rect(75, 75+offset, 880, 495) #,75,,
geom['tab'] = Rect(955,75+offset, 170, 495) #,75,,
geom['panel'] = Rect(75, 570+offset, 1050, 255) #,570,,
geom['scriptArea'] = Rect(5, 20, 500-10, 255-30)
geom['scriptPanel'] = Rect(500+5+18, 20, 520, 255) # A glitch in PGU TextArea/ScriptArea requires the +18
geom['subtitle']= Rect(geom['theater'].width // 2, 
					   geom['theater'].height - 20,
					   geom['theater'].width * 3/4,
					   1);
geom['thumb']= Rect(0,0,40,40);
geom['text']= Rect(0,0,12, 18);

marks= {};
marks['offstage']= (-1000,-1000);
marks['offstage-left']= (-300, 350);
marks['offstage-right']= (geom['theater'].width+300, 350);
marks['houseLeft']= (0, 350);
marks['houseRight']= (800, 350);
marks['center']= (440, 247);
marks['narrator']= (-1,-1);

subtitleCode= {};
subtitleCode['italic']= '<<';
subtitleCode['normal']= '';
subtitleCode['ignore']= '>>';

graphicExtensions= ['jpg','jpeg','png','gif','bmp','pcx','tga','tif'];
backdrops= findValidBackdrops(graphicExtensions);
#backdrops.extend(backdrops);
#backdrops.extend(backdrops);
#backdrops.extend(backdrops);
actors= findValidActors();

limits= {};
limits['actors']= 6;

defaults= {};
defaults['actor']= 'nerd (brown)';
defaults['actorName']= _("Name");
defaults['voice']= voices[0];
defaults['voice-test']= _("Hello, I am currently speaking. How do I sound?");
defaults['position']= (200,350);
defaults['positions']= [(x*150+150, 350) for x in xrange(limits['actors']-1)];
defaults['mixer-frequency']= 22050;
defaults['mixer-size']= -16;
defaults['mixer-channels']= 2;
defaults['mixer-buffer']= 4096;
defaults['mouth-threshold']= 700;
defaults['mouth-range']= 200;
defaults['actor-speed']= 200 / 1; # pixels per second
defaults['actor-pause']= times['second'];
defaults['theater-skip']= 8;
defaults['backdrop']= 'tutorial';
if os.name == 'nt':
	defaults['favorites']= [('games/broadway/images/dialog-usb.png', _("USB"), r"C:\Users\acbart\Documents"),
							('games/broadway/images/dialog-star.png', _("Built-in"), r"C:\Users\acbart\Projects\broadway.activity\games\broadway"),
							('games/broadway/images/dialog-house.png', _("Home"), r"C:\Users\acbart")]
elif hacks['xo']:
	defaults['favorites']= [('games/broadway/images/dialog-usb.png', _("USB"), '/media/'),
							('games/broadway/images/dialog-star.png', _("Built-in"), '/home/olpc/Activities/broadway.activity/games/broadway'),
							('games/broadway/images/dialog-house.png', _("Home"), '/home/olpc/')]
else:
	defaults['favorites']= [('games/broadway/images/dialog-usb.png', _("USB"), '/media/'),
							('games/broadway/images/dialog-star.png', _("Built-in"), '/'),
							('games/broadway/images/dialog-house.png', _("Home"), '~/')]



# All the strings that don't show up naturally, to ensure that they're 
# automatically translated. This is probably a horrible way of doing this, but
# a better way wasn't immediately clear and I'm done investing time into this!
k = [_("Angry"), _("Annoyed"), _("Anxious"), _("Bored"), _("Cheerful"), _("Cocky"), 
     _("Distraught"), _("Embarrassed"), _("Excited"), _("Grumpy"), _("Guilty"), 
     _("Happy"), _("Joyful"), _("Loving"), _("Normal"), _("Sad"), _("Scared"), 
     _("Surprised"), _("Unhappy"), _("Worried"), _("Stands"), _("Left"), _("Right"), 
     _("Cheerleader (Blue)"), _("Cheerleader (Brown)"), _("Cheerleader (Pink)"), 
     _("Hippie (Brown)"), _("Hippie (Green)"), _("Hippie (Pink)"), _("Little girl (Brown)"), 
     _("Little girl (Peach)"), _("Little girl (Yellow)"), _("Narrator"), _("Nerd (Brown)"), 
     _("Nerd (Green)"), _("Nerd (Red)"), _("Princess (Blue)"), _("Princess (Green)"), 
     _("Princess (Peach)"), _("Basketball"), _("Beach"), _("Country"), _("Jungle"), 
     _("School"), _("Theater"), _("Tutorial"), _("Winter"), _("Female 1"), _("Female 2"), 
     _("Female 3"), _("Female 4"), _("Female 5"), _("Female Fast"), _("Female Slow"), 
     _("Whisper"), _("Male 1"), _("Male 2"), _("Male 3"), _("Male 4"), _("Male 5"), 
     _("Male Fast"), _("Male Slow"), _("Croaker"), _("File"), _("Backdrop"), 
     _("Actor"), _("Plan"), _("Write"), _("Theater"), _("Generic Panel"),
     _("Fancy"), _("Plain")]
del k

processes= {};
if os.name == 'nt':
	processes['espeak']= r"C:\Program Files (x86)\eSpeak\command_line\espeak.exe";
else:
	processes['espeak']= "espeak";
	
directories= {};
if os.name == 'nt':
	directories['temp']= 'games/broadway/';
else:
	directories['temp']= os.path.join('/','tmp/');
	#directories['temp']= os.path.join(activity.get_activity_root(), "tmp");
	#directories['sample-scripts']= os.path.join(activity.get_activity_root(), 'data');
directories['images'] = 'games/broadway/images'
directories['sample-scripts']= os.path.join('games/broadway', 'samples');
if os.name == 'nt':
	directories['export-folder']= "~\\"
else:
	directories['export-folder']= '/home/olpc/'
    
if hacks['xo']:
    try:
        import sugar.activity.activity
        directories['instance'] = os.path.join(sugar.activity.activity.get_activity_root(), 'instance/')
    except:
        directories['instance'] = 'games/broadway/'
else:
    directories['instance'] = 'games/broadway/'

def getTeacherList():
	try:
		rawTeacherList = requests.get(hacks['server']+"broadway.php", params={'action':'teachers'})
		if rawTeacherList.status_code == requests.codes.ok:
			teacherList= []
			for aTeacher in (rawTeacherList.content.rsplit('\n')):
				teacherList.append(aTeacher.rsplit('\t'))
			return teacherList
		else:
			print "Couldn't grab teacher file"
			return None
	except Exception, e:
		print "Connection Error", e
		return None

def downloadTeachersImage(username):
	imageData= requests.get(hacks['server']+"broadway.php", params={"action": "image", "teacher": username}, timeout=5)
	i = open(images['teacher-backdrop'], 'wb')
	i.write(imageData.content)
	i.close()

def uploadToTeacher(teacher, title, fancy, bdwPath, filePath):
	data= {"action" : "upload",
		   "teacher": teacher,
		   "story-name": title,
		   "time": str(time.time()),
		   "type": fancy}
	files= {"exported-file": open(filePath, "rb"),
			"broadway-file": open(bdwPath, "rb")}
	result= requests.post(url=hacks['server']+"broadway.php", data=data, files=files)