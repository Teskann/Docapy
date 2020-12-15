# -*- coding: utf-8 -*-
"""
This  is  the  Docapy Core file. It contains all the functions to generate the
documentation from a Python project.

This  file should not be run. To run Docapy, edit and run 'edit_and_run_me.py'
instead.     For     more    details,    refer    to    the    documentation :
https://teskann.github.io/docapy/
"""

import re
import os
import shutil
import git
from fnmatch import fnmatch


def parse_docstr(docstr):
    """
    Description
    -----------
    
    Parses the docstring and returns the corresponding HTML. The docstring
    must follow the Numpydoc syntax. This function will detect :
        - Titles : <h3> elements
        - Lists : <ul> and <li> elements
        - Indentations : <div class="indent"> elements
        - Code parts : <div class="code"> elements
    
    Parameters
    ----------
    
    docstr : str
        Docstring to parse. Must follow the NumpyDoc format
    
    Returns
    -------
    
    str
        HTML of the docstring
    
    """

    # Indentation level ......................................................

    def indentation(line):
        """
        Returns the index of the first non-space character

        Parameters
        ----------
        line : str
            String to find the indentation level from

        Returns
        -------
        Index of the first non-space character or None if there is no char

        """

        strip = len(line.lstrip())

        if strip:
            return (len(line) - strip) // 4
        else:
            return None

    # Case with empty string .................................................

    if docstr is None or docstr.strip() == '':
        return "No documentation found for this section"

    html = ''

    # Split Lines ............................................................

    all_lines = docstr.split('\n')

    # Finding minimum indent level ...........................................

    min_ = -1

    for line in all_lines:
        if line.strip() != '':
            i = indentation(line)
            if min_ == -1:
                min_ = i
            elif i < min_:
                min_ = i

    all_lines = [x[4 * min_:] for x in all_lines]

    # Parsing sections .......................................................

    all_sections = []  # List  containing  sections.  Each  section is a dict
    # with a name fiels and a content field

    i_l = len(all_lines) - 1
    last_content = i_l
    for line in all_lines[::-1]:
        if i_l:
            if all(x == '-' for x in line.strip()) and len(line.strip()) > 0:
                if indentation(line) == indentation(all_lines[i_l - 1]):
                    if len(line.strip()) <= len(all_lines[i_l - 1].strip()):
                        content = '\n'.join(all_lines[i_l + 1:last_content])
                        section = {'name': all_lines[i_l - 1].strip(),
                                   'content': content}
                        last_content = i_l - 1
                        all_sections.append(section)
        i_l -= 1

    # If Description section is not explicit
    if last_content > 1 and \
            ''.join([x.strip() for x in all_lines[:last_content]]) != '':
        content = '\n'.join(all_lines[:last_content])
        section = {'name': 'Description',
                   'content': content}
        all_sections.append(section)

    # Parsing to HTML ........................................................

    for section in all_sections[::-1]:
        html += "<h3>" + section['name'] + "</h3>"

        # Parsing section content  . . . . . . . . . . . . . . . . . . . . . .

        sect_lines = section['content'].split('\n')
        last_indent = 0
        code = False  # True if it's a code division ">>> foo(bar)"
        list_ = False  # True if there is a list in the docstring
        code_indent0 = 0
        list_indent0 = 0
        last_line_was_empty = False
        open_div = 0

        for i_l, line in enumerate(sect_lines):
            if line.strip() != '':
                # Finding indent evolution
                if indentation(line) > last_indent and not code:
                    delta = indentation(line) - last_indent
                    while delta > 0:
                        html += '<div class="indent">'
                        open_div += 1
                        delta -= 1

                elif indentation(line) < last_indent and not code and \
                        not list_ or code and \
                        indentation(
                            line) < code_indent0 or list_ and not code:
                    if code:
                        html += "</div>"
                        code = False
                    if list_:
                        if indentation(line) < list_indent0:
                            html += "</li></ul>"
                            list_indent0 = 0
                            list_ = False
                    for _ in range(last_indent - indentation(line)):
                        html += '</div>'
                        open_div -= 1

                content = line
                content = content.replace('&', '&amp;')

                last_indent = indentation(line)

                if code:
                    html += "<br>"

                # Code section
                if content.strip()[:3] == '>>>' and not code:
                    code = True
                    code_indent0 = indentation(line)
                    if not last_line_was_empty:
                        html += "<br>"
                    html += '<div class="code">'

                if code:
                    content = content[4 * code_indent0:]
                    content = content.replace(' ', '&nbsp;')
                else:
                    content = line.strip()
                content = content.replace('<', '&lt;').replace('>', '&gt;')
                content = content.replace("'", '&apos;')
                content = content.replace('"', "&quot;")

                # finding URLs
                urls = set(re.findall(
                    r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))""",
                    content))
                for url in urls:
                    rep = '<a href="' + url + '">' + url + "</a>"
                    content = content.replace(url, rep)

                # List section
                if content[:2] in ['- ', '* '] and not code:
                    content = content[2:]
                    if not list_:
                        html += '<ul>'
                        list_ = True
                        list_indent0 = indentation(line)
                    else:
                        html += "</li>"
                    html += '<li>'

                # Bold before ':'
                if not code and "</a>" not in content:
                    sp = content.split(':')
                    if len(sp) > 1:
                        content = "<b>" + sp[0] + "</b>" + ':' + \
                                  ':'.join(sp[1:])

                # Adding content
                html += ' ' + content
                last_line_was_empty = False

            # Empty line
            else:
                if code:
                    html += "</div>"
                    code = False
                if list_:
                    for _ in range(last_indent - list_indent0):
                        html += "</div>"
                        open_div -= 1
                    last_indent = list_indent0
                    html += "</li></ul>"
                    list_ = False
                if i_l != 0:
                    html += "<br>"
                last_line_was_empty = True

        # Closing section
        if code:
            html += "</div>"
            code = False
        if list_:
            html += "</li></ul>"
            list_ = False

        while open_div > 0:
            html += "</div>"
            open_div -= 1
    return html


# Generate HTML block from function __________________________________________

def generate_html_from_fct(definition, docstr, type_):
    """
    Description
    -----------
    
    Generates the HTML block from a function/class and its docstring
    
    The  generated  HTML is set inside a <details> elements that is NOT closed
    to  allow  nested  structures.  This  element should be closed in a higher
    level function.
    
    For more details about the HTML generation, see the function parse_docstr
    
    Parameters
    ----------
    
    definition : str
        Function / class definition line
    
    docstr : str
        Docstring of the function / class. Must follow the numpydoc format
        Can be None if no documentation is available
        
    type_ : str
        Content type. Can be "class" for classes or "def" for functions
    
    Returns
    -------
    
    html : str
        HTML of the docstring
    
    """

    fname = definition.split('(')[0]
    rest = '('.join(definition.split('(')[1:])

    html = "<details><summary>" + '<span class="def">' + type_ + \
           '</span> <span class="blue">' + fname + '</span>' + \
           ('(' if rest != '' else '') + rest + \
           '</summary>' + \
           parse_docstr(docstr)
    return html


# Detect Imports _____________________________________________________________

def detect_imports(file_path, all_files):
    """
    Description
    -----------
    
    Detects all the imported files / modules in the file_text
    
    Parameter
    ---------
    
    file_path : str
        String containing Python file path
    
    all_files : list of str
        List of all the files of the project. Every element is the path to the
        py file : "./<pathToTheFile>/file.py" where . is the project directory
        List must be sorted in alphabetical order
        
    Returns
    -------
    
    Dict of lists
        {'internal' : Internal imports (from this project),
         
         'external' : External imports (from other)}
    
    """
    with open(file_path, 'r', encoding="utf8") as f:
        file_text = f.read()

        all_lines = file_text.split('\n')
        imports = {'internal': [],
                   'external': []}

        module_names = [x.split('/')[-1][:-3] for x in all_files]

        docstr_smp = False
        docstr_dbl = False

        # Ignoring docstring declarations
        for line in all_lines:
            if '"""' in line and not docstr_smp:
                if docstr_dbl:
                    docstr_dbl = False
                    line = line.split('"""')[1]
                else:
                    docstr_dbl = True
            elif "'''" in line and not docstr_dbl:
                if docstr_smp:
                    docstr_smp = False
                    line = line.split("'''")[1]
                else:
                    docstr_smp = True

            if not docstr_dbl and not docstr_smp:
                strip = line.strip()
                if strip[:7] == "import ":
                    imps = strip[7:].strip().split(',')
                    imps = [x.split(' ')[0] for x in imps]
                    for imp in imps:
                        if imp in module_names:
                            imports['internal'].append(imp)
                        else:
                            imports['external'].append(imp)
                elif strip[:5] == "from ":
                    imp = strip[5:].strip().split(' ')[0]
                    if imp in module_names:
                        imports['internal'].append(imp)
                    else:
                        imports['external'].append(imp)
        f.close()

        imports['internal'] = list(set(imports['internal']))
        imports['external'] = list(set(imports['external']))

        return imports


# Imports to HTML ____________________________________________________________

def imports_to_html(files, file, imports):
    """
    Description
    -----------
    
    Generates  the  HTML block for the side menu for navigation between docapy
    files. The block is a div which class is "sideMenu". Folders are <details>
    elements. Files are hyperlinks <a> elements.

    Parameters
    ----------
    files : list of str
        List of all the files of the project. Every element is the path to the
        py file : "./<pathToTheFile>/file.py" where . is the project directory
        List must be sorted in alphabetical order
    
    file : str
        Path of the file for which you want to generate the imports block
    
    imports : dict of lists
        {'internal' : Internal imports (from this project),
         
         'external' : External imports (from other)}

    Returns
    -------
    str
        HTML block containing the imports
    """

    html = ''
    if imports['internal'] != [] or imports['external'] != []:
        html += '<h2>Imports</h2>'

    module_names = [x.split('/')[-1][:-3] for x in files]

    # Internal imports
    if imports['internal']:
        html += '<h3>From This Project</h3><ul>'
        for imp in imports['internal']:
            link = '../' * (len(file.split('/')) - 2)
            link += files[module_names.index(imp)][:-3] + '.html'
            html += '<li>'
            html += '<a href="' + link + '" class="import">' + imp + '</a>'
            html += '</li>'
        html += '</ul>'

    # External imports
    if imports['external']:

        external_pip = []
        stdpgk = []

        # List of standard libraries
        stdlib = ["string", 're', 'difflib', 'textwrap', 'unicodedata',
                  'stringprep', 'readline', 'rlcompleter', 'struct', 'codecs',
                  'datetime', 'calendar', 'collections', 'collections.abc',
                  'heapq', 'bisect', 'array', 'weakref', 'types', 'copy',
                  'pprint', 'reprlib', 'enum', 'numbers', 'math', 'cmath',
                  'decimal', 'fractions', 'random', 'statistics', 'itertools',
                  'functools', 'operator', 'pathlib', 'os.path', 'fileinput',
                  'stat', 'filecmp', 'tempfile', 'glob', 'fnmatch',
                  'linecache', 'shutil', 'pickle', 'copyreg', 'shelve',
                  'marshal', 'dbm', 'sqlite3', 'zlib', 'gzip', 'bz2', 'lzma',
                  'zpifile', 'tarfile', 'csv', 'configparser', 'netrc',
                  'xdrlib', 'plistlib', 'hashlib', 'hmac', 'secrets', 'os',
                  'io', 'time', 'argparse', 'getopt', 'logging',
                  'logging.config', 'logging.handlers', 'getpass', 'curses',
                  'curses.textpad', 'curses.ascii', 'curses.panel',
                  'platform', 'errno', 'ctypes', 'threading',
                  'multiprocessing', 'multiprocessing.shared_memory',
                  'concurrent', 'concurrent.futures', 'subprocess', 'sched',
                  'queue', '_thread', '_dummy_thread', 'dummy_threading',
                  'contextvars', 'asyncio', 'socket', 'ssl', 'select',
                  'selectors', 'asyncore', 'asynchat', 'signal', 'mmap',
                  'email', 'json', 'mailcap', 'mailbox', 'mimetypes',
                  'base64', 'binhex', 'binascii', 'quopri', 'uu', 'html',
                  'html.parser', 'html.entities', 'xml.etree.ElementTree',
                  'xml.dom', 'xml.dom.minidom', 'xml.dom.pulldom', 'xml.sax',
                  'xml.sax.handler', 'xml.sax.saxutils', 'xml.sax.xmlreader',
                  'xml.parsers.expat', 'webbrowser', 'cgi', 'cgitb',
                  'wsgiref', 'urllib', 'urllib.request', 'urllib.response',
                  'urllib.parse', 'urllib.error', 'urllib.robotparser',
                  'http', 'http.client', 'ftplib', 'poplib', 'imaplib',
                  'nntplib', 'smtplib', 'smtpd', 'telnetlib', 'uuid',
                  'socketserver', 'http.server', 'http.cookies',
                  'http.cookiejar', 'xmlrpc', 'xmlrpc.client',
                  'xmlrpc.server', 'ipaddress', 'audioop', 'aifc', 'sunau',
                  'wave', 'chunk', 'colorsys', 'imghdr', 'sndhdr',
                  'ossaudiodev', 'gettext', 'locale', 'turtle', 'cmd',
                  'shlex', 'tkinter', 'tkinter.ttk', 'tkinter.tix',
                  'tkinter.scrolledtext', 'IDLE', 'typing', 'pydoc',
                  'doctest', 'unittest', 'unittest.mock', 'unittest.mock',
                  '2to3', 'test', 'test.support',
                  'test.support.script_helper', 'audit_events', 'bdb',
                  'faulthandler', 'pdb', 'profile', 'timeit', 'trace',
                  'tracemalloc', 'distutils', 'ensurepip', 'venv', 'zipapp',
                  'sys', 'sysconfig', 'builtins', '__main__', 'warnings',
                  'dataclasses', 'contextlib', 'abc', 'atexit', 'traceback',
                  '__future__', 'gc', 'inspect', 'site', 'code', 'codeop',
                  'zipimport', 'pkgutil', 'modulefinder', 'runpy',
                  'importlib', 'importlib.metadata', 'parser', 'ast',
                  'symtable', 'symbol', 'token', 'keyword', 'tokenize',
                  'tabnanny', 'pyclbr', 'py_compile', 'compileall', 'dis',
                  'pickletools', 'formatter', 'msilib', 'msvcrt', 'winreg',
                  'winsound', 'posix', 'pwd', 'spwd', 'grp', 'crypt',
                  'termios', 'tty', 'pty', 'fcntl', 'pipes', 'resource',
                  'nis', 'syslog', 'optparse', 'imp']

        for imp in imports['external']:
            if imp in stdlib:
                stdpgk.append(imp)

            else:

                external_pip.append(imp.split('.')[0])

        html += '</ul>'

        if stdpgk:
            html += '<h3>Standard Packages</h3><ul>'
            for imp in stdpgk:
                link = "https://docs.python.org/3/library/" + imp + '.html'
                html += '<li>'
                html += '<a href="' + link + '" class="import">' + imp + \
                        '</a>'
                html += '</li>'
            html += "</ul>"

        external_pip = list(set(external_pip))
        if external_pip != []:
            html += '<h3>External Packages</h3><ul>'
            for imp in external_pip:
                link = 'https://pypi.org/project/' + imp.split('.')[0]
                html += '<li>'
                html += '<a href="' + link + '" class="import">' + imp + \
                        '</a>'
                html += '</li>'
            html += '</ul>'

            html += "If you don't have them, you can install these " \
                    "packages" + \
                    ' running <a href="https://pypi.org/project/pip/">' \
                    'pip</a> :' + \
                    '<br>'

            for imp in external_pip:
                html += '<div class="code">'
                html += '$ <span class="blue">pip</span> install ' + imp
                html += '<br></div>'

    return html


# Geenerate doc from filename ________________________________________________

def generate_doc(filename):
    """
    Description
    -----------
    
    Generates a HTML block for every docstring in the file <filename>
    
    The documentation strings must follow the Numpy docstring format.
    
    This function :
        - Opens the file "filename"
        - Detects all the functions and classes declarations
        - Generates HTML for every docstring
        - Generates HTML for the docstring of the file

    Parameters
    ----------
    filename : string
        Path leading to the file you want to generate the documentation from.

    Returns
    -------
    string
        HTML string containing the documentation

    """

    # opening file ...........................................................

    with open(filename, 'r', encoding="utf8") as file:

        # Finding all the docstrings .........................................

        text = file.read()

        all_lines = text.split('\n')

        last_obj_ind = 0  # Last object indentation level

        i_l = 0  # Line number (index)

        # The  following  variable  is the list of all the functions / classes
        # that  are  defined in the file. Every element of this list is a dict
        # containing the following fields :
        #       - def :         (str)   Fct / class definition line
        #       - docstring :   (str)   Docstring of the fct/class
        #       - last_ind :    (int)   Lowest  indentation  level encountered
        #                               since last function / class definition
        #       - ind :         (int)   Indentation level of the fct/class
        #       - type :        (str)   "class" of "def"
        def_list = []

        # For all lines of the Python file
        while i_l < len(all_lines):

            line = all_lines[i_l]  # Current Line
            i_c = 0  # Char of the current line index
            i_c_is_1st_nonspace_char = True

            # For each char of the line
            indentation_level = 0
            while i_c < len(line):

                # Finding indentation level  . . . . . . . . . . . . . . . . .

                while line[i_c] == ' ':
                    indentation_level += 1
                    i_c += 1
                    while i_c == len(line):

                        i_l += 1
                        if i_l >= len(all_lines): break
                        line = all_lines[i_l]
                        i_c = 0
                        indentation_level = 0
                        i_c_is_1st_nonspace_char = True
                    if i_l >= len(all_lines):
                        break

                if i_c == len(line):
                    break
                if i_l >= len(all_lines):
                    break

                if not i_c_is_1st_nonspace_char and \
                        indentation_level < last_obj_ind:
                    last_obj_ind = indentation_level

                # Checking if the line is commented  . . . . . . . . . . . . .

                if line[i_c] == '#':
                    break

                # Finding functions definitions  . . . . . . . . . . . . . . .

                function_found = False
                fun_def = ''

                if i_c + 4 < len(line) and line[i_c:i_c + 4] in ['def ',
                                                                 'def\\'] \
                        and i_c_is_1st_nonspace_char:

                    i_c += 3

                    fun_def = ''

                    # Finding the opening parenthesis
                    while line[i_c] != '(':
                        i_c += 1
                        # Going to the next line if necessary
                        if i_c == len(line):
                            i_l += 1
                            line = all_lines[i_l]
                            i_c = 0
                            i_c_is_1st_nonspace_char = True
                        fun_def += line[i_c]

                    # Mathcing the closing parenthesis
                    open_par = 1
                    i_c += 1
                    while open_par != 0:
                        # Ignoring parentheses in strings
                        if i_c > 0 and line[i_c] == '"':
                            fun_def += line[i_c]
                            i_c += 1
                            # Going to the next line if necessary
                            if i_c == len(line):
                                i_l += 1
                                line = all_lines[i_l]
                                i_c = 0
                                i_c_is_1st_nonspace_char = True
                            fun_def += line[i_c]

                            while line[i_c] != '"':
                                i_c += 1
                                # Going to the next line if necessary
                                if i_c == len(line):
                                    i_l += 1
                                    line = all_lines[i_l]
                                    i_c = 0
                                    i_c_is_1st_nonspace_char = True
                                fun_def += line[i_c]
                            fun_def = fun_def[:-1]
                        if i_c > 0 and line[i_c] == "'":
                            fun_def += line[i_c]
                            i_c += 1
                            # Going to the next line if necessary
                            if i_c == len(line):
                                i_l += 1
                                line = all_lines[i_l]
                                i_c = 0
                                i_c_is_1st_nonspace_char = True
                            fun_def += line[i_c]
                            while line[i_c] != "'":
                                i_c += 1
                                # Going to the next line if necessary
                                if i_c == len(line):
                                    i_l += 1
                                    line = all_lines[i_l]
                                    i_c = 0
                                    i_c_is_1st_nonspace_char = True
                                fun_def += line[i_c]
                            fun_def = fun_def[:-1]

                        if line[i_c] == '(':
                            open_par += 1
                        elif line[i_c] == ')':
                            open_par -= 1
                        fun_def += line[i_c]
                        i_c += 1
                        # Going to the next line if necessary
                        if i_c == len(line):
                            i_l += 1
                            line = all_lines[i_l]
                            i_c = 0
                            i_c_is_1st_nonspace_char = True

                    # Until we reach ':'
                    while line[i_c] != ':':
                        i_c += 1
                        if i_c == len(line):
                            i_l += 1
                            line = all_lines[i_l]
                            i_c = 0
                            i_c_is_1st_nonspace_char = True

                    fun_def = fun_def.replace(" ", "").replace(',', ', ')

                    function_found = True

                # Finding class definitions  . . . . . . . . . . . . . . . . .

                class_found = False

                if i_c + 6 < len(line) and line[i_c:i_c + 6] in ['class ',
                                                                 'class\\'] \
                        and i_c_is_1st_nonspace_char:

                    class_found = True

                    i_c += 5

                    fun_def = ''

                    # Until we reach ':'
                    while line[i_c] != ':':
                        fun_def += line[i_c]
                        # Mathcing the closing parenthesis
                        if line[i_c] == '(':
                            open_par = 1
                            i_c += 1
                            while open_par != 0:
                                if line[i_c] == '(':
                                    open_par += 1
                                elif line[i_c] == ')':
                                    open_par -= 1
                                fun_def += line[i_c]
                                if open_par != 0:
                                    i_c += 1
                                # Going to the next line if necessary
                                if i_c == len(line):
                                    i_l += 1
                                    line = all_lines[i_l]
                                    i_c = 0
                                    i_c_is_1st_nonspace_char = True
                        i_c += 1
                        if i_c == len(line):
                            i_l += 1
                            line = all_lines[i_l]
                            i_c = 0
                            i_c_is_1st_nonspace_char = True

                    fun_def = fun_def.replace(" ", "").replace(',', ', ')

                    function_found = True

                # Finding docstring  . . . . . . . . . . . . . . . . . . . . .

                if function_found or class_found:

                    # Finding docstring
                    i_c += 1
                    while i_c == len(line):
                        i_l += 1
                        line = all_lines[i_l]
                        i_c = 0
                        i_c_is_1st_nonspace_char = True
                    if len(line) > 0:
                        while line[i_c] == ' ':
                            i_c += 1
                            while i_c == len(line):
                                i_l += 1
                                line = all_lines[i_l]
                                i_c = 0
                                i_c_is_1st_nonspace_char = True

                    if line[i_c:i_c + 3] == '"""':
                        docstrquotes = '"'
                    elif line[i_c:i_c + 3] == "'''":
                        docstrquotes = "'"
                    else:
                        docstrquotes = ''

                    if docstrquotes != '':
                        i_c += 3
                        lastchar = line[i_c - 1]
                        docstr = ''
                        match = 3 * docstrquotes
                        while line[i_c:i_c + 3] != match or lastchar == '\\':
                            i_c += 1
                            while i_c >= len(line):
                                docstr += '\n'
                                i_l += 1
                                line = all_lines[i_l]
                                i_c = 0
                                i_c_is_1st_nonspace_char = True
                            lastchar = line[i_c - 1]
                            docstr += line[i_c]
                    else:
                        docstr = None

                    if docstr is not None:
                        docstr = docstr[:-1]
                    type_ = "class" if class_found else "def"
                    # Adding the object to the list
                    def_dict = {'def': fun_def,
                                'docstring': docstr,
                                'last_ind': last_obj_ind,
                                'ind': indentation_level,
                                'type': type_}

                    def_list.append(def_dict)

                    last_obj_ind = indentation_level

                # Checking quotes to not consider strings  . . . . . . . . . .

                # If the quote char is not preceded by a backslash
                if i_c > 0 and line[i_c - 1] != '\\' or i_c == 0:

                    # If we encounter a single quote
                    if line[i_c] == "'":

                        # Loop until the string closes
                        while line[i_c] != "'" or i_c > 0 and line[i_c - 1] \
                                == '\\':
                            i_c += 1

                            # Going to the next line if necessary
                            if i_c == len(line):
                                i_l += 1
                                line = all_lines[i_l]
                                i_c = 0
                                i_c_is_1st_nonspace_char = True

                    # If we encounter double quotes
                    if line[i_c] == '"':

                        # Loop until the string closes
                        while line[i_c] != '"' or i_c > 0 and line[i_c - 1] \
                                == '\\':
                            i_c += 1

                            # Going to the next line if necessary
                            if i_c == len(line):
                                i_l += 1
                                line = all_lines[i_l]
                                i_c = 0
                                i_c_is_1st_nonspace_char = True

                i_c_is_1st_nonspace_char = False

                # Going to the next char
                i_c += 1

            # Going to the next line
            i_l += 1

        # Generating the HTML ................................................

        html = ''
        if def_list:

            html += generate_html_from_fct(def_list[0]['def'],
                                           def_list[0]['docstring'],
                                           def_list[0]['type'])
            delta_indent = 0
            i_f = 1
            while i_f < len(def_list):
                fct = def_list[i_f]
                delta_indent = (fct['ind'] - fct['last_ind']) // 4

                # Fct is declared in the previous fct
                if delta_indent > 0:
                    # It is a nested function / class
                    if def_list[i_f - 1]['type'] == 'def':
                        # Nested function
                        if fct['type'] == 'def':
                            html += '<h3>Nested Functions</h3>'
                        # Inner class
                        else:
                            html += '<h3>Inner Classes</h3>'
                    # It is an inner class or a method
                    else:
                        # Method
                        if fct['type'] == 'def':
                            html += '<h3>Methods</h3>'
                        # Inner class
                        else:
                            html += '<h3>Inner Classes</h3>'

                    html += generate_html_from_fct(fct['def'],
                                                   fct['docstring'],
                                                   fct['type'])
                else:
                    while delta_indent <= 0:
                        html += '</details>'
                        delta_indent += 1
                    html += generate_html_from_fct(fct['def'],
                                                   fct['docstring'],
                                                   fct['type'])

                i_f += 1

            while delta_indent >= 0:
                html += '</details>'
                delta_indent -= 1
            html = "<h2>Functions & Classes</h2>" + html

        # Finding the file docstring .........................................

        i_l = 0
        docstr_found_dbl = False
        docstr_found_smp = False
        file_docstr = ""
        for line in all_lines:

            if docstr_found_dbl or docstr_found_smp:
                file_docstr += line + '\n'

            # Ignoring empty lines
            if line.strip() == '':
                continue

            # Ignoring comment lines
            if line.strip()[0] == '#':
                continue

            # Docstring found
            if line[:3] == '"""':
                if not (docstr_found_dbl or docstr_found_smp):
                    docstr_found_dbl = True
                    file_docstr += file_docstr[3:] + '\n'
                elif docstr_found_dbl:
                    break

            # Docstring found
            elif line[:3] == "'''":
                if not (docstr_found_dbl or docstr_found_smp):
                    docstr_found_smp = True
                    file_docstr += file_docstr[3:] + '\n'
                elif docstr_found_smp:
                    break

            # No docstring
            elif not (docstr_found_dbl or docstr_found_smp):
                break
        file_docstr = file_docstr[:-3]

        par = parse_docstr(file_docstr).replace('<h3>Description</h3>', '')

        html = "<h2>File Description</h2>" + par + html

        # Adding content division around HTML
        html = '<div class="content">' + html + "</div>"
    return html


# Generate Navigation Menu ___________________________________________________

def side_menu(files, file_):
    """
    Description
    -----------
    
    Generates  the  HTML block for the side menu for navigation between docapy
    files. The block is a div which class is "sideMenu". Folders are <details>
    elements. Files are hyperlinks <a> elements.

    Parameters
    ----------
    files : list of str
        List of all the files of the project. Every element is the path to the
        py file : "./<pathToTheFile>/file.py" where . is the project directory
        List must be sorted in alphabetical order
    
    file_ : str
        Path of the file for which you want to generate the menu block

    Returns
    -------
    str
        HTML block containing the side menu
    """

    pathback = '../' * (len(file_.split('/')) - 2)

    # Creating HTML block
    html = '<div class="sideMenu"><span class="browse">Browse Project ' \
           'Files' + '</span>'

    lastfile = ['.']
    for file in files:

        sub_dirs = file.split('/')[1:]

        open_details = len(lastfile) - 1

        # Checking similarities with the last file
        details_to_open = []
        for i_s, subdir in enumerate(sub_dirs[:-1]):
            if subdir == lastfile[i_s]:
                open_details -= 1
            else:
                details_to_open += sub_dirs[i_s:-1]
                break

        for _ in range(open_details):
            html += "</details>"

        for det in details_to_open:
            html += '<details class="menuDetails"><summary class="menuSum' + \
                    'mary">' + det + '</summary>'

        if file_ == file:
            html += '<span class="blue">'
        html += '<a href="' + pathback + '/'.join(sub_dirs[:-1]) + \
                ('/' if len(sub_dirs[:-1]) else '') + sub_dirs[-1][:-3] + \
                '.html" class="menua">' + sub_dirs[-1] + '</a>'
        if file == file_:
            html += "</span>"

        lastfile = sub_dirs

    # Closing the remaining opened details
    for _ in range(len(lastfile) - 1):
        html += "</details>"

    return html + "</div>"


# Generate the html header ___________________________________________________

def html_header(file, project_name, github):
    """
    Description
    -----------
    
    Generates the HTML header for the specified file and the specified project
    
    Parameters
    ----------
    
    file : str
        Path of the Python file corresponding to the HTML file
    
    project_name : str
        Name of your project
    
    github : str
        Github link of the project
    
    Returns
    -------
    
    str
        HTML block containing the header
    
    """

    filename = file.split('/')[-1]

    # Metadata
    html = '<!doctype html><html lang="en"><head><meta charset="utf-8">' + \
           '<title>' + project_name + ' Documentation - ' + filename + \
           '</title>'
    html += '<meta name="author" content="' + 'Docapy' + '">'

    # CSS Link
    html += '<link rel="stylesheet" href="' + '../' * (
            len(file.split('/')) - 2) + 'style.css"></head><body>'

    # Navigation Bar
    html += '<div class="navbar"><a href="' + '../' * \
            (len(file.split('/')) - 2) + \
            'index.html" class="titla"><span class="title"><span ' \
            'class="blue">' + project_name + '</span>' + \
            ' Documentation</span></a><span class="links"><a href="' + \
            github + '">View Github</a><a href="' + \
            'https://github.com/Teskann/Docapy">About Docapy</a></span>' \
            '</div>'

    return html


# Generate HTML file for an entire project ___________________________________

def html_for_project(directory, project_name, github, color='cyan'):
    """
    Description
    -----------
    
    Generates  many  HTML files for all the *.py files in the given directory.
    Saves  every  HTML  file  in  a  directory  named  "docapy". The file tree
    structure  of the project is copied in this folder. Every *py file has his
    own HTML file containing all its documentation and references to the other
    HTML files of the project.
    
    This  function  also  creates  an  index.html  file containing the project
    overview.
    
    If  docapy  documentation  already  exists  for  this  project, it will be
    overwritten.
    
    Parameters
    ----------
    
    directory : str
        Directory of your project
    
    project_name : str
        Name of your project
    
    github : str
        Github link of the project
    
    color : str, optional
        Accent color for the documentation. It can be one of these values :
            - "blue"
            - "cyan" (default)
            - "red"
            - "green"
            - "orange"
            - "purple"
            - "#XXXXXX" where XXXXXX is a hexadecimal color value (custom)
    
    Returns
    -------
    
    None
    
    """

    # File management ........................................................

    # Moving to the project directory
    abspath = os.path.abspath(directory).replace('\\', '/')
    os.chdir(directory)

    # Finding all *.py files if git  . . . . . . . . . . . . . . . . . . . . .

    g = git.cmd.Git(".")
    try:
        files = g.ls_files().split('\n')
        all_files = []
        for file in files:
            if fnmatch(file, "*.py"):
                all_files.append(file.replace('\\', '/'))

    # Find all *.py files if no git  . . . . . . . . . . . . . . . . . . . . .
    except git.exc.GitCommandError:
        print("Git repository not found for the current project. "
              "Trying to match all *.py files instead")

        all_files = []
        pattern = "*.py"
        for path, _, files in os.walk('.'):
            for name in files:
                if fnmatch(name, pattern):
                    all_files.append(os.path.join(path, name)
                                     .replace('\\', '/'))

    # Creates the docapy directory
    if os.path.exists('docapy'):
        shutil.rmtree('docapy')
    os.makedirs("docapy")

    # Writing the HTML files .................................................

    external_imports = []
    stdlib = ["string", 're', 'difflib', 'textwrap', 'unicodedata',
              'stringprep', 'readline', 'rlcompleter', 'struct', 'codecs',
              'datetime', 'calendar', 'collections', 'collections.abc',
              'heapq', 'bisect', 'array', 'weakref', 'types', 'copy',
              'pprint', 'reprlib', 'enum', 'numbers', 'math', 'cmath',
              'decimal', 'fractions', 'random', 'statistics', 'itertools',
              'functools', 'operator', 'pathlib', 'os.path', 'fileinput',
              'stat', 'filecmp', 'tempfile', 'glob', 'fnmatch', 'linecache',
              'shutil', 'pickle', 'copyreg', 'shelve', 'marshal', 'dbm',
              'sqlite3', 'zlib', 'gzip', 'bz2', 'lzma', 'zpifile', 'tarfile',
              'csv', 'configparser', 'netrc', 'xdrlib', 'plistlib', 'hashlib',
              'hmac', 'secrets', 'os', 'io', 'time', 'argparse', 'getopt',
              'logging', 'logging.config', 'logging.handlers', 'getpass',
              'curses', 'curses.textpad', 'curses.ascii', 'curses.panel',
              'platform', 'errno', 'ctypes', 'threading', 'multiprocessing',
              'multiprocessing.shared_memory', 'concurrent',
              'concurrent.futures', 'subprocess', 'sched', 'queue', '_thread',
              '_dummy_thread', 'dummy_threading', 'contextvars', 'asyncio',
              'socket', 'ssl', 'select', 'selectors', 'asyncore', 'asynchat',
              'signal', 'mmap', 'email', 'json', 'mailcap', 'mailbox',
              'mimetypes', 'base64', 'binhex', 'binascii', 'quopri', 'uu',
              'html', 'html.parser', 'html.entities', 'xml.etree.ElementTree',
              'xml.dom', 'xml.dom.minidom', 'xml.dom.pulldom', 'xml.sax',
              'xml.sax.handler', 'xml.sax.saxutils', 'xml.sax.xmlreader',
              'xml.parsers.expat', 'webbrowser', 'cgi', 'cgitb', 'wsgiref',
              'urllib', 'urllib.request', 'urllib.response', 'urllib.parse',
              'urllib.error', 'urllib.robotparser', 'http', 'http.client',
              'ftplib', 'poplib', 'imaplib', 'nntplib', 'smtplib', 'smtpd',
              'telnetlib', 'uuid', 'socketserver', 'http.server',
              'http.cookies', 'http.cookiejar', 'xmlrpc', 'xmlrpc.client',
              'xmlrpc.server', 'ipaddress', 'audioop', 'aifc', 'sunau',
              'wave', 'chunk', 'colorsys', 'imghdr', 'sndhdr', 'ossaudiodev',
              'gettext', 'locale', 'turtle', 'cmd', 'shlex', 'tkinter',
              'tkinter.ttk', 'tkinter.tix', 'tkinter.scrolledtext', 'IDLE',
              'typing', 'pydoc', 'doctest', 'unittest', 'unittest.mock',
              'unittest.mock', '2to3', 'test', 'test.support',
              'test.support.script_helper', 'audit_events', 'bdb',
              'faulthandler', 'pdb', 'profile', 'timeit', 'trace',
              'tracemalloc', 'distutils', 'ensurepip', 'venv', 'zipapp',
              'sys', 'sysconfig', 'builtins', '__main__', 'warnings',
              'dataclasses', 'contextlib', 'abc', 'atexit', 'traceback',
              '__future__', 'gc', 'inspect', 'site', 'code', 'codeop',
              'zipimport', 'pkgutil', 'modulefinder', 'runpy', 'importlib',
              'importlib.metadata', 'parser', 'ast', 'symtable', 'symbol',
              'token', 'keyword', 'tokenize', 'tabnanny', 'pyclbr',
              'py_compile', 'compileall', 'dis', 'pickletools', 'formatter',
              'msilib', 'msvcrt', 'winreg', 'winsound', 'posix', 'pwd',
              'spwd', 'grp', 'crypt', 'termios', 'tty', 'pty', 'fcntl',
              'pipes', 'resource', 'nis', 'syslog', 'optparse', 'imp']

    for file in all_files:
        print(file)

        # Moving to the python file directory
        os.chdir(abspath)

        # Generate file documentation
        html = generate_doc(file)

        # Detecting imports
        imports = detect_imports(file, all_files)
        imphtml = imports_to_html(all_files, file, imports)
        for imp in imports['external']:
            if imp not in stdlib and imp.split('.')[0] not in \
                    external_imports:
                external_imports.append(imp.split('.')[0])

        # Adding imports in the middle of the documentation
        ht = html.split('<h2>Functions & Classes</h2>')
        if len(ht) > 1:
            html = ht[0] + imphtml + '<h2>Functions & Classes</h2>' + \
                   '<h2>Functions & Classes</h2>'.join(ht[1:])
        else:
            html = ht[0][:-6] + imphtml + "</div>"

        # Moving to the docapy root directory
        os.chdir(abspath + "/docapy")

        # Creating folders to the file path
        sub_dirs = file.split('/')
        for sub_dir in sub_dirs[:-1]:
            if sub_dir == '.':
                continue
            # Creates the directory
            if not os.path.exists(sub_dir):
                os.makedirs(sub_dir)
            os.chdir('./' + sub_dir)

        # opening / Creating the html file
        with open(sub_dirs[-1][:-3] + '.html', 'w', encoding="utf8") as f:
            html_ = html_header(file, project_name, github)
            html_ += "<h1>" + file.split('/')[-1] + "</h1>"
            html_ += side_menu(all_files, file)
            html = html_ + html + "</body></html>"
            f.write(html)
            f.close()

    # Creating index html ....................................................

    os.chdir(abspath + "/docapy")
    with open('index.html', 'w', encoding="utf8") as f:
        html = html_header('./index.py', project_name, github)
        html += side_menu(all_files, './index.py')
        html += "<h1>" + project_name.upper() + " DOCUMENTATION" + "</h1>"
        html += '<div class="content"><h2>Welcome !</h2>'
        html += '<p>Welcome to the documentation of the ' + \
                project_name + ' project !<br><br>This website inventories ' \
                               'all ' + \
                'the documentation for all the Python files (*.py) of the ' \
                'project'
        html += '. There is one page per file. You can browse files' + \
                ' now using the browser on the left.<br>This ' \
                'website contains ' + \
                'the documentation for all the functions and classes' \
                ' of the ' + \
                project_name + ' project.<br></p>'
        html += '<h2>Getting Started</h2><h3>Get the Project</h3>' + \
                '</p>First clone the git repository :<br>' \
                '<div class="code">$ ' + \
                '<span class="blue">git</span> <span class="def">' \
                'clone</span> ' + \
                '<a href="' + github + '">' + github + '</a></div>' \
                                                       'Then move to the' + \
                ' project folder :<br><div class="code">$ <span ' \
                'class="blue">cd' + \
                '</span> ./' + github.split('/')[-1] + '</div>'

        # Adding imports
        if external_imports:
            html += '<h3>Install Modules</h3>This project uses' + \
                    ' the following non-standard modules :<ul>'
            external_imports = list(set(external_imports))
            external_imports.sort(key=str.casefold)

            for imp in external_imports:
                link = 'https://pypi.org/project/' + imp.split('.')[0]
                html += '<li>'
                html += '<a href="' + link + '" class="import">' + imp + \
                        '</a>'
                html += '</li>'
            html += '</ul>'

            html += "If you don't have them, you can install these " \
                    "packages" + \
                    ' running <a href="https://pypi.org/project/pip/">' \
                    'pip</a> :' + \
                    '<br>'

            for imp in external_imports:
                html += '<div class="code">'
                html += '$ <span class="blue">pip</span> install ' + imp + \
                        '<br>'
                html += '</div>'

        else:
            html += '<h3>Modules</h3>This project doesn\'t use any non ' + \
                    'standard Python modules.'

        html += '<h3>Learn More</h3><p>For more details, check out ' + \
                'the ' + project_name + ' repository here : <a href="' + \
                github + '">' + github + '</a>'

        html += '<h2>About the Documentation</h2><p>This website has ' \
                'been ' + \
                'automatically generated by Docapy. Docapy is a ' \
                'documentation ' + \
                'generator for Python projects. Check out the official ' + \
                'repository' + \
                'to learn more : <a href="https://github.com/Teskann/Docapy' \
                '">' + \
                'https://github.com/Teskann/Docapy</a></p></div>'
        f.write(html)
        f.close()

    # Copying CSS and font files .............................................

    from shutil import copyfile
    fdir = os.path.dirname(os.path.abspath(__file__))
    copyfile(fdir + '/style.css', './style.css')
    copyfile(fdir + '/ModernSans-Light.otf', './ModernSans-Light.otf')

    colors = {'blue': '#004bff',
              'cyan': '#03c3f5',
              'red': '#e50914',
              'green': '#00991e',
              'orange': '#ff5626',
              'purple': '#ad0fc9'}

    with open('./style.css', 'r+', encoding='utf8') as f:
        text = f.read()

        col = color if color[0] == '#' else colors[color]

        text = text.replace("#03c3f5", col)

        f.write(text)
        f.close()


# Main _______________________________________________________________________

if __name__ == "__main__":
    print("This file should not be run. To run Docapy, edit and run"
          " 'edit_and_run_me.py' instead.\nFor more details, refer to the"
          " documentation : https://teskann.github.io/docapy/")
