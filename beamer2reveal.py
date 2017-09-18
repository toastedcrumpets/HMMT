#!/usr/bin/python3

import re
import os
from bs4 import BeautifulSoup
from TexSoup import TexSoup, TexNode

class Tex2Reveal(object):
    def __init__(self, filepath):
        self.info = {}
        self._handle_document(None) #All variable initialisation is done on \begin{document}

        with open(filepath, 'r') as f:
            code = f.read()

        self.tex_dir = os.path.dirname(filepath)
        
        #Remove comments
        code = re.sub('(?<!\\\\)%.*$', '', code, flags=re.M)
        #Remove inline display math shortcuts
        code = code.replace(r'\[', r'\begin{equation*}')
        code = code.replace(r'\]', r'\end{equation*}')

        #Handle other special characters
        code = code.replace('~', u"\u00A0")
        code = code.replace('---', u"\u2014")
        code = code.replace('--', u"\u2013")
        code = code.replace('``', u"\u201C")
        code = code.replace("''", u"\u201D")

        #Fix my silly use of \bf
        code = code.replace("{\\bf", "\\textbf{")
        
        #Collapse whitespace
        code = re.sub(r'\n\s*\n', '\n\n', code, flags=re.M)

        print("RAWCODE:\n", code)
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
        template = """
<!doctype html>
<html lang="en">
    <head>
	<meta charset="utf-8">
	<title>Heat, Mass, and Momentum Transfer</title>
	<meta name="description" content="Heat Mass and Momentum Transfer notes">
	<meta name="author" content="Marcus Bannerman <m.bannerman@gmail.com">
	<meta name="apple-mobile-web-app-capable" content="yes" />
	<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
	<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, minimal-ui">
	<script src="../reveal.js/lib/js/head.min.js" data-headjs-load="header.js"></script>
    </head>
    <body>
	<div class="reveal">
	    <div class="slides">
		<section>
		    <section>
			<div class="backbox">
			    <h2>Heat, Mass, and Momentum Transfer</h2>
			    <h3>Use the menu <a href="#" onclick="RevealMenu.toggle(); return false;"><i class="fa fa-bars"></i></a> and use the Lectures <i class="fa fa-external-link"></i> select menu.</h3>
			</div>
			<p>
			    Marcus N. Bannerman<br/>
			    <a href="mailto:m.campbellbannerman@abdn.ac.uk">m.campbellbannerman@abdn.ac.uk</a><br/>
			</p>
			<div style="width:10em;">
			    <object type="image/svg+xml" data="img/UoALarge.svg" width="100%" height="100%">
				Your browser does not support SVG
			    </object>
			</div>
		    </section>
		</section>
	    </div>
	    <div class="slide-menu-button" style="left:170px;cursor:pointer;">
		<a class="hide-on-pdf" onclick="document.location = '?print-pdf';" id="PrintButton"><i class="fa fa-print"></i></a>	    
	    </div>
	    <script src="footer.js"></script>
	</div>
    </body>
</html>
"""
        self.current_tag = None
        self.current_slide = None
        self.soup = BeautifulSoup(template, "lxml")
        self.slides = self.soup.div.div
        self.current_section = None
        self._in_equation = False
        self.subsection_title = None

    def push(self, tagname):
        tag = self.soup.new_tag(tagname)
        self.current_tag.append(tag)
        self.current_tag=tag
        return tag

    def pop(self, tagname):
        while self.current_tag.name != tagname:
            self.current_tag = self.current_tag.parent
        self.current_tag = self.current_tag.parent
        return self.current_tag
        
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
        self.current_tag.append('\\begin{align'+('*' if starred else '')+'}\n')
        self.current_tag.append(''.join(str(x) for x in node.contents))
        self.current_tag.append('\\end{align'+('*' if starred else '')+'}\n')
        return True
    
    _handle_align = _handle_equation

    def _handle_frametitle(self, node, starred=False, fragment=False):
        tag = self.soup.new_tag("h3")
        self.current_slide.append(tag)
        tag.string = ''.join(node.contents)
        return True #Skip children

    def _handle_lists(self, node, starred=False, fragment=False):
        if node.name == 'itemize':
            container = self.push("ul")
        elif node.name == 'enumerate':
            container = self.push("ol")
            
        for item in node.contents:
            self._walk(item)
        #Can't pop here, due to the open ended nature of \list
        #commands. Just manually reset.
        self.current_tag = container.parent
        return True #Skip children

    _handle_itemize = _handle_lists
    _handle_enumerate = _handle_lists
    
    def _handle_item(self, node, starred=False, fragment=False):
        if self.current_tag.name == 'li':
            self.pop('li')

        li = self.push('li')
        if fragment:
            li['class'] = "fragment"        
        for item in node.contents:
            self._walk(item)
        #We don't reset to the parent container here, as \item is open
        #ended. Trust that \end{itemize} will close the li in the end.
        return True
    
    def _handle_textbf(self, node, starred=False, fragment=False):
        self.push('b')
        for item in node.contents:
            self._walk(item)
        self.pop('b')
        return True
    
    def _handle_section(self, node, starred=False, fragment=False):
        self.current_tag=self.current_section=self.soup.new_tag("section")
        self.current_section['data-menu-title'] = ''.join(node.contents)
        self.slides.append(self.current_section)
        return True

    def _handle_subsection(self, node, starred=False, fragment=False):
        self.subsection_title = ''.join(node.contents)
        return True
    
    def _handle_columns(self, node, starred=False, fragment=False):
        container = self.push('div')
        container['style'] = "display:flex;align-items:center;"
        for item in node.contents:
            self._walk(item)
        self.pop('div')
        return True
        
    def _handle_column(self, node, starred=False, fragment=False):
        container = self.push('div')
        container['style'] = "flex: 0 0 100% * "+str(list(node.args)[0])[1:-1].replace("\\linewidth", "1").replace("\\textwidth", "1")+";"

        for item in node.contents:
            self._walk(item)
        self.pop('div')
        return True
        
    def _handle_includegraphics(self, node, starred=False, fragment=False):
        filename = str(list(node.args)[-1])[1:-1].replace("figures/", '')

        #print("\n\n!!! Handling includegraphics!")
        print(filename)
        print(repr(list(node.args)))
        print(repr(list(node.contents)))
        print(self.tex_dir)
        path=os.path.join(self.tex_dir, 'figures/vector/'+filename+'.svg')
        if os.path.isfile(path):
            #print("SVG found"+path)
            return True
        
        path=os.path.join(self.tex_dir, 'figures/bitmap/'+filename+'.jpg')
        if os.path.isfile(path):
            #print("jpg found"+path)
            return True

        print("Could not find file "+filename)
        
        return True

    def _handle_unknown(self, node, starred=False, fragment=False):
        print("No handler for ", node.name + ('*' if starred else ''))
        print(repr(list(node.contents)))
        if self.current_slide != None:
            pass
            #self.current_tag.append('\\%s ' % node.name)
        else:
            print("Outside of frame!")

import sys

soup = Tex2Reveal(sys.argv[1])

open('out.html', 'wb').write(soup.soup.encode(formatter='html'))
