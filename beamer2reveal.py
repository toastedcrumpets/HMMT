#!/usr/bin/python3

import re
import os
from bs4 import BeautifulSoup
from TexSoup import TexSoup, TexNode, TexCmd, TexEnv, OArg, RArg

class Tex2Reveal(object):
    def __init__(self, filepath):
        self.info = {}
        self._handle_document(None) #All variable initialisation is done on \begin{document}

        with open(filepath, 'r') as f:
            code = f.read()

        self.tex_dir = os.path.dirname(filepath)
        
        #Remove comments
        code = re.sub('(?<!\\\\)%.*$', '', code, flags=re.M)

        #Add $ to the math environments
        for env in ['align', 'equation']:
            code = code.replace(r'\begin{'+env+'}', r'\begin{'+env+'}$')
            code = code.replace(r'\end{'+env+'}', r'$\end{'+env+'}')
            code = code.replace(r'\begin{'+env+'*}', r'\begin{'+env+'*}$')
            code = code.replace(r'\end{'+env+'*}', r'$\end{'+env+'*}')

        #Handle other special characters
        code = code.replace('~', u"\u00A0")
        code = code.replace('---', u"\u2014")
        code = code.replace('--', u"\u2013")
        code = code.replace('``', u"\u201C")
        code = code.replace("''", u"\u201D")
        code = code.replace("\\ldots", u"\u2026")
        code = code.replace("\\,", u"\u202F")#Replace the half space with a
                                        #simple comma
        
        #Fix my use of \bf and \em, switches go hard on texsoup
        code = code.replace("{\\bf", "\\textbf{")
        code = code.replace("{\\em", "\\textit{")
        code = code.replace("{\\scriptsize", "\\scriptsize{")
        
        #Also the use of \bm which is not supported by mathjax
        code = code.replace("\\bm{", "\\boldsymbol{")
        code = code.replace("\\&", "\\ampersand")

        #There's some common stuff that TexSoup has problems with
        code = code.replace("\\right|}", "\\right| }")
        code = code.replace("\\hfill(", "\\hfill (")
        
        #Collapse whitespace
        code = re.sub(r'\n\s*\n', '\n\n', code, flags=re.M)
        self.soup = TexSoup(code)
        
        #Parse any standalone commands
        nodes = ('title', 'subtitle', 'author', 'institute', 'date', 'logo')
        for node in nodes:
            for elem in self.soup.find_all(node):
                data = list(elem.contents)
                if len(data) != 0:
                    self.info[node] = data
                
        #Walk the document creating the tree
        self._walk(self.soup.find('document'))

    def _walk(self, node):
        if isinstance(node, TexNode):
            name = node.name
            if name == "":
                return;
            
            #print('\n\nname',type(node))
            #print('contents',repr(list(node.contents)))
            #print('args',repr(list(node.args)))
            #print('extra',repr(node.extra))
            #print('children',repr(list(node.children)))

            #Check for <1-> decorators and remove them
            fragment = False
            fragment_search = re.search('<[0-9]+-?[0-9]*>', name)
            if fragment_search != None:
                dec = name[fragment_search.start():fragment_search.end()]
                name = name[:fragment_search.start()]
                if dec != "<1->" and dec != "<->":
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
	    <div class="slides"></div>
	    <div class="slide-menu-button" style="left:170px;cursor:pointer;">
		<a class="hide-on-pdf" onclick="document.location = '?print-pdf';" id="PrintButton"><i class="fa fa-print"></i></a>	    
	    </div>
        <script type="text/x-mathjax-config">
        MathJax.Hub.Config({ TeX: { extensions: ["cancel.js"] }});
        </script>
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
        self.subsection_title = None
        self.table_mode = False
        self.footnote_counter = 1

    def push(self, tagname):
        tag = self.soup.new_tag(tagname)
        self.current_tag.append(tag)
        self.current_tag=tag
        return tag

    def find_parent(self, tagname):
        tag = self.current_tag 
        while tag.name != tagname:
            tag = tag.parent
        return tag

    def pop(self, tagname):
        self.current_tag = self.find_parent(tagname).parent
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

        self.footnote_counter = 1
        return False
                
    # _handle methods return True if the children are to be skipped.
    
    def _handle_str(self, node):
        data = str(node)
        if self.table_mode:
            lines=data.split('\\\\')
            for i,line in enumerate(lines):
                if i:
                    self.pop('tr')
                    self.push('tr')
                    self.push('td')
                cells=line.split('&')
                for j,line in enumerate(cells):
                    if j:
                        self.pop('td')
                        self.push('td')
                    self.current_tag.append(line.strip())
        else:
            lines=data.split('\\\\')
            for i,line in enumerate(lines):
                if i:
                    self.current_tag.append(self.soup.new_tag("br"))
                self.current_tag.append(line)
        
    def _handle_equation(self, node, starred=False, fragment=False):
        self.current_tag.append('\\begin{align'+('*' if starred else '')+'}\n')
        #We need to trim the $ added to make sure TexSoup leaves commands in there alone
        self.current_tag.append(''.join(str(x) for x in node.contents)[1:-1])
        self.current_tag.append('\\end{align'+('*' if starred else '')+'}\n')
        return True
    
    _handle_align = _handle_equation

    def _handle_frametitle(self, node, starred=False, fragment=False):
        tag = self.soup.new_tag("h3")
        self.current_slide.append(tag)
        tag.string = ''.join(node.contents)
        return True #Skip children

    def _handle_titlepage(self, node, starred=False, fragment=False):
        title = self.push('h2')
        self.current_tag.string = self.info['subtitle'][0]
        self.pop('h2')
        return True
    
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
    

    def _handle_wrapper(self, node, starred=False, fragment=False):
        name = node.name
        if fragment:
            fragment_search = re.search('<[0-9]+-?[0-9]*>', name)
            name = name[:fragment_search.start()]
            
        tagtype = {
            'textbf':['b',{}],
            'textit':['i',{}],
            'underline':['u',{}],
            'only':['div',{}],
            'uncover':['div',{}],
            'center':['div',{"class":'center'}],
            'figure':['figure', {}],
            'caption':['figcaption', {}],
        }[name]
        container = self.push(tagtype[0])

        if fragment:
            container['class'] = "fragment"
        if "class" in tagtype[1]:
            container['class'] = tagtype[1]["class"] + (" fragment" if fragment else "")
        
        for item in node.contents:
            self._walk(item)
            
        self.pop(tagtype[0])
        
        return True
        
    _handle_textbf = _handle_wrapper
    _handle_textit = _handle_wrapper
    _handle_underline = _handle_wrapper
    _handle_only = _handle_wrapper
    _handle_uncover = _handle_wrapper
    _handle_figure = _handle_wrapper
    _handle_caption = _handle_wrapper
    _handle_center = _handle_wrapper

    def _handle_href(self, node, starred=False, fragment=False):
        a = self.push('a')
        args = list(node.args)
        a['src'] = args[0]
        self._walk(args[1])
        self.pop('a')
        return True

    def _handle_textcolor(self, node, starred=False, fragment=False):
        span = self.push('span')
        args = list(node.args)
        span['style'] = "color:"+args[0]
        self._walk(args[1])
        self.pop('span')
        return True
        
    
    def _handle_section(self, node, starred=False, fragment=False):
        self.current_tag=self.current_section=self.soup.new_tag("section")
        self.subsection_title = ''.join(node.contents)
        self.slides.append(self.current_section)
        return True

    def _handle_subsection(self, node, starred=False, fragment=False):
        if self.subsection_title == None:
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

        args = list(node.args)
        widtharg = args[0] if isinstance(args[0], RArg) else args[1]
        
        container['style'] = "flex: 1 1 calc(100% * "+str(widtharg)[1:-1].replace("\\linewidth", "1").replace("\\textwidth", "1")+");"

        for item in node.contents:
            self._walk(item)
        self.pop('div')
        return True
            
    def _handle_scriptsize(self, node, starred=False, fragment=False):
        container = self.push('div')
        if fragment:
            container['class'] = "fragment"
        container['style'] = "font-size:0.7em;"
        for item in node.contents:
            self._walk(item)
        self.pop('div')
        return True

    def _handle_reserveandshow(self, node, starred=False, fragment=False):
        args = list(node.args)
        newnode = TexCmd('includegraphics', args=[args[2], args[3]])
        self._handle_includegraphics(newnode, starred, fragment=True)
        return True
    
    def _handle_newline(self, node, starred=False, fragment=False):
        self.current_tag.append(self.soup.new_tag('br'))
        return False

    def _handle_footnote(self, node, starred=False, fragment=False):
        #Add the annotation in place
        span = self.push("span")
        span['class'] = "footnote"
        span.string = str(self.footnote_counter)
        self.pop("span")

        #Check for (and add if needed) the footnote container div
        container = list(self.current_slide.find_all('div', class_='footnote-container'))
        if container:
            container = container[0]
        else:
            container = self.soup.new_tag('div')
            container['class'] = 'footnote-container'
            self.current_slide.append(container)

        #Add a div to the outer slide page for the actual footnote
        footnote = self.soup.new_tag('div')
        footnote['class'] = 'footnote'
        container.append(footnote)
        span = self.soup.new_tag('span')
        span['class'] = "footnote"
        span.string = str(self.footnote_counter)
        footnote.append(span)

        old_loc = self.current_tag
        self.current_tag = footnote
        for item in node.args:
            self._walk(item)        
        self.current_tag = old_loc
        self.footnote_counter += 1
        
        self.current_tag.append(span)
        return False

    def _handle_ignore(self, node, starred=False, fragment=False):
        return True

    _handle_hfill = _handle_ignore
    _handle_vfill = _handle_ignore
    _handle_vspace = _handle_ignore
    _handle_hspace = _handle_ignore
    _handle_logoimage = _handle_ignore

    def _handle_tableofcontents(self, node, starred=False, fragment=False):
        div = self.push('div')
        div['class'] = 'tableofcontents'
        self.pop('div')
        return True

    
    def _handle_includegraphics(self, node, starred=False, fragment=False):
        filename = str(list(node.args)[-1])[1:-1].replace("figures/", '')

        match = re.search("width=([0-9\\.]*)",list(node.args)[0].value)
        linewidth=None
        if match != None:
            linewidth = match.group(1)
            if linewidth == "":
                linewidth = "1"
            linewidth=int(float(linewidth)*100)

        #print(repr(list(node.args)))
        path=os.path.join(self.tex_dir, 'figures/vector/'+filename+'.svg')
        if os.path.isfile(path):
            import xml.etree.ElementTree as ET
            tree = ET.parse(path)
            root = tree.getroot()
            width=root.attrib['width']
            height=root.attrib['height']
            #del root.attrib['width']
            #del root.attrib['height']
            root.attrib['viewBox'] = '0 0 '+str(width)+' '+str(height)
            root.attrib['preserveAspectRatio']="xMidYMid meet"
            tree.write('img/'+filename+'.svg')

            
            tag = self.soup.new_tag('object')
            tag['type'] = "image/svg+xml"
            tag['data'] = 'img/'+filename+'.svg'
            if width != None:
                tag['width'] = str(linewidth)+"%"

            self.current_tag.append(tag)
            return True

        for ext in ['jpg', 'png']:
            path=os.path.join(self.tex_dir, 'figures/bitmap/'+filename+'.'+ext)
            if os.path.isfile(path):
                import shutil
                tag = self.soup.new_tag('img')
                shutil.copy(path, 'img/'+filename+'.'+ext)
                tag['src'] = 'img/'+filename+'.'+ext
                if linewidth != None:
                    tag['style'] = "width:"+str(linewidth)+"%;"
                self.current_tag.append(tag)
                return True
        
        print("Could not find file "+filename)        
        return True
    
    def _handle_tabular(self, node, starred=False, fragment=False):
        table = self.push('table')
        table['style'] = 'border-collapse:collapse;'
        self.push('tr')
        self.push('td')
        self.table_mode = True
        for item in node.contents:
            self._walk(item)
        self.table_mode = False
        self.pop('table')
        return True

    def _handle_hline(self, node, starred=False, fragment=False):
        tr = self.find_parent('tr')
        
        if tr.has_attr('style'):
            tr['style'] = 'border-top:thick solid black;'
        else:
            tr['style'] = 'border-top:thin solid black;'
        return False #Parse the remaining elements

    def _handle_multicolumn(self, node, starred=False, fragment=False):
        td = self.current_tag
        if td.name != "td":
            raise Exception("Unexpected multicolumn in "+td.name+" tag")
        args = list(node.args)
        td['colspan'] = str(args[0])[1:-1]
        td['style'] = "text-align:center;"
        if len(args)>2:
            self._walk(str(args[2])[1:-1])
        return True
    
    def _handle_ampersand(self, node, starred=False, fragment=False):
        self.current_tag.append("&")
        return False
    
    def _handle_unknown(self, node, starred=False, fragment=False):
        print("No handler for ", node.name + ('*' if starred else ''))
        print("\t", repr(node.parent))
        print(repr(list(node.contents)))
        if self.current_slide != None:
            pass
            #self.current_tag.append('\\%s ' % node.name)
        else:
            print("Outside of frame!")
            
import sys

soup = Tex2Reveal(sys.argv[1])

open(os.path.basename(sys.argv[1]).replace('.tex', '.html'), 'w').write(soup.soup.prettify())
