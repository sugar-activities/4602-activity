"""
"""
import os

from const import *
import table, area, document
import basic, input, button

try:
    from sugar.datastore import datastore
except:
    class datastore(object):
        class DSObject(object):
            def __init__(self, name):
                self.metadata = {'title' : name}
        @staticmethod
        def create():
            return DSObject()
        @staticmethod
        def write(ds_object):
            pass
        @staticmethod
        def find(query, sorting=None):
            names = ["Sample Story", "The Beach", "Monochrome No Kiss"]
            return [DSObject(name) for name in names]

class Dialog(table.Table):
    """A dialog window with a title bar and an "close" button on the bar.
    
    <pre>Dialog(title,main)</pre>
    
    <dl>
    <dt>title<dd>title widget, usually a label
    <dt>main<dd>main widget, usually a container
    </dl>
    
    <strong>Example</strong>
    <code>
    title = gui.Label("My Title")
    main = gui.Container()
    #add stuff to the container...
    
    d = gui.Dialog(title,main)
    d.open()
    </code>
    """
    def __init__(self,title,main,**params):
        params.setdefault('cls','dialog')
        table.Table.__init__(self,**params)
        
        
        self.tr()
        self.td(title,align=-1,cls=self.cls+'.bar')
        clos = button.Icon(self.cls+".bar.close")
        clos.connect(CLICK,self.close,None) 
        self.td(clos,align=1,cls=self.cls+'.bar')
        
        self.tr()
        self.td(main,colspan=2,cls=self.cls+".main")
        
#         self.tr()
#         
#         
#         t = table.Table(cls=self.cls+".bar")
#         t.tr()
#         t.td(title)
#         clos = button.Icon(self.cls+".bar.close")
#         t.td(clos,align=1)
#         clos.connect(CLICK,self.close,None) 
#         self.add(t,0,0)
#         
#         main.rect.w,main.rect.h = main.resize()
#         clos.rect.w,clos.rect.h = clos.resize()
#         title.container.style.width = main.rect.w - clos.rect.w
#         
#         self.tr()
#         self.td(main,cls=self.cls+".main")
# 

class InfoDialog(Dialog):
    def __init__(self,title,body,width= 400, **params):
        title= basic.Label(title);
        creditsLabel= basic.WidthLabel(value=body, width=width);
        creditsExit = button.Button("Okay", style = {'width' : 80, 'height': 40});
        creditsExit.connect(CLICK, self.close);
        creditsPanel= document.Document();
        creditsPanel.add(creditsLabel);
        creditsPanel.br(10)
        creditsPanel.br(4)
        creditsPanel.space((width // 2 - 40,4));
        creditsPanel.add(creditsExit);
        Dialog.__init__(self, title, creditsPanel)

class TeacherDialog(Dialog):
    def __init__(self):
        self.list = area.List(width=350, height=150)
        okButton = button.Button("Okay", style={'width': 80, 'height': 28, 'margin':8})
        okButton.connect(CLICK, self.okayClicked)
        cancelButton = button.Button("Cancel", style={'width': 80, 'height': 28, 'margin':8})
        cancelButton.connect(CLICK, self.close)
        body = table.Table()
        body.tr()
        body.td(basic.Label("Select your teacher"), colspan= 2)
        body.tr()
        body.td(self.list, colspan= 2)
        body.tr()
        body.td(okButton)
        body.td(cancelButton)
        Dialog.__init__(self, basic.Label("Teachers"), body)
    
    def loadTeachers(self, teachers):
        for username, name in teachers:
            self.list.add(name, value=username)
    
    def okayClicked(self):
        if self.list.value:
            self.value = self.list.value
            self.send(CHANGE);
            self.close()
            
class JournalDialog(Dialog):
    def __init__(self, title="", default="", editable= True, special_button= None):
        self.list = area.List(width=350, height=150)
        self.list.connect(CHANGE, self.itemClicked, None)
        self.journalItems = []
        okButton = button.Button("Okay", style={'width': 80, 'height': 28, 'margin':8})
        okButton.connect(CLICK, self.okayClicked)
        cancelButton = button.Button("Cancel", style={'width': 80, 'height': 28, 'margin':8})
        cancelButton.connect(CLICK, self.close)
        self.input_item = input.Input(default)
        self.input_item.connect(CHANGE, self.itemTyped, None)
        self.input_item.disabled = not editable
        body = table.Table()
        body.tr()
        body.td(basic.Label(title), colspan= 2)
        body.tr()
        body.td(self.list, colspan= 2)
        body.tr()
        if special_button:
            body.td(self.input_item, colspan= 1)
            body.td(special_button, colspan= 1)
        else:
            body.td(self.input_item, colspan= 2)
        body.tr()
        body.td(okButton)
        body.td(cancelButton)
        Dialog.__init__(self, basic.Label(title), body)
    
    def loadJournalItems(self, journalItems, key='title'):
        self.journalItems = journalItems
        self.journalKey = key
        for anItem in journalItems:
            self.list.add(str(anItem.metadata[key]), value=anItem)
        self.itemTyped(None)
            
    def itemClicked(self, arg):
        self.input_item.value = self.list.value.metadata[self.journalKey]
        self.input_item.actualValue = self.list.value
    
    def itemTyped(self, arg):
        for anItem in self.journalItems:
            if anItem.metadata[self.journalKey] == self.input_item.value:
                self.input_item.actualValue = anItem
                self.list.group.value = anItem
                for x in self.list.items:
                    x.focus()
                self.input_item.focus()
                return
        self.input_item.actualValue = self.input_item.value
                
    
    def okayClicked(self):
        if self.input_item:
            self.value = self.input_item
            self.send(CHANGE);
            self.close()

class ConfirmDialog(Dialog):
    def __init__(self, title, message):
        title = basic.Label(title)
        main = table.Table()
        import app
        warningIcon= basic.Image(app.App.app.theme.get('warningdialog.warning', '', 'image'))
        if type(message) is list:
            if len(message) >= 1:
                main.tr();
                main.td(warningIcon, rowspan= len(message), style={'margin': 5});
                main.td(basic.Label(message[0]), align=-1);
            for aMessage in message[1:]:
                main.tr();
                main.td(basic.Label(aMessage), align=-1, colspan=2);
        else:
            main.tr();
            main.td(warningIcon);
            main.td(basic.Label(message), align=-1, colspan=2);
        main.tr();
        self.okayButton= button.Button("Okay");
        self.okayButton.connect(CLICK, self.okayClicked)
        self.cancelButton= button.Button("Cancel");
        self.cancelButton.connect(CLICK, self.close)
        main.td(basic.Spacer(1,1));
        main.td(self.okayButton, align=1, style={'margin': 10});
        main.td(self.cancelButton, align=-1, style={'margin': 10});
        Dialog.__init__(self, title, main)
    
    def okayClicked(self):
        self.value = True
        self.send(CHANGE);
        self.close()
        
class FileDialog(Dialog):
    """A file picker dialog window.
    
    <pre>FileDialog()</pre>
    <p>Some optional parameters:</p>
    <dl>
    <dt>title_txt<dd>title text
    <dt>button_txt<dd>button text
    <dt>path<dd>initial path
    </dl>
    """
    
    def __init__(self, title_txt="File Browser", button_txt="Okay", cls="dialog", path=None, filter=None, default="", favorites=None, special_button=None):
        cls1 = 'filedialog'
        self.filter= filter;
        if not path: self.curdir = os.getcwd()
        else: self.curdir = path
        import app
        self.dir_img = basic.Image(app.App.app.theme.get(cls1+'.folder', '', 'image'))
        td_style = {'padding_left': 4,
                    'padding_right': 4,
                    'padding_top': 2,
                    'padding_bottom': 2}
        self.title = basic.Label(title_txt, cls=cls+".title.label")
        self.body = table.Table()
        self.list = area.List(width=350, height=150)
        self.input_dir = input.Input()
        self.input_file = input.Input(default)
        self._list_dir_()
        self.button_redirect= button.Button("Go");
        self.button_ok = button.Button(button_txt)
        self.body.tr()
        self.body.td(basic.Label("Folder"), style=td_style, align=-1)
        self.body.td(self.input_dir, style=td_style)
        self.body.td(self.button_redirect, style=td_style)
        self.button_redirect.connect(CLICK, self._button_redirect_clicked_, None);
        if favorites or special_button:
            self.body.tr()
            d= document.Document()
            if special_button:
                d.add(special_button)
            for icon, text, link in favorites:
                t= table.Table()
                t.tr()
                t.td(basic.Image(icon))
                t.tr()
                t.td(basic.Label(text))
                b = button.Button(t)
                b.connect(CLICK, self._button_redirect_link_, link)
                d.space((20,28))
                d.add(b)
            self.body.td(d, colspan=3)
        self.body.tr()
        self.body.td(self.list, colspan=3, style=td_style)
        self.list.connect(CHANGE, self._item_select_changed_, None)
        self.button_ok.connect(CLICK, self._button_okay_clicked_, None)
        self.body.tr()
        self.body.td(basic.Label("File"), style=td_style, align=-1)
        self.body.td(self.input_file, style=td_style)
        self.body.td(self.button_ok, style=td_style)
        self.value = None
        Dialog.__init__(self, self.title, self.body)
        
    def _list_dir_(self):
        self.input_dir.value = self.curdir
        self.input_dir.pos = len(self.curdir)
        self.input_dir.vpos = 0
        dirs = []
        files = []
        try:
            for i in os.listdir(self.curdir):
                if os.path.isdir(os.path.join(self.curdir, i)): dirs.append(i)
                else: 
                    if self.filter is not None:
                        path, extension= os.path.splitext(i);
                        if extension in self.filter:
                            files.append(i)
                    else:
                        files.append(i)
        except:
            self.input_file.value = "Opps! no access"
        #if '..' not in dirs: dirs.append('..')
        dirs.sort()
        dirs = ['..'] + dirs
        
        files.sort()
        for i in dirs:
            #item = ListItem(image=self.dir_img, text=i, value=i)
            self.list.add(i,image=self.dir_img,value=i)
        for i in files:
            #item = ListItem(image=None, text=i, value=i)
            self.list.add(i,value=i)
        #self.list.resize()
        self.list.set_vertical_scroll(0)
        #self.list.repaintall()
        
        
    def _item_select_changed_(self, arg):
        self.input_file.value = self.list.value
        fname = os.path.abspath(os.path.join(self.curdir, self.input_file.value))
        if os.path.isdir(fname):
            self.input_file.value = ""
            self.curdir = fname
            self.list.clear()
            self._list_dir_()
    
    def _button_redirect_clicked_(self, arg):
        newDirectory= self.input_dir.value;
        if os.path.isdir(newDirectory):
            self.input_file.value = ""
            self.curdir = newDirectory
            self.list.clear()
            self._list_dir_()

    def _button_redirect_link_(self, destination):
        if os.path.isdir(destination):
            self.input_file.value = ""
            self.curdir = destination
            self.list.clear()
            self._list_dir_()

    def _button_okay_clicked_(self, arg):
        if self.input_dir.value != self.curdir:
            if os.path.isdir(self.input_dir.value):
                self.input_file.value = ""
                self.curdir = os.path.abspath(self.input_dir.value)
                self.list.clear()
                self._list_dir_()
        else:
            self.value = os.path.join(self.curdir, self.input_file.value)
        self.send(CHANGE);
        self.close()
