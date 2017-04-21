import pygame
import spyral

import weakref;

#_ = lambda x: x

from constants import *;

class Action(object):
    """
    Represents an Action performed by an Actor. Each Action is described by
    a subject and verb, and optionally has objects.
    E.g. 
    | Action(anActor, verbs.FEEL, 'sad')
    | Action(anActor, verbs.MOVE, (100, 200))
    | Action(anActor, verbs.EXIT, 'left')
    | Action(anActor, verbs.DO, 'stands')
    | Action(anActor, verbs.FOCUS, None)
    """
    def __init__(self, subject, verb, objects):
        """
        Initializes the Action
        
        | *subject* is the Actor that is performing.
        | *verb* is the Action being performed, one of the constants in the enumeration *verbs*.
        | *objects* can be any of a number of things depending on the verb, including None.
        """
        self.verb= verb;
        self.subject= subject;
        self.objects= objects;
    
    def encodeJSON(self):
        """ 
        Encodes the object in a JSON-friendly format (dictionary) and returns it.
        """
        output= {};
        output['Subject']= id(self.subject);
        output['Verb']= self.verb;
        output['Objects']= self.objects;
        return output;
    
    @classmethod
    def decodeJSON(cls, input, actorMap):
        """
        Class method that decodes a JSON-created object into an Action and returns it.
        Requires a dictionary mapping the encoded Actor IDs and new Actor objects.
        """
        subject= actorMap[safeStr(input['Subject'])];
        verb= safeStr(input['Verb']);
        objects= safeStr(input['Objects']);
        return Action(subject, verb, objects);
    
    def getStateChange(self):
        """
        Returns the aspects of a state that would be changed if this action
        were to be applied to it.
        """
        if self.verb == verbs.MOVE:    return True, False, False, False;
        elif self.verb == verbs.FEEL:  return False, True, False, False;
        elif self.verb == verbs.DO:    return False, False, True, False;
        elif self.verb == verbs.FACE:  return False, False, False, True;
        elif self.verb == verbs.EXIT:  return True, False, False, False;
        elif self.verb == verbs.ENTER: return True, False, False, False;
        elif self.verb == verbs.FOCUS: return False, False, False, False;
        elif self.verb == verbs.START: return False, False, False, False;
        elif self.verb == verbs.SAY:   return False, False, False, False;
        else:                          return False, False, False, False;
    
    def isSameType(self, other):
        """
        Tests if this action has the same verb and subject as the *other* action.
        The verbs MOVE, EXIT, and ENTER are considered to be the same.
        """
        movements= [verbs.MOVE, verbs.EXIT, verbs.ENTER];
        isSameVerb= ((self.verb == other.verb) or (self.verb in movements and 
                                                   other.verb in movements));
        isSameSubject= (self.subject == other.subject);
        return isSameVerb and isSameSubject;
    
    def toText(self):
        """
        Returns a string representation of this Action that can be inserted
        into a ScriptArea.
        """
        if self.verb == verbs.FEEL:
            return _("<Looks %(expression)s>") % {"expression" : _(self.objects)}
        elif self.verb == verbs.MOVE:
            return _("<Moves>")
        elif self.verb == verbs.DO:
            return _("<%(action)s>") % {"action" : _(self.objects).capitalize()}
        elif self.verb == verbs.FACE:
            return _("<Faces %(direction)s>") % {"direction" : _(self.objects)}
        elif self.verb == verbs.EXIT:
            return _("<Exits %(direction)s>") % {"direction" : _(self.objects)}
        elif self.verb == verbs.ENTER:
            if self.objects == marks['houseLeft']:
                return _("<Enters left>");
            else:
                return _("<Enters right>");
        elif self.verb == verbs.FOCUS:
            return _("\n[%(name)s]\t") % {"name" : self.subject.name}
        elif self.verb == verbs.SAY:
            return _("<Say %(speech)s>") % {"speech" : self.objects}
        else:
            return _("<Error>");
    
    def toPrettyText(self):
        """
        Returns a pretty string representation of this Action that can be printed
        to the user.
        """
        if self.verb == verbs.FEEL:
            return _("<Looks %(expression)s>") % {"expression" : _(self.objects)};
        elif self.verb == verbs.MOVE:
            return _("<Moves>");
        elif self.verb == verbs.DO:
            return _("<%(action)s>") % _(self.objects).capitalize();
        elif self.verb == verbs.FACE:
            return _("<Faces %(direction)s>") % {"direction" : _(self.objects)}
        elif self.verb == verbs.EXIT:
            return _("<Exits %(direction)s>") % {"direction": _(self.objects)}
        elif self.verb == verbs.ENTER:
            if self.objects == marks['houseLeft']:
                return _("<Enters left>");
            else:
                return _("<Enters right>");
        elif self.verb == verbs.FOCUS:
            return _("\n%(name)s: ") % {"name" : self.subject.name}
        elif self.verb == verbs.SAY:
            return self.objects
        else:
            return "";
    
    def toHTML(self):
        """
        Returns a pretty string representation of this Action that can be printed
        to the user.
        """
        if self.verb == verbs.FEEL:
            return _("<em>&lt;Looks %(expression)s&gt;</em>") % {"expression" : (self.objects)}
        elif self.verb == verbs.MOVE:
            return _("<em>&lt;Moves&gt;</em>")
        elif self.verb == verbs.DO:
            return _("<em>&lt;%(action)s&gt;</em>") % {"action" : _(self.objects).capitalize()}
        elif self.verb == verbs.FACE:
            return _("<em>&lt;Faces %(direction)s&gt;</em>") % {"direction " : _(self.objects)}
        elif self.verb == verbs.EXIT:
            return _("<em>&lt;Exits %(direction)s&gt;</em>") % {"direction" : _(self.objects)}
        elif self.verb == verbs.ENTER:
            if self.objects == marks['houseLeft']:
                return _("<em>&lt;Enters left&gt;</em>");
            else:
                return _("<em>&lt;Enters right&gt;</em>");
        elif self.verb == verbs.FOCUS:
            return _("<br>\n<strong>%(name)s</strong>:&nbsp;") % {"name" : self.subject.name}
        elif self.verb == verbs.SAY:
            return self.objects
        else:
            return "";
    
    def __str__(self):
        """
        Returns a string representation of this Action that can reveal
        detailed information about the Action.
        """
        if self.verb == verbs.FEEL:
            return "<%(name)s, LOOKS, %(expression)s>" % {"name": self.subject.name, 
                                                          "expression" : str(self.objects)}
        elif self.verb == verbs.MOVE:
            return "<%(name)s, MOVES, %(position)s>" % {"name": self.subject.name, 
                                                        "position" : str(self.objects)}
        elif self.verb == verbs.DO:
            return "<%(name)s, DOES, %(action)s>" % {"name": self.subject.name, 
                                                     "action": str(self.objects)}
        elif self.verb == verbs.FACE:
            return "<%(name)s, FACES, %(direction)s>" % {"name": self.subject.name, 
                                                         "direction": str(self.objects)}
        elif self.verb == verbs.EXIT:
            return "<%(name)s, EXITS, %(direction)s>" % {"name": self.subject.name, 
                                                         "direction" : str(self.objects)}
        elif self.verb == verbs.ENTER:
            if self.objects == marks['houseLeft']:
                return "<%(name)s, FACES, LEFT>" % {"name": self.subject.name}
            else:
                return "<%(name)s, FACES, RIGHT>" % {"name": self.subject.name}
        elif self.verb == verbs.FOCUS:
            return "<%(name)s, FOCUSES, %(something)s>" % {"name": self.subject.name, 
                                                           "something": str(self.objects)}
        elif self.verb == verbs.START:
            return "<%(name)s, STARTS, %(something)s>" % {"name": self.subject.name, 
                                                          "something": str(self.objects)}
        elif self.verb == verbs.SAY:
            return "<%(name)s, SAYS, %(speech)s>" % {"name": self.subject.name, 
                                                     "speech" : str(self.objects)}
        else:
            return "<%(name)s, %(verb)s, %(objects)s>" % {"name": self.subject.name, 
                                                          "verb" : str(self.verb), 
                                                          "objects" : str(self.objects)}
    
    def toSubtitle(self):
        """
        Returns a string representation of this Action that can be rendered
        by a Subtitler.
        """
        if self.verb == verbs.FEEL:
            return subtitleCode['italic'], self.subject.name, _("Looks %(expression)s.") % {"expression": _(self.objects)}
        elif self.verb == verbs.MOVE:
            return subtitleCode['italic'],self.subject.name, _("Moves.");
        elif self.verb == verbs.DO:
            return subtitleCode['italic'],self.subject.name, _("%(action)s.") % {"action" : _(self.objects).capitalize()}
        elif self.verb == verbs.FACE:
            return subtitleCode['italic'],self.subject.name, _("Faces %(direction)s.") % {"direction" : _(self.objects)}
        elif self.verb == verbs.EXIT:
            return subtitleCode['italic'],self.subject.name, _("Exits %(direction)s.") % {"direction" : _(self.objects)}
        elif self.verb == verbs.ENTER:
            if self.objects == marks['houseLeft']:
                return subtitleCode['italic'],self.subject.name, _("Enters left.")
            else:
                return subtitleCode['italic'],self.subject.name, _("Enters right.")
        elif self.verb == verbs.FOCUS:
            return subtitleCode['ignore'],"","";
        elif self.verb == verbs.START:
            return subtitleCode['ignore'],"","";
        elif self.verb == verbs.SAY:
            if self.objects.strip():
                return subtitleCode['normal'], self.subject.name, self.objects.strip();
            else:
                return subtitleCode['ignore'],"","";
        else:
            return subtitleCode['ignore'];