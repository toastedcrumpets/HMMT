#!/usr/bin/python3

import re
from bs4 import BeautifulSoup
from TexSoup import TexSoup, TexNode

class Tex2Reveal(object):
    def __init__(self, code):
        self.info = {}
        self._handle_document(None) #All variable initialisation is done on \begin{document}
        
        #Remove comments
        code = re.sub('(?<!\\\\)%.*$', '', code, flags=re.M)
        #Remove inline display math shortcuts
        code = code.replace(r'\[', r'\begin{equation*}')
        code = code.replace(r'\]', r'\end{equation*}')
        #Collapse whitespace
        code = re.sub(r'\n\s*\n', '\n\n', code, flags=re.M)
        self.soup = TexSoup(code)
        
        #Parse any standalone commands
        nodes = ('title', 'author', 'institute', 'date', 'logo')
        for node in nodes:
            for elem in self.soup.find_all(node):
                data = list(elem.contents)
                if len(data) != 0:
                    self.info[node] = data
                
        #Walk the document creating the tree
        self._walk(self.soup.find('document'))

    def _walk(self, node):
        if isinstance(node, TexNode):
            if self._in_equation:
                self._handle_str(node)
            else:
                name = node.name

                #Check for <1-> decorators and remove them
                fragment = False
                fragment_search = re.search('<[0-9]+-?[0-9]*>', name)
                if fragment_search != None:
                    name = name[:fragment_search.start()]
                    fragment = True

                #Check if the function name is starred
                starred = False                
                if name[-1] == '*':
                    name = name[:-1]
                    starred=True
                
                method_name = '_handle_%s' % name
                method = getattr(self, method_name, None)
                skip_children = False
                if method:
                    skip_children = method(node, starred=starred, fragment=fragment)
                else:
                    self._handle_unknown(node, starred=starred, fragment=fragment)
                if not skip_children:
                    for element in node.contents:
                        self._walk(element)
        elif isinstance(node, str):
            if self.current_slide is not None:
                self._handle_str(node)

    def _handle_document(self, node, starred=False, fragment=False):
        self.current_tag = None
        self.current_slide = None
        self.soup = BeautifulSoup('<div class="slides"></div>', "lxml")
        self.slides = self.soup.div
        self.current_section = None
        self._in_equation = False
        self.subsection_title = None

    def _handle_frame(self, node, starred=False, fragment=False):
        if self.current_section == None:
            self.current_section = self.soup.new_tag("section")
            self.slides.append(self.current_section)
        
        self.current_tag = self.current_slide = self.soup.new_tag("section")
        if self.subsection_title != None:
            self.current_slide['data-menu-title'] = self.subsection_title
            self.subsection_title = None
        self.current_section.append(self.current_slide)
        return False
                
    # _handle methods return True if the children are to be skipped.
    
    def _handle_str(self, node):
        data = str(node)
        if '$' in data:
            self._in_equation = not self._in_equation
        self.current_tag.append(data)
        
    def _handle_equation(self, node, starred=False, fragment=False):
        self.current_tag.append('\begin{align'+('*' if starred else '')+'}\n')
        self.current_tag.append(''.join(str(x) for x in node.contents))
        self.current_tag.append('\end{align'+('*' if starred else '')+'}\n')
        return True
    
    _handle_align = _handle_equation

    def _handle_frametitle(self, node, starred=False, fragment=False):
        tag = self.soup.new_tag("h3")
        self.current_slide.append(tag)
        tag.string = ''.join(node.contents)
        return True #Skip children

    def _handle_lists(self, node, starred=False, fragment=False):
        if node.name == 'itemize':
            container=self.soup.new_tag("ul")
        elif node.name == 'enumerate':
            container=self.soup.new_tag("ol")
        self.current_tag.append(container)
        self.current_tag=container
        for item in node.contents:
            self._walk(item)
            self.current_tag = container
        self.current_tag=container.parent
        return True #Skip children

    _handle_itemize = _handle_lists
    _handle_enumerate = _handle_lists
    
    def _handle_item(self, node, starred=False, fragment=False):
        li=self.soup.new_tag("li")
        if fragment:
            li['class'] = "fragment"

        self.current_tag.append(li)
        self.current_tag=li
        return False

    def _handle_bf(self, node, starred=False, fragment=False):
        container=self.soup.new_tag("b")
        self.current_tag.append(container)
        self.current_tag=container
        for item in node.contents:
            self._walk(item)
            self.current_tag=container
        self.current_tag=container.parent
        return True
    
    def _handle_textbf(self, node, starred=False, fragment=False):
        self.current_tag.append(node.string)
        return True
    
    def _handle_section(self, node, starred=False, fragment=False):
        self.current_tag=self.current_section = self.soup.new_tag("section")
        self.current_section['data-menu-title'] = ''.join(node.contents)
        self.slides.append(self.current_section)
        return True

    def _handle_subsection(self, node, starred=False, fragment=False):
        self.subsection_title = ''.join(node.contents)
        return True
    
    def _handle_unknown(self, node, starred=False, fragment=False):
        print("No handler for ", node.name + ('*' if starred else ''))
        print(repr(list(node.contents)))
        if self.current_slide != None:
            self.current_tag.append('\\%s ' % node.name)
        else:
            print("Outside of frame!")


    def _handle_columns(self, node, starred=False, fragment=False):
        container = self.soup.new_tag("div")
        container['style'] = "display:flex;align-items:center;"     
        self.current_tag.append(container)

        for item in node.contents:
            self.current_tag=container
            self._walk(item)
        return False
        
    def _handle_column(self, node, starred=False, fragment=False):
        container = self.soup.new_tag("div")
        container['style'] = "display:flex;align-items:center;"        
        self.current_tag.append(container)

        print("!!!",repr(list(node.args))) 
        print("###",repr(list(node.contents)))
        exit()
        
        for item in node.contents:
            self.current_tag=container
            self._walk(item)
        return False
        
def readfile(path):
    with open(path, 'r') as f:
        return f.read()


import sys

soup = Tex2Reveal(readfile(sys.argv[1]))
print(soup.slides.prettify())
