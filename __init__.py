'''
The Builder Module for Web Builder program.
Classes defined here are ->
    1.BuilderError -> Base class for all exceptions.
    2.FileError -> Error class for errors related to files.
    3.reader -> a file reader, opens the file in 'utf-8'.
    4.page -> Parent object/class representing a html page.
    5.elements -> Base class for all element's objects/classes.
    6.project -> Parent object/class representing a complete project.
    7.cssSelector -> a class to render css selectors
    8.renderFile -> used to render a page, only works if you are on the correct path
'''



import webbrowser as web
import os, pickle,shutil, sys
from zipfile import *
from bs4 import BeautifulSoup
import html.parser
import datetime
class BuilderError(Exception):
        pass
class FileError(BuilderError):
    def __init__(self,message:str):
        '''
        Initialize a FileError object with the given message.
        
        Args:
        message (str): The message to be shown as the error.
        '''
        
        self.message = message
        super().__init__(message)
class AcessError(BuilderError):
    def __init__(self, message:str):
        '''
        Initialize a AcessError object with the given message.
        
        Args:
        message (str): The message to be shown as the error.
        '''
        self.message = message
        super().__init__(message)
def __validate_chdir__(to:str):
        '''
        Validate if the user is in the correct directory.
        
        Args:
        to (str): The path to the directory to chdir to.
        
        Raises:
        AcessError: If the settings could not be accesed, please be in the correct directory.
        '''
        print(to)
        if not to == os.curdir:
            try:
                os.chdir(to)
            except FileNotFoundError:
                raise AcessError('The settings could not be accesed, please be in the correct directory')
        else:
            print('Not Possible. Cur dir->'+os.curdir)
class Tag(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.datal = []
        self.empty_tags = []
        self.idx = 0

    def handle_starttag(self, tag, attrs):
        self.datal.append('<' + tag + '>')
        self.datal.append(attrs)
        self.empty_tags.append(tag)

    def handle_data(self, data):
        self.datal.append(data)

    def handle_endtag(self, tag):
        self.datal.append('</' + tag + '>')
        self.empty_tags.remove(tag)

class Reader:
    def __init__(self,file_name='',code='',returnBuilder=True):
        self.__doc__ = '''
        Reader parses HTML files and code to Builder elements.
        The code is first pre-processed and then processed to come in the following structure::
            ('tag_name',[('attribute_class','attribute_data')],[children],'tag_type')
        Like::
            ('p',
                [('font-family','sans-serif')]
                ,[
                    ('b',[],['Hello'],'Container')
                ],'Container'
            )
        And then converts them to Builder elements!

        Args:
            1.file_name -> path to html file
            2.code -> html code
            3. returnBuilder -> return builder elements if true, otherwise return html as lists of elements in the above structure
        Usage:
            1. if file name provided, do 
                ```
                page = Reader('path_to_file/file.html').parse_file()
                ```
            2. if code provided, do
                ```
                page = Reader(code='HTML_CODE').parse_code()
                ```
        '''
        self.file_name = file_name
        self.html = code
        self.giveBuilder = returnBuilder
        self.elements = elements
    
    def parse_code(self):
        print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] Filtering HTML to Raw data')
        self.datal,self.empty_tags = self.parse_html()
        self.head, self.body = self.split_data(self.clean_data(self.datal))
        print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] Parsing Raw data')
        self.head = self.parse(self.head)
        self.body = self.parse(self.body)
        print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] Converting Parsed data to Builder Elements')
        self.headEle = self.define(self.head)
        self.bodyEle = self.define(self.body)
        if self.giveBuilder:
            return [self.headEle,self.bodyEle]
        else:
            return [self.head,self.body]
    def parse_file(self):
        print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] Reading file')
        self.html = self.read_file()
        return self.parse_code()
    def read_file(self):
        with open(self.file_name, encoding='utf-8') as file:
            return file.read()

    def parse_html(self):
        parser = Tag()
        parser.feed(self.html)
        return parser.datal, parser.empty_tags

    def clean_data(self, data):
        cleaned_data = []
        for x in data:
            if x != '\n':
                cleaned_data.append(x)
        cleaned_data.pop(0)
        cleaned_data.pop(0)
        cleaned_data.pop(-1)
        return cleaned_data

    def split_data(self, data):
        head = data[:7]
        body = data[7:]
        return head, body

    def parse(self, tag_list, re=False):
        d = (tag_list[0].removesuffix('>')).removeprefix('<')  # name
        e = tag_list[1]  # attributes
        if d in self.empty_tags:  # empty tag!
            return d, e, None, 'Empty'
        if len(tag_list) == 4:  # filtring those with only 1 child
            return d, e, tag_list[-2], 'Container'
        f = tag_list[2:-1]  # children
        master = ''  # tag name without < and >
        dumb = 0  # iteration counter for tags to determine start and end of a container tag
        dum = []  # contains a single container tag
        duh = []  # final product
        empty = False
        for x in f:
            if dumb == 0:
                if ('<' in x) and ('>' in x):  # new tag recognition
                    master = (x.removesuffix('>')).removeprefix('<')
                    if master in self.empty_tags:
                        empty = True
                    dum.append(master)  # set name
                else:
                    return d, e, f, 'Container'  # wildcard exit
            else:
                dum.append(x)  # else it is tag data
            if empty and len(dum) == 2:
                empty = False
                dumb = 0
                duh.append(self.parse(dum, re=True))
                dum = []
                continue
            if ('</' in x) and ('>' in x):
                if (x.removesuffix('>')).removeprefix('</') == master:
                    # print(dum)
                    duh.append(self.parse(dum, re=True))  # container tag completed! nest the data
                    dum = []  # empty single tag container
                    dumb = 0  # iterate for a new tag
                    continue  # dont success (+1) dumb
            dumb += 1
            # print([x, dumb, master, dum])
        if not re:
            f = duh  # if provided with a tag in nested function call, provide with the new struc
        return d, e, f, 'Container'  # or else let it go as it is

    def define(self, object):
        if type(object) == str:
            return object
        tag_name = object[0]
        attri_dumb = {}
        children = []
        for x in object[1]:
            attri_dumb[x[0]] = x[1]
        if object[-1] == 'Container':
            if type(object[2]) != str:
                for x in object[2]:
                    children.append(self.define(x))
            else:
                children = object[2]
        match tag_name:
            case 'p':
                dummy = self.elements.p(children, attri_dumb)
            case 'head':
                dummy = self.elements.head(children)
            case 'body':
                dummy = self.elements.body(children)
            case 'title':
                dummy = self.elements.title(children)
            case 'img':
                dummy = self.elements.img(attri_dumb)
            case 'b':
                dummy = self.elements.b(children)
            case 'br':
                dummy = self.elements.br()
            case 'h1','h2','h3','h4','h5','h6':
                dummy = self.elements.hn(int(tag_name[-1]),children,attri_dumb)
            case 'hr':
                dummy = self.elements.hr(attri_dumb)
            case _:
                dummy = self.elements.tag(f'<{tag_name}>',object[-1],children,attri_dumb)
        return dummy
class page():
    def __init__(self,fileName:str='main',head=None,body=None):
        '''
        Initialize a page object with the given arguments.
        
        Args:
        fileName (str): The name of the file. Defaults to 'main'.
        head (elements): The head tag of the page. Defaults to None.
        body (elements): The body tag of the page. Defaults to None.
        '''
        self.fileName = fileName
        self.head = head
        self.body = body
        #self.alphaNum = list('abcdefghijklmnopqrstuvwxyz')
    def render(self):
        '''
        Renders this page. Returns a string as a html page.

        This method generates a complete HTML document as a string by rendering
        the head and body components of the page. It begins with the doctype 
        declaration and opening <html> tag, followed by the rendered content of 
        the head and body, and concludes with the closing </html> tag.

        Returns:
            str: The complete HTML document as a string.
        '''
        doc = '<!doctype html>\n<html>\n'
        doc += self.head.render()
        doc += self.body.render()
        doc += '</html>'
        doc = BeautifulSoup(doc,'html.parser').prettify()
        return doc
    def renderSecured(self,headObj,bodyObj,secClass):
        pass
    def export(self):
        file = open(self.fileName+'.html','w',encoding='utf-8')
        file.write(self.render())
        file.close()
        return '200'
    def exportRaw(self):
        '''
        Export the page as a raw folder. This folder will be given the same name as the page.
        The folder will contain two files, 'Head.RBCode' and 'Body.RBCode', which contain the
        head and body of the page, respectively, in a serialized form.
        
        Raises:
        FileExistsError: If a folder with the same name as the page already exists.
        FileError: If the folder could not be created.
        '''
        
        try:
            os.mkdir(self.fileName)
            __validate_chdir__(self.fileName)
        except FileExistsError:
            raise FileError(f'A folder with the project name "{self.fileName}" already exists, try renaming the original folder or rename this project by changing it\'s "fileName" attribute.')
        except FileNotFoundError:
            raise FileError(f'We could not acess the project\'s root folder and cannot find a reason why. Please share your problem with the devs')
        HeadFile = open('Head.RBCode','wb')
        BodyFile = open('Body.RBCode','wb')
        pickle.dump(self.head, HeadFile)
        pickle.dump(self.body, BodyFile)
        HeadFile.close()
        BodyFile.close()
        __validate_chdir__('..')
    def importRaw(self, ProjectName: str):
        try:
            __validate_chdir__(ProjectName)
        except FileNotFoundError:
            raise FileError('The project\'s root folder could not be accessed. Please make sure you the path is of the preceeding folder of your project. If still unsure, please contact the devs.')
        try:
            HeadFile = open('Head.RBCode','rb')
            BodyFile = open('Body.RBCode','rb')
        except FileNotFoundError:
            raise FileError('The head or body (or both) raw files does not exist.\nPlease check these-> Are you in the right folder? Had you renamed the files? Did you delete any file?\n If no, please contact the dev for better solution.')
        head = pickle.load(HeadFile)
        body = pickle.load(BodyFile)
        HeadFile.close()
        BodyFile.close()
        self.head = head
        self.body = body
        return [head, body]
class elements():
    class title():
        def __init__(self,innerHTML):
            """
            A <title> html tag representing object with the following funcs
            1. render
            
            Args:
            1. count -> Does not hold any significant importance; can be set to 0
            2. innerHTML -> The content that goes inside <title></title> tags.
            """
            self.tag = '<title>'
            self.innerhtml = innerHTML
            self.token = 'Verified'
        def render(self) -> str:
            """
            Renders this widget. Returns a string as a html tag.
            """
            self.line = ''
            self.line += self.tag
            if type(self.innerhtml)==type('str'):
                self.line += self.innerhtml
            else:
                if type(self.innerhtml) != type(['h','l']):
                    self.line += self.innerhtml.render()
                else:
                    for x in self.innerhtml:
                        if type(x)==str:
                            self.line += x
                        else:
                            self.line += x.render()
            self.line += self.tag.replace('<','</')
            self.line += '\n'
            return self.line
    class head():
        def __init__(self,innerHTML=[]):
            """
            The root object holder for all objects related to <head> tag(s) with the following funcs
            1. render -> render this object
            2. addElement -> add a children element

            Args:
            1. innerHTML -> all the children elements

            This object can have many other children objects/elements and can be added using it's addElement function. When rendered, all children objects/elements will also be rendered.
            Also, you can remove, access, add any children element by accessing it's innerhtml variable
            NOTE: innerhtml is different from innerHTML. innerHTML will be found in args, while it will be stored as innerhtml in the object.
            """
            self.tag = '<head>'
            self.innerhtml = innerHTML
            self.token = 'Verified'
        def render(self):
            """Render this object, including any children elements"""
            self.line = ''
            self.line += self.tag
            if type(self.innerhtml)==type('str'):
                self.line += self.innerhtml
            else:
                if type(self.innerhtml) != type(['h','l']):
                    self.line += self.innerhtml.render()
                else:
                    for x in self.innerhtml:
                        if type(x)==str:
                            self.line += x
                        else:
                            self.line += x.render()
            self.line += self.tag.replace('<','</')
            self.line += '\n'
            return self.line
        def addElement(self,element):
            """Add a children element"""
            self.innerhtml.append(element)
    class body():
        def __init__(self,innerHTML=[]):
            """The root object holder for all objects related to <body> tag(s) with the following funcs
            1. render -> render this object
            2. addElement -> add a children element

            Args:
            1. innerHTML -> all the children elements

            This object can have many other children objects/elements and can be added using it's addElement function. When rendered, all children objects/elements will also be rendered.
            Also, you can remove, access, add any children element by accessing it's innerhtml variable
            NOTE: innerhtml is different from innerHTML. innerHTML will be found in args, while it will be stored as innerhtml in the object."""
            self.tag = '<body>'
            self.innerhtml = innerHTML
            self.token = 'Verified'
        def render(self):
            """Render this object, including any children elements"""
            self.line = ''
            self.line += self.tag
            if type(self.innerhtml)==type('str'):
                self.line += self.innerhtml
            else:
                if type(self.innerhtml) != type(['h','l']):
                    self.line += self.innerhtml.render()
                else:
                    for x in self.innerhtml:
                        if type(x)==str:
                            self.line += x
                        else:
                            self.line += x.render()
            self.line += self.tag.replace('<','</')
            self.line += '\n'
            return self.line
        def addElement(self,element):
            """Add a child element"""
            self.innerhtml.append(element)
    class li():
        def __init__(self,innerHTML,attributes={}):
            """A <li> tag object with the following funcs
            1. render -> render this object as a <li>
            2. renderAttributes -> renders attributes, used by render
            
            You can add more elements by appending to it's innerhtml attribute

            Args:
            1. count -> currently useless, maybe used later
            2. innerHTML -> content between <li> and </li>
            3. attributes -> a dict that stores all the atrributes for this tag. Ex: {'font-family':'Times New Roaman'}
            NOTE: innerhtml is different from innerHTML. innerHTML will be found in args, while it will be stored as innerhtml in the object.
            """
            self.tag = '<li>'
            self.innerhtml = innerHTML
            self.attributes = attributes
            self.token = 'Verified'
        def render(self):
            self.line = ''
            if self.attributes=={}:
                self.line += self.tag
            else:
                self.line += self.renderAttributes()
            if type(self.innerhtml)==type('str'):
                self.line += self.innerhtml
            else:
                if type(self.innerhtml) != type(['h','l']):
                    self.line += self.innerhtml.render()
                else:
                    for x in self.innerhtml:
                        if type(x)==str:
                            self.line += x
                        else:
                            self.line += x.render()
            self.line += self.tag.replace('<','</')
            self.line += '\n'
            return self.line
        def renderAttributes(self):
            """Used by the render() function"""
            self.line = self.tag.replace('>',' ')
            for y in self.attributes:
                self.line += y+'="'
                if not type(self.attributes[y])==type('str'):
                    for z in self.attributes[y]:
                        if y != 'style':
                            self.line+= z+' '
                        else:
                            self.line += z+';'
                    self.line.removesuffix(' ')
                    self.line += '" '
                elif type(self.attributes[y])==type('str'):
                    self.line += self.attributes[y]+'" '
            self.line += '>'
            return self.line
    class ul():
        def __init__(self,innerHTML,attributes={}):
            """A <ul> tag object with the following funcs
            1. render -> render this object as a <ul>
            2. renderAttributes -> renders attributes, used by render
            3. addElement -> add any more child element

            Args:
            1. count -> currently useless, maybe used later
            2. innerHTML -> content between <ul> and </ul>
            3. attributes -> a dict that stores all the atrributes for this tag. Ex: {'font-family':'Times New Roaman'}
            NOTE: innerhtml is different from innerHTML. innerHTML will be found in args, while it will be stored as innerhtml in the object.
            """
            self.tag = '<ul>'
            self.innerhtml = innerHTML
            self.attributes = attributes
            self.token = 'Verified'
        def addElement(self, child):
            self.innerhtml.append(child)
        def render(self):
            self.line = ''
            if self.attributes=={}:
                self.line += self.tag
            else:
                self.line += self.renderAttributes()
            if type(self.innerhtml)==type('str'):
                self.line += self.innerhtml
            else:
                if type(self.innerhtml) != type(['h','l']):
                    self.line += self.innerhtml.render()
                else:
                    for x in self.innerhtml:
                        if type(x)==str:
                            self.line += x
                        else:
                            self.line += x.render()
            self.line += self.tag.replace('<','</')
            self.line += '\n'
            return self.line
        def renderAttributes(self):
            self.line = self.tag.replace('>',' ')
            for y in self.attributes:
                self.line += y+'="'
                if not type(self.attributes[y])==type('str'):
                    for z in self.attributes[y]:
                        if y != 'style':
                            self.line+= z+' '
                        else:
                            self.line += z+';'
                    self.line.removesuffix(' ')
                    self.line += '" '
                elif type(self.attributes[y])==type('str'):
                    self.line += self.attributes[y]+'" '
            self.line += '>'
            return self.line
    class ol():
        def __init__(self,innerHTML:str|list,attributes:dict={}):
            """A <ol> tag object with the following funcs
            1. render -> render this object as a <ol>
            2. renderAttributes -> renders attributes, used by render
            3. addElement -> add any more child element

            Args:
            1. count -> currently useless, maybe used later
            2. innerHTML -> content between <ol> and </ol>
            3. attributes -> a dict that stores all the atrributes for this tag. Ex: {'font-family':'Times New Roaman'}
            NOTE: innerhtml is different from innerHTML. innerHTML will be found in args, while it will be stored as innerhtml in the object.
            """
            self.tag = '<ol>'
            self.innerhtml = innerHTML
            self.attributes = attributes
            self.token = 'Verified'
        def addElement(self, child):
            self.innerhtml.append(child)
        def render(self):
            self.line = ''
            if self.attributes=={}:
                self.line += self.tag
            else:
                self.line += self.renderAttributes()
            if type(self.innerhtml)==type('str'):
                self.line += self.innerhtml
            else:
                if type(self.innerhtml) != type(['h','l']):
                    self.line += self.innerhtml.render()
                else:
                    for x in self.innerhtml:
                        if type(x)==str:
                            self.line += x
                        else:
                            self.line += x.render()
            self.line += self.tag.replace('<','</')
            self.line += '\n'
            return self.line
        def renderAttributes(self):
            self.line = self.tag.replace('>',' ')
            for y in self.attributes:
                self.line += y+'="'
                if not type(self.attributes[y])==type('str'):
                    for z in self.attributes[y]:
                        if y != 'style':
                            self.line+= z+' '
                        else:
                            self.line += z+';'
                    self.line.removesuffix(' ')
                    self.line += '" '
                elif type(self.attributes[y])==type('str'):
                    self.line += self.attributes[y]+'" '
            self.line += '>'
            return self.line
    class p():
        def __init__(self,innerHTML:str|list,attributes:dict={}):
            """A <p> tag object with the following funcs
            1. render -> render this object as a <p>
            2. renderAttributes -> renders attributes, used by render
            You can add any child element by appending to it's innerhtml

            Args:
            1. count -> currently useless, maybe used later
            2. innerHTML -> content between <p> and </p>
            3. attributes -> a dict that stores all the atrributes for this tag. Ex: {'font-family':'Times New Roaman'}
            NOTE: innerhtml is different from innerHTML. innerHTML will be found in args, while it will be stored as innerhtml in the object.
            """
            self.tag = '<p>'
            self.innerhtml = innerHTML
            self.attributes = attributes
            self.token = 'Verified'
        def render(self):
            self.line = ''
            if self.attributes=={}:
                self.line += self.tag
            else:
                self.line += self.renderAttributes()
            if type(self.innerhtml)==type('str'):
                self.line += self.innerhtml
            else:
                if type(self.innerhtml) != type(['h','l']):
                    self.line += self.innerhtml.render()
                else:
                    for x in self.innerhtml:
                        if type(x)==str:
                            self.line += x
                        else:
                            self.line += x.render()
            self.line += self.tag.replace('<','</')
            self.line += '\n'
            return self.line
        def renderAttributes(self):
            self.line = self.tag.replace('>',' ')
            for y in self.attributes:
                self.line += y+'="'
                if not type(self.attributes[y])==type('str'):
                    for z in self.attributes[y]:
                        if y != 'style':
                            self.line+= z+' '
                        else:
                            self.line += z+';'
                    self.line.removesuffix(' ')
                    self.line += '" '
                elif type(self.attributes[y])==type('str'):
                    self.line += self.attributes[y]+'" '
            self.line += '>'
            return self.line
    class tag():
        def __init__(self,tag: str='<br>',tagType: str='Empty',innerHTML:str|list=[],attributes:dict={}):
            """A special tag object that deals with those tags not listed here; with the following funcs
            1. render -> render this object as a html tag
            2. renderAttributes -> renders attributes, used by render
            You can add any child element by appending to it's innerhtml (please check if the tag supports it)

            Args:
            1. tag -> the starting tag. Ex: '<p>' . NOTE: Please do not include anything else than that
            2. tagType -> if the tag being specified is an empty tag (that does not requires to be closed), then provide 'Empty', else provide 'Container'
            3. innerHTML -> content inside (if empty, then can be provided  a blank list)
            4. count -> currently useless, maybe used later
            3. attributes -> a dict that stores all the atrributes for this tag. Ex: {'font-family':'Times New Roaman'}
            NOTE: innerhtml is different from innerHTML. innerHTML will be found in args, while it will be stored as innerhtml in the object.
            """
            self.tag = tag
            self.type = tagType
            self.innerhtml = innerHTML
            self.token = 'Unverified'
            self.attributes = attributes
        def render(self):
            self.line = ''
            if self.attributes=={}:
                self.line += self.tag
            else:
                self.line += self.renderAttributes()
            if self.type=='Container':
                if type(self.innerhtml)==type('str'):
                    self.line += self.innerhtml
                else:
                    if type(self.innerhtml) != type(['h','l']):
                        self.line += self.innerhtml.render()
                    else:
                        for x in self.innerhtml:
                            if type(x)==str:
                                self.line += x
                            else:
                                self.line += x.render()
                self.line += self.tag.replace('<','</')
            self.line += '\n'
            return self.line
        def renderAttributes(self):
            self.line = self.tag.replace('>',' ')
            for y in self.attributes:
                self.line += y+'="'
                if not type(self.attributes[y])==type('str'):
                    for z in self.attributes[y]:
                        if y != 'style':
                            self.line+= z+' '
                        else:
                            self.line += z+';'
                    self.line.removesuffix(' ')
                    self.line += '" '
                elif type(self.attributes[y])==type('str'):
                    self.line += self.attributes[y]+'" '
            self.line += '>'
            return self.line
    class hn():
        def __init__(self,level:int,innerHTML:str|list='',attributes:dict={}):
            """A heading tag (like <h1>) with the following funcs
            1. render -> render this object as a <hn>
            2. renderAttributes -> renders attributes, used by render
            You can add any child element by appending to it's innerhtml (please check if the tag supports it)

            Args:
            1. level -> (expects an integer value, from 1 to 6, including both endpoints) depicts the heading level
            2. innerHTML -> content inside
            3. count -> currently useless, maybe used later
            4. attributes -> a dict that stores all the atrributes for this tag. Ex: {'font-family':'Times New Roaman'}
            NOTE: innerhtml is different from innerHTML. innerHTML will be found in args, while it will be stored as innerhtml in the object.
            """
            self.tag = f'<h{level}>'
            self.innerhtml = innerHTML
            self.attributes = attributes
            self.token = 'Verified'
        def render(self):
            self.line = ''
            if self.attributes=={}:
                self.line += self.tag
            else:
                self.line += self.renderAttributes()
            if type(self.innerhtml)==type('str'):
                self.line += self.innerhtml
            else:
                if type(self.innerhtml) != type(['h','l']):
                    self.line += self.innerhtml.render()
                else:
                    for x in self.innerhtml:
                        if type(x)==str:
                            self.line += x
                        else:
                            self.line += x.render()
            self.line += self.tag.replace('<','</')
            self.line += '\n'
            return self.line
        def renderAttributes(self):
            self.line = self.tag.replace('>',' ')
            for y in self.attributes:
                self.line += y+'="'
                if not type(self.attributes[y])==type('str'):
                    for z in self.attributes[y]:
                        if y != 'style':
                            self.line+= z+' '
                        else:
                            self.line += z+';'
                    self.line.removesuffix(' ')
                    self.line += '" '
                elif type(self.attributes[y])==type('str'):
                    self.line += self.attributes[y]+'" '
            self.line += '>'
            return self.line
    class div():
        def __init__(self,innerHTML:str|list=[],attributes:dict={}):
            """A <div> tag object with the following funcs
            1. render -> render this object as a <div>
            2. renderAttributes -> renders attributes, used by render
            3. addElement -> adds a child element
            You can add any child element by appending to it's innerhtml (please check if the tag supports it)

            Args:
            1. innerHTML -> content inside 
            2. count -> currently useless, maybe used later
            3. attributes -> a dict that stores all the atrributes for this tag. Ex: {'font-family':'Times New Roaman'}
            NOTE: innerhtml is different from innerHTML. innerHTML will be found in args, while it will be stored as innerhtml in the object.
            """
            self.tag = '<div>'
            self.innerhtml = innerHTML
            self.token = 'Verified'
            self.attributes = attributes
        def render(self):
            self.line = ''
            if self.attributes=={}:
                self.line += self.tag
            else:
                self.line += self.renderAttributes()
            if type(self.innerhtml)==type('str'):
                self.line += self.innerhtml
            else:
                if type(self.innerhtml) != type(['h','l']):
                    self.line += self.innerhtml.render()
                else:
                    for x in self.innerhtml:
                        if type(x)==str:
                            self.line += x
                        else:
                            self.line += x.render()
            self.line += self.tag.replace('<','</')
            self.line += '\n'
            return self.line
        def addElement(self,element):
            self.innerhtml.append(element)
        def renderAttributes(self):
            self.line = self.tag.replace('>',' ')
            for y in self.attributes:
                self.line += y+'="'
                if not type(self.attributes[y])==type('str'):
                    for z in self.attributes[y]:
                        if y != 'style':
                            self.line+= z+' '
                        else:
                            self.line += z+';'
                    self.line.removesuffix(' ')
                    self.line += '" '
                elif type(self.attributes[y])==type('str'):
                    self.line += self.attributes[y]+'" '
            self.line += '>'
            return self.line
    class img():
        def __init__(self,attributes:dict={}):
            
            """An <img> tag object with the following funcs
            1. render -> render this object as a <img>
            2. renderAttributes -> renders attributes, used by render
            You can add any child element by appending to it's innerhtml (please check if the tag supports it)

            Args:
            1. attributes -> a dict that stores all the atrributes for this tag. Ex: {'font-family':'Times New Roaman'}
            NOTE: innerhtml is different from innerHTML. innerHTML will be found in args, while it will be stored as innerhtml in the object.
            
            2. renderAttributes -> renders attributes, used by render

            Args:
            1. src -> the source of the image
            2. alt -> the alternative text to display if the image can't be loaded
            3. count -> currently useless, maybe used later
            4. attributes -> a dict that stores all the atrributes for this tag. Ex: {'font-family':'Times New Roaman'}
            NOTE: innerhtml is different from innerHTML. innerHTML will be found in args, while it will be stored as innerhtml in the object.
            """
            self.tag = '<img>'
            self.attributes = attributes
            self.token = 'Verified'
        def render(self):
            self.line = ''
            if self.attributes=={}:
                self.line += self.tag
            else:
                self.line += self.renderAttributes()
            self.line += self.tag.replace('<','</')
            self.line += '\n'
            return self.line
        def renderAttributes(self):
            self.line = self.tag.replace('>',' ')
            for y in self.attributes:
                self.line += y+'="'
                if not type(self.attributes[y])==type('str'):
                    for z in self.attributes[y]:
                        if y != 'style':
                            self.line+= z+' '
                        else:
                            self.line += z+';'
                    self.line.removesuffix(' ')
                    self.line += '" '
                elif type(self.attributes[y])==type('str'):
                    self.line += self.attributes[y]+'" '
            self.line += '>'
            return self.line
    class hr():
        def __init__(self,attributes: dict={}):
            """A <hr> tag object with the following funcs
            1. render -> render this object as a <hr>
            2. renderAttributes -> renders attributes, used by render
            Args:
            1. count -> currently useless, maybe used later
            2. attributes -> a dict that stores all the atrributes for this tag. Ex: {'font-family':'Times New Roaman'}
            """
            self.tag = '<hr>'
            self.attributes = attributes
            self.token = 'Verified'
        def render(self):
            self.line = ''
            if self.attributes=={}:
                self.line += self.tag
            else:
                self.line += self.renderAttributes()
            self.line += self.tag.replace('<','</')
            self.line += '\n'
            return self.line
        def renderAttributes(self):
            self.line = self.tag.replace('>',' ')
            for y in self.attributes:
                self.line += y+'="'
                if not type(self.attributes[y])==type('str'):
                    for z in self.attributes[y]:
                        if y != 'style':
                            self.line+= z+' '
                        else:
                            self.line += z+';'
                    self.line.removesuffix(' ')
                    self.line += '" '
                elif type(self.attributes[y])==type('str'):
                    self.line += self.attributes[y]+'" '
            self.line += '>'
            return self.line
    class br():
        def __init__(self):
            """A <br> tag object with the following funcs
            1. render -> render this object as a <br>
                            
            Args:
            1. count -> currently useless, maybe used later
            """
            self.tag = '<br>'
            self.token = 'Verified'
        def render(self):
            self.line = self.tag
            self.line += '\n'
            return self.line
    class comment():
        def __init__(self,comment:str):
            """A <!-- --> tag object with the following funcs
            1. render -> render this object as a <!-- -->
                            
            Args:
            1. comment -> the message you want to add
            """
            self.tag = '<!--'
            self.comment = comment
            self.token = 'Verified'
        def render(self):
            return self.tag+self.comment+'-->'
    class b():
        def __init__(self,innerHTML: str | list,attributes:dict={}):
            """A <b> tag object with the following funcs
            1. render -> render this object as a <li>
            2. renderAttributes -> render this object's attributes, used by render          
            Args:
            1. count -> currently useless, maybe used later
            2. innerHTML -> the content inside
            3. attributes -> a dict that stores all the atrributes for this tag. Ex: {'font-family':'Times New Roaman'}
            NOTE: innerhtml is different from innerHTML. innerHTML will be found in args, while it will be stored as innerhtml in the object.
            """
            self.tag = '<b>'
            self.innerhtml = innerHTML
            self.attributes = attributes
            self.token = 'Verified'
        def render(self):
            self.line = ''
            if self.attributes=={}:
                self.line += self.tag
            else:
                self.line += self.renderAttributes()
            if type(self.innerhtml)==type('str'):
                self.line += self.innerhtml
            else:
                if type(self.innerhtml) != type(['h','l']):
                    self.line += self.innerhtml.render()
                else:
                    for x in self.innerhtml:
                        if type(x)==str:
                            self.line += x
                        else:
                            self.line += x.render()
            self.line += self.tag.replace('<','</')
            self.line += '\n'
            return self.line
        def renderAttributes(self):
            self.line = self.tag.replace('>',' ')
            for y in self.attributes:
                self.line += y+'="'
                if not type(self.attributes[y])==type('str'):
                    for z in self.attributes[y]:
                        if y != 'style':
                            self.line+= z+' '
                        else:
                            self.line += z+';'
                    self.line.removesuffix(' ')
                    self.line += '" '
                elif type(self.attributes[y])==type('str'):
                    self.line += self.attributes[y]+'" '
            self.line += '>'
            return self.line
class project():
    def __init__(self, projectName:str, Images: bool = True, Javascript:bool=True,CSS:bool=True,XML:bool=True):
        """A parent object for your website. When created creates a folder (and sub-folders) in the path specified in this order
        projectname\n
            |----Resources--|\n
            |---------------|Javascript\n
            |---------------|CSS\n
            |---------------|XML\n
            |---------------|Other\n
            |----settings.py\n
        All HTML files will be saved in the root folder (in the above case, in projectname). All files will be saved in thier respective folder.

        You can also customize what folders are created. The "other" folder is created by default.
        Theses folders are created for ease of acess to static files, and can their path can be found using this object's getRespath() object.

        This object also has a "pages" variable (not included in the attributes), which is used to store the pages.

        You will also notice three py files "pagesData.py" , "resourcesData.py" and "about.py" in their respective folders.
        these contain data about the what pages are there and what resources are registered. When the project is being packed, all data registered here is packed in the package,
        and when a version is declared, all data about the version is stored in "about.py"

        With project, you can ship your website anytime you want and declare a version as per your want! This is the reason wyhy there are two more folders- "version" and "packages"
        Args:
        1. projectName -> the name of the project (used to store at the root path, used when packing and versioning)
        2. Images -> Make a Images folder?
        3. Javascript -> Make a Javascript folder?
        4. CSS -> Make a CSS folder?
        5. XML -> Make a XML folder?

        As soon as you make this object, you will be asked for the root directory. Just select the desired directory, and you're good to go!
        """
        self.__name__ = projectName
        self.__supported_resources__ = ('xml','js','png','jpg','css','jpeg','gif','svg','bmp','img','other')
        try:
            os.mkdir(projectName)
        except FileExistsError:
            raise FileError('The folder already exists! Please try some other name.')
        __validate_chdir__(projectName)
        os.mkdir('Resources')
        __validate_chdir__('Resources')
        if Images:
            os.mkdir('Images')
        if Javascript:
            os.mkdir('Javascript')
        if XML:
            os.mkdir('XML')
        if CSS:
            os.mkdir('CSS')
        os.mkdir('Other')
        __validate_chdir__('..')
        os.mkdir('Versions')
        self.pages = {}
        os.chdir('.\\.')
        with open('settings.py','w',encoding='utf-8') as setting:
            setting.write('VERSIONS = ["0.0.1"]\n')
            setting.write("REGISTERED_RESOURCES = {'IMAGES':"+str(Images)+",'JAVASCRIPT':"+str(Javascript)+",'XML':"+str(XML)+",'CSS':"+str(CSS)+"}\n")
            setting.write("RESOURCES = {} # {'gg.png':PATH}\n")
            setting.write('PAGES = []')
    def __changeSetting__(self,grp:str,main,add:bool=True,/,key=None):
        with open('settings.py','a',encoding='utf-8') as setting:
            match grp:
                case 'pages':
                    if add:
                        setting.write(f'\nPAGES.append({main})')
                    else:
                        setting.write(f'\nPAGES.remove({main})')
                case 'resource':
                    if add:
                        setting.write(f'\nRESOURCES[{key}] = {main}')
                    else:
                        setting.write(f'\nRESOURCES.pop({main},__default="")')
                case 'version':
                    if add:
                        setting.write(f'\nVERSIONS.append({main})')
                    else:
                        setting.write(f'\nVERSIONS.remove({main})')
    def addPage(self,page :page):
        self.pages[page.fileName+'.html'] = [page, page.head,page.body]
    def package(self):
        __validate_chdir__(self.__name__)
        sys.path.insert(0,os.getcwd())
        try:
            import settings
        except ModuleNotFoundError:
            raise AcessError('The settings could not be accesed, please be in the correct directory')
        version = settings.VERSIONS[-1]
        zipped = ZipFile(f'{self.__name__}_{version}','w')
        for x in settings.PAGES:
            zipped.write(x,x)
        os.chdir("Resources")
        zipped.mkdir("Resources")
        for x in os.listdir():
            if settings.REGISTERED_RESOURCES[x.title()]:
                __validate_chdir__(x)
                for y in os.listdir():
                    if y in settings.RESOURCES:
                        zipped.write(y,f"Resources\\{x}\\{y}")
        zipped.close()
    def addResource(self,name:str,extension:str,fileByte:bytes):
        __validate_chdir__(self.__name__)
        __validate_chdir__('Resources')
        match extension:
            case 'css':
                os.chdir('CSS')
                file = open(name+'.css','wb')
                file.write(fileByte)
                file.close()
                os.chdir('..\\..')
                self.__changeSetting__('resource','Resources\\CSS',True,key=name+'.css')
            case 'js':
                os.chdir('Javascript')
                file = open(name+'.js','wb')
                file.write(fileByte)
                file.close()
                os.chdir('..\\..')
                self.__changeSetting__('resource','Resources\\Javascript',True,key=name+'.js')
            case 'xml':
                os.chdir('XML')
                file = open(name+'.xml','wb')
                file.write(fileByte)
                file.close()
                os.chdir('..\\..')
                self.__changeSetting__('resource','Resources\\XML',True,key=name+'.xml')
            case 'png' | 'jpg' | 'svg' | 'bmp' | 'gif' | 'jpeg' | 'img':
                os.chdir('Images')
                file = open(name+f'.{extension}','wb')
                file.write(fileByte)
                file.close()
                os.chdir('..\\..')
                self.__changeSetting__('resource','Resources\\Images',True,key=name+f'.{extension}')
            case 'other':
                os.chdir('Other')
                file = open(name+f'.{extension}','wb')
                file.write(fileByte)
                file.close()
                os.chdir('..\\..')
                self.__changeSetting__('resource','Resources\\Other',True,key=name+f'.{extension}')
    def save(self):
        __validate_chdir__(self.__name__)
        sys.path.insert(0,os.getcwd())
        try:
            import settings
        except ModuleNotFoundError:
            raise AcessError('The settings could not be accesed, please be in the correct directory')
        for x in self.pages:
            if x in settings.PAGES:
                continue
            else:
                self.__changeSetting__('pages',self.pages[x][0].fileName+'.html',True)
            self.pages[x][0].export(self.pages[x][0].render(self.pages[x][1],self.pages[x][2]))
            self.pages[x][0].exportRaw(self.pages[x][1],self.pages[x][2])
    def getPage(self, pageName: str):
        __validate_chdir__(self.__name__)
        p = page(pageName)
        head, body = p.importRaw(pageName)
        return [p, head, body]
    def deletePage(self, pageName:str):
        __validate_chdir__(self.__name__)
        os.remove(pageName+'str')
        shutil.rmtree(pageName)
    def get_resource_address(self,resourceName:str):
        sys.path.insert(0,os.getcwd())
        try:
            import settings
        except ModuleNotFoundError:
            raise AcessError('The settings could not be accesed, please be in the correct directory')
        return settings.RESOURCES[resourceName]
class cssSelector():
    def __init__(self,selector,propertyDict):
        self.selector = selector
        self.property = propertyDict
    def render(self):
        self.line = ''
        self.line += self.selector+'{\n'
        for x in self.property:
            self.line += x+':'+self.property[x]+';\n'
        self.line += '}\n'
        return self.line
def renderFile(self, fileName):
    """A func that can be used to open any file, with the filename provided. Make sure you are in the correct path"""
    try:
        web.open(fileName)
    except FileNotFoundError:
        raise FileError('The file could not be found! Are you in the correct folder? If not, use os.chdir')
