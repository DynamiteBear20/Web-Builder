from html.parser import HTMLParser
datal = []
idx = 0
def makeDict(tag,attr,inner):
    datal[idx] = [tag,attr,inner]
class Tag(HTMLParser):
    def handle_starttag(self,tag,attrs):
        datal.append('<'+tag+'>')
        datal.append(attrs)
    def handle_data(self,data):
        datal.append(data)
    def handle_endtag(self,tag):
        datal.append('</'+tag+'>')
file = open('test.html', encoding='utf-8')
html = file.read()
parser = Tag()
parser.feed(html)
for x in datal:
    if x=='\n':
        datal.remove('\n')
datal.pop(0)
datal.pop(0)
datal.pop(-1)
#print(datal)
head = datal[:7]
body = datal[7:]
print(head,body)
def foo(tagList:list[str],re=False):
    d = (tagList[0].removesuffix('>')).removeprefix('<')
    e = tagList[1]
    if len(tagList)==4:
        return d,e,tagList[-2]
    f = tagList[2:-1]
    master = ''
    dumb = 0
    dum = [] # hah
    duh = []
    for x in f:
        if dumb==0:
            if ('<' in x) and ('>' in x):
                master = (x.removesuffix('>')).removeprefix('<')
                dum.append(master)
            else:
                return d,e,f
        else:
            dum.append(x)
        if ('</' in x) and ('>' in x):
            if (x.removesuffix('>')).removeprefix('</') == master:
                print(dum)
                duh.append(foo(dum,re=True))
                dum = []
                dumb = 0
                continue
        dumb += 1
        #print([x,dumb,master,dum])
    if not re:
        f = duh
    return (d,e,f)
html5 = [foo(head),foo(body)]
print(html5)
'''
from bs4 import BeautifulSoup, Tag
import json, os


def tag2dict(tag):
    if isinstance(tag, Tag):
        attrs = tag.attrs
        attrs['tag'] = tag.name
        #attrs['inner_html'] = str(tag)
        attrs['children'] = [tag2dict(child) for child in tag.children if child != '\n']
        return attrs
    else:
        return str(tag)
def findElement(main):
    if main['tag'] == '[document]':
        head = main['children'][1]['children'][0]
        body = main['children'][1]['children'][1]
        return [head,body]
def decode(element):
    elements = []
    #print(element)
    for x in element['children']:
        if type(x) != type('str'):
            dumb = []
            dumb.append(x['tag'])
            dumb2 = []
            for y in element.keys():
                if y != 'tag' and y != 'children':
                    dumb2.append(element[y])
            childrens = []
            for y in decode(x):
                childrens.append(y)
            dumb.append(dumb2)
            dumb.append(childrens)
            elements.append(dumb)
        if type(x) == type('str'):
            elements.append(x)
    return elements
with open('test.html','r', encoding='utf-8') as file:
    string = file.read()
    soup = BeautifulSoup(string, 'html.parser')
    dict_data = tag2dict(soup)
    head, body = findElement(dict_data)
    #print(json.dumps(head, indent=4))
    #print('\n')
    #print(json.dumps(body, indent=4))
    #print(body)
    print(decode(body))'''