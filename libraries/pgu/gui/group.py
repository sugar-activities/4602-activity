"""
"""
from const import *
import widget

class Group(widget.Widget):
	"""An object for grouping together Form elements.
	
	<pre>Group(name=None,value=None)</pre>
	
	<dl>
	<dt>name<dd>name as used in the Form
	<dt>value<dd>values that are currently selected in the group
	</dl>
	
	<p>See [[gui-button]] for several examples.</p>
	
	<p>When the value changes, an <tt>gui.CHANGE</tt> event is sent.
	Although note, that when the value is a list, it may have to be sent by hand via
	<tt>g.send(gui.CHANGE)</tt></p>
	"""
	
	def __init__(self,name=None,value=None):
		widget.Widget.__init__(self,name=name,value=value)
		self.widgets = []
	
	def kill(self):
		widget.Widget.kill(self);
		for aWidget in self.widgets:
			aWidget.kill();
		self.widgets= [];
	
	def add(self,w):
		"""Add a widget to this group.
		
		<pre>Group.add(w)</pre>
		"""
		self.widgets.append(w)
	
	def __setattr__(self,k,v, silent=False):
		_v = self.__dict__.get(k,NOATTR)
		self.__dict__[k] = v
		if k == 'value' and _v != NOATTR and _v != v and not silent:
			self._change()
	
	def _change(self):
		self.send(CHANGE)
		for w in self.widgets:
			w.repaint()
		
	def change(self, value):
		self.__setattr__('value',value, True);
		for w in self.widgets:
			w.checkState()
			w.repaint();
		
	def remove(self, w):
		self.widgets.remove(w);
	
	def kill(self):
		widget.Widget.kill(self);
		for aWidget in self.widgets:
			aWidget.kill();