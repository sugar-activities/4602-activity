"""
"""
import pygame
from pygame.locals import *

from const import *
import widget, surface
import weakref, weakProxy;

class Container(widget.Widget):
	"""The base container widget, can be used as a template as well as stand alone.
	
	<pre>Container()</pre>
	"""
	def __init__(self,**params):
		widget.Widget.__init__(self,**params)
		self.myfocus = None
		self.mywindow = None
		self.myhover = None
		#self.background = 0
		self.widgets = []
		self.windows = []
		self.toupdate = {}
		self.topaint = {}
	
	def kill(self):
		widget.Widget.kill(self);
		for aWidget in self.widgets:
			aWidget.container= None;
			aWidget.kill();
		self.widgets= [];
		for aWindow in self.windows:
			aWindow.kill();
		self.windows= [];
		self.toupdate= {};
		self.topaint= {};
	
	def update(self,s):
		updates = []
		
		if self.myfocus and self.myfocus(): 
			self.toupdate[self.myfocus] = self.myfocus

		for w in self.topaint:
			if self.mywindow and w and w() is self.mywindow():
				continue
			else:
				sub = surface.subsurface(s,w().rect)
				sub.blit(w()._container_bkgr,(0,0))
				w().paint(sub)
				updates.append(pygame.rect.Rect(w().rect))
		
		for w in self.toupdate:
			if self.mywindow and w and w() is self.mywindow():
				continue
			else:			
				us = w().update(surface.subsurface(s,w().rect))
			if us:
				for u in us:
					updates.append(pygame.rect.Rect(u.x + w().rect.x,u.y+w().rect.y,u.w,u.h))
		
		for w in self.topaint:
			if self.mywindow and w and w() is self.mywindow():
				w().paint(self.top_surface(s,w()))
				updates.append(pygame.rect.Rect(w().rect))
			else:
				continue 
		
		for w in self.toupdate:
			if self.mywindow and w and w() is self.mywindow():
				us = w().update(self.top_surface(s,w()))
			else:			
				continue 
			if us:
				for u in us:
					updates.append(pygame.rect.Rect(u.x + w().rect.x,u.y+w().rect.y,u.w,u.h))
		
		self.topaint = {}
		self.toupdate = {}
		
		return updates
	
	def repaint(self,w=None):
		if not w:
			return widget.Widget.repaint(self)
		weakW= weakref.ref(w)
		self.topaint[weakW] = weakW
		self.reupdate()
	
	def reupdate(self,w=None):
		if not w:
			return widget.Widget.reupdate(self)
		weakW= weakref.ref(w);
		self.toupdate[weakW] = weakW
		self.reupdate()
	
	def paint(self,s):
		self.toupdate = {}
		self.topaint = {}
		
		for w in self.widgets:
			ok = False
			try:
				sub = surface.subsurface(s,w.rect)
				ok = True
			except: 
				print 'container.paint(): %s not in %s'%(w.__class__.__name__,self.__class__.__name__)
				print s.get_width(),s.get_height(),w.rect
				ok = False
			if ok: 
				if not (hasattr(w,'_container_bkgr') and w._container_bkgr.get_width() == sub.get_width() and w._container_bkgr.get_height() == sub.get_height()):
					w._container_bkgr = sub.copy()
				w._container_bkgr.fill((0,0,0,0))
				w._container_bkgr.blit(sub,(0,0))
				
				w.paint(sub)
		
		for w in self.windows:
			w.paint(self.top_surface(s,w))
	
	def top_surface(self,s,w):
		x,y = s.get_abs_offset()
		s = s.get_abs_parent()
		return surface.subsurface(s,(x+w.rect.x,y+w.rect.y,w.rect.w,w.rect.h))
	
	def event(self,e):
		used = False
		
		if self.mywindow and self.mywindow() and e.type == MOUSEBUTTONDOWN:
			w = self.mywindow()
			if self.myfocus and self.myfocus() is w:
				if not w.rect.collidepoint(e.pos): 
					self.blur(w)
			if not self.myfocus:
				if w.rect.collidepoint(e.pos): self.focus(w)
		
		if not self.mywindow:
			#### by Gal Koren
			##
			## if e.type == FOCUS:
			if e.type == FOCUS and not self.myfocus:
				#self.first()
				pass
			elif e.type == EXIT:
				if self.myhover and self.myhover(): self.exit(self.myhover())
			elif e.type == BLUR:
				if self.myfocus and self.myfocus(): self.blur(self.myfocus())
			elif e.type == MOUSEBUTTONDOWN:
				h = None
				for w in self.widgets:
					if not w.disabled: #focusable not considered, since that is only for tabs
						if w.rect.collidepoint(e.pos):
							h = w
							if (self.myfocus and self.myfocus() is not w) or (self.myfocus is None and w is not None): self.focus(w)
				if not h and (self.myfocus and self.myfocus()):
					self.blur(self.myfocus())
			elif e.type == MOUSEMOTION:
				if 1 in e.buttons:
					if self.myfocus and self.myfocus(): ws = [self.myfocus()]
					else: ws = []
				else: ws = self.widgets
				
				h = None
				for w in ws:
					if w.rect.collidepoint(e.pos):
						h = w
						if (self.myhover and self.myhover() is not w) or (self.myhover is None and w is not None): 
							self.enter(w)
				if not h and self.myhover and self.myhover():
					self.exit(self.myhover())
				if self.myhover: w = self.myhover()
				else: w= None
				
				if w and (not self.myfocus or w is not self.myfocus()):
					sub = pygame.event.Event(e.type,{
						'buttons':e.buttons,
						'pos':(e.pos[0]-w.rect.x,e.pos[1]-w.rect.y),
						'rel':e.rel})
					used = w._event(sub)
		
		if self.myfocus: w = self.myfocus()
		else: w= None;
		
		if w:
			sub = e
			
			if e.type == MOUSEBUTTONUP or e.type == MOUSEBUTTONDOWN:
				sub = pygame.event.Event(e.type,{
					'button':e.button,
					'pos':(e.pos[0]-w.rect.x,e.pos[1]-w.rect.y)})
				used = w._event(sub)
			elif e.type == CLICK and ((self.myhover and self.myhover() is w) or (self.myhover is None and w is None)):
				sub = pygame.event.Event(e.type,{
					'button':e.button,
					'pos':(e.pos[0]-w.rect.x,e.pos[1]-w.rect.y)})
				used = w._event(sub)
			elif e.type == CLICK: #a dead click
				pass
			elif e.type == MOUSEMOTION:
				sub = pygame.event.Event(e.type,{
					'buttons':e.buttons,
					'pos':(e.pos[0]-w.rect.x,e.pos[1]-w.rect.y),
					'rel':e.rel})
				used = w._event(sub)
			else:
				used = w._event(sub)
				
		if not used:
			if e.type is KEYDOWN:
				if e.key is K_TAB and self.myfocus and self.myfocus():
					if (e.mod&KMOD_SHIFT) == 0:
						self.myfocus().next()
					else:
						self.myfocus().previous()
					return True
				elif e.key == K_UP: 
					#self._move_focus(0,-1)
					return True
				elif e.key == K_RIGHT:
					#self._move_focus(1,0)
					return True
				elif e.key == K_DOWN:
					#self._move_focus(0,1)
					return True
				elif e.key == K_LEFT:
					#self._move_focus(-1,0)
					return True
		return used
		
	def _move_focus(self,dx_,dy_):
		if not self.myfocus: return
		myfocus = self.myfocus()
		
		from pgu.gui import App
		widgets = self._get_widgets(App.app)
		#if myfocus not in widgets: return
		#widgets.remove(myfocus)
		if myfocus() in widgets:
			widgets.remove(myfocus())
		rect = myfocus().get_abs_rect()
		fx,fy = rect.centerx,rect.centery
		
		def sign(v):
			if v < 0: return -1
			if v > 0: return 1
			return 0
		
		dist = []
		for w in widgets:
			wrect = w.get_abs_rect()
			wx,wy = wrect.centerx,wrect.centery
			dx,dy = wx-fx,wy-fy
			if dx_ > 0 and wrect.left < rect.right: continue
			if dx_ < 0 and wrect.right > rect.left: continue
			if dy_ > 0 and wrect.top < rect.bottom: continue
			if dy_ < 0 and wrect.bottom > rect.top: continue
			dist.append((dx*dx+dy*dy,w))
		if not len(dist): return
		dist.sort()
		d,w = dist.pop(0)
		w.focus()
		
	def _get_widgets(self,c):
		widgets = []
		if c.mywindow:
			widgets.extend(self._get_widgets(c.mywindow))
		else:
			for w in c.widgets:
				if isinstance(w,Container):
					widgets.extend(self._get_widgets(w))
				elif not w.disabled and w.focusable:
					widgets.append(w)
		return widgets
	
	def remove(self,w):
		"""Remove a widget from the container.
		
		<pre>Container.remove(w)</pre>
		"""
		self.blur(w)
		self.widgets.remove(w)
		#self.repaint()
		self.chsize()
	
	def removeAll(self):
		"""Remove all widget from the container.
		
		<pre>Container.removeAll()</pre>
		"""
		for w in self.widgets:
			self.blur(w)
			self.widgets.remove(w)
			#self.repaint()
			self.chsize()
	
	def clear(self):
		""" Not only removes any widgets, but ensures that they and their
		children are fully removed from the ecosystem """
		for w in self.widgets:
			self.blur(w);
			self.chsize();
			if isinstance(w, Container):
				w.clear();
		self.widgets= [];
	
	def add(self,w,x,y):
		"""Add a widget to the container.
		
		<pre>Container.add(w,x,y)</pre>
		
		<dl>
		<dt>x, y<dd>position of the widget
		</dl>
		"""
		w.style.x = x
		w.style.y = y 
		w.container = weakref.ref(self)
		#NOTE: this might fix it, sort of...
		#but the thing is, we don't really want to resize
		#something if it is going to get resized again later
		#for no reason...
		#w.rect.x,w.rect.y = w.style.x,w.style.y
		#w.rect.w, w.rect.h = w.resize()
		self.widgets.append(w)
		self.chsize()
	
	def open(self,w=None,x=None,y=None):
		from app import App #HACK: I import it here to prevent circular importing
		if not w:
			if (not hasattr(self,'container') or not self.container()) and self is not App.app:
				self.container = weakref.ref(App.app)
			#print 'top level open'
			return widget.Widget.open(self)
		
		if self.container and self.container():
			if x != None: return self.container().open(w,self.rect.x+x,self.rect.y+y)
			return self.container().open(w)
		
		w.container = weakref.ref(self)
		
		if w.rect.w == 0 or w.rect.h == 0: #this might be okay, not sure if needed.
			#_chsize = App.app._chsize #HACK: we don't want this resize to trigger a chsize.
			w.rect.w,w.rect.h = w.resize()
			#App.app._chsize = _chsize
		
		if x == None or y == None: #auto center the window
			#w.style.x,w.style.y = 0,0
			w.rect.x = (self.rect.w-w.rect.w)/2
			w.rect.y = (self.rect.h-w.rect.h)/2
			#w.resize()
			#w._resize(self.rect.w,self.rect.h)
		else: #show it where we want it
			w.rect.x = x
			w.rect.y = y
			#w._resize()
		
		self.windows.append(w)
		self.mywindow = weakref.ref(w)
		self.focus(w)
		self.repaint(w)
		w.send(OPEN)
	
	def close(self,w=None):
		if not w:
			return widget.Widget.close(self)
			
		if self.container and self.container(): #make sure we're in the App
			return self.container().close(w)
		
		if self.myfocus and self.myfocus() is w: 
			self.blur(w)
		
		if w not in self.windows: return #no need to remove it twice! happens.
		
		self.windows.remove(w)
		
		self.mywindow = None
		if self.windows:
			self.mywindow = weakref.ref(self.windows[-1])
			self.focus(self.mywindow())
		
		if not self.mywindow:
			self.myfocus = weakref.ref(self.widget) #HACK: should be done fancier, i think..
			if not self.myhover:
				self.enter(self.widget)
		 
		self.repaintall()
		w.send(CLOSE)
	
	def focus(self,w=None):
		widget.Widget.focus(self) ### by Gal koren
#		if not w:
#			return widget.Widget.focus(self)
		if not w: return
		if self.myfocus and self.myfocus(): self.blur(self.myfocus())
		if (not self.myhover) or (self.myhover and self.myhover() is not w):
			self.enter(w)
		self.myfocus = weakref.ref(w)
		w._event(pygame.event.Event(FOCUS))
		
		#print self.myfocus,self.myfocus.__class__.__name__
	
	def blur(self,w=None):
		if not w:
			return widget.Widget.blur(self)
		if self.myfocus and self.myfocus() is w:
			if self.myhover and self.myhover() is w: self.exit(w)
			self.myfocus = None
			w._event(pygame.event.Event(BLUR))
	
	def enter(self,w):
		if self.myhover and self.myhover(): self.exit(self.myhover())
		self.myhover = weakref.ref(w)
		w._event(pygame.event.Event(ENTER))
	
	def exit(self,w):
		if self.myhover and self.myhover() is w:
			self.myhover = None
			w._event(pygame.event.Event(EXIT))	
	
	
#	 def first(self):
#		 for w in self.widgets:
#			 if w.focusable:
#				 self.focus(w)
#				 return
#		 if self.container: self.container.next(self)
	
#	 def next(self,w):
#		 if w not in self.widgets: return #HACK: maybe.  this happens in windows for some reason...
#		 
#		 for w in self.widgets[self.widgets.index(w)+1:]:
#			 if w.focusable:
#				 self.focus(w)
#				 return
#		 if self.container: return self.container.next(self)
	
	
	def _next(self,orig=None):
		start = 0
		if orig in self.widgets: start = self.widgets.index(orig)+1
		for w in self.widgets[start:]:
			if not w.disabled and w.focusable:
				if isinstance(w,Container):
					if w._next():
						return True
				else:
					self.focus(w)
					return True
		return False
	
	def _previous(self,orig=None):
		end = len(self.widgets)
		if orig in self.widgets: end = self.widgets.index(orig)
		ws = self.widgets[:end]
		ws.reverse()
		for w in ws:
			if not w.disabled and w.focusable:
				if isinstance(w,Container):
					if w._previous():
						return True
				else:
					self.focus(w)
					return True
		return False
				
	def next(self,w=None):
		if w != None and w not in self.widgets: return #HACK: maybe.  this happens in windows for some reason...
		
		if self._next(w): return True
		if self.container and self.container(): return self.container().next(self)
	
	
	def previous(self,w=None):
		if w != None and w not in self.widgets: return #HACK: maybe.  this happens in windows for some reason...
		
		if self._previous(w): return True
		if self.container and self.container(): return self.container().previous(self)
	
	def resize(self,width=None,height=None):
		#r = self.rect
		#r.w,r.h = 0,0
		ww,hh = 0,0
		if self.style.width: ww = self.style.width
		if self.style.height: hh = self.style.height
		
		for w in self.widgets:
			#w.rect.w,w.rect.h = 0,0
			w.rect.x,w.rect.y = w.style.x,w.style.y
			w.rect.w, w.rect.h = w.resize()
			#w._resize()
			
			ww = max(ww,w.rect.right)
			hh = max(hh,w.rect.bottom)
		return ww,hh
