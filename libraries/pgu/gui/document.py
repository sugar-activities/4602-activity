"""
"""
import pygame

import weakref, weakProxy;
import container
import layout

class _document_widget:
	def __init__(self,w,align=None):
		#w.rect.w,w.rect.h = w.resize()
		#self.rect = w.rect
		self.widget = w
		if align != None: self.align = align
	
	def kill(self):
		if self.widget:
			self.widget.kill();
			self.widget= None;
	
	def clear(self):
		if self.widget:
			self.widget= None;

class Document(container.Container):
	"""A document container contains many widgets strung together in a document format.  (How informative!)
	By which they mean, left-to-right until the end of the line (or a "br"), and then down the page.
	You can also use spacers to add gaps.
	
	<pre>Document()</pre>
	
	"""
	def __init__(self,**params):
		params.setdefault('cls','document')
		container.Container.__init__(self,**params)
		self.layout =  layout.Layout(pygame.Rect(0,0,self.rect.w,self.rect.h))
	
	def kill(self):
		container.Container.kill(self);
		self.layout= None;
	
	def add(self,e,align=None):
		"""Add a widget.
		
		<pre>Document.add(e,align=None)</pre>
		
		<dl>
		<dt>e<dd>widget
		<dt>align<dd>alignment (None,-1,0,1)
		</dl>
		"""
		dw = _document_widget(e,align)
		self.layout.add(dw)
		e.container = weakref.ref(self)
		e._c_dw = weakref.ref(dw)
		self.widgets.append(e)
		self.chsize()
		
	def remove(self,e):
		self.layout._widgets.remove(e._c_dw())
		self.widgets.remove(e)
		self.chsize()
	
	def clear(self):
		for aWidget in self.layout._widgets:
			aWidget.clear();
		self.layout._widgets= [];
		for w in self.widgets:
			self.blur(w);
			self.chsize();
			if isinstance(w, container.Container):
				w.clear();
		self.chsize()
	
	def block(self,align):
		"""Start a new block.
		
		<pre>Document.block(align)</pre>
		
		<dl>
		<dt>align<dd>alignment of block (-1,0,1)
		</dl>
		"""
		self.layout.add(align)
	
	def space(self,e):
		"""Add a spacer.
		
		<pre>Document.space(e)</pre>
		
		<dl>
		<dt>e<dd>a (w,h) size for the spacer
		</dl>
		"""
		self.layout.add(e)
	
	def br(self,height):
		"""Add a line break.
		
		<pre>Document.br(height)</pre>
		
		<dl>
		<dt>height<dd>height of line break
		</dl>
		"""
		self.layout.add((0,height))
	
	def resize(self,width=None,height=None):
		if self.style.width: width = self.style.width
		if self.style.height: height = self.style.height
		
		for w in self.widgets:
			w.rect.w,w.rect.h = w.resize()
			
			if (width != None and w.rect.w > width) or (height != None and w.rect.h > height):
				w.rect.w,w.rect.h = w.resize(width,height)
			
			dw = w._c_dw()
			dw.rect = pygame.Rect(0,0,w.rect.w,w.rect.h)
		
		if width == None: width = 65535
		self.layout.rect = pygame.Rect(0,0,width,0)
		self.layout.resize()
		
		_max_w = 0
		
		for w in self.widgets:
			#xt,xl,xb,xr = w.getspacing()
			dw = w._c_dw()
			w.style.x,w.style.y,w.rect.w,w.rect.h = dw.rect.x,dw.rect.y,dw.rect.w,dw.rect.h
			#w.resize()
			w.rect.x,w.rect.y = w.style.x,w.style.y
			_max_w = max(_max_w,w.rect.right)
		
		#self.rect.w = _max_w #self.layout.rect.w
		#self.rect.h = self.layout.rect.h
		#print 'document',_max_w,self.layout.rect.h
		return _max_w,self.layout.rect.h
