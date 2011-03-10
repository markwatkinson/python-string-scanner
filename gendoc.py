#!/usr/bin/env python
"""
  Very quick hackish script to generate some docs
  pydoc produces horribly unstylable output!
"""
import scanner
import inspect
import re

methods = []
getset = []


def format_doc(doc):
  if doc is None: doc = ''
  doc = inspect.cleandoc(doc)
  # slow
  regex = '|'.join( [m[0] for m in methods] + [m[0] for m in getset] )
  regex = r'(\b' + regex + r')\b'
  doc = re.sub('\r|\r\n', '\n', doc)
  
  doc = doc.replace('&', '&amp;').replace('>', '&gt;').replace('<', '&lt;')
  doc = re.sub(regex, lambda x: '<a href="#{0}">{0}</a>'.format(x.group(0)), doc)
  doc = '<pre>' + doc + '</pre>'
  return doc


for name, type_ in inspect.getmembers(scanner.Scanner):
  if name.startswith('_') and name != '__init__':
    continue
  obj = getattr(scanner.Scanner, name)
  
  if inspect.ismethod(obj):  
    argdata = inspect.getargspec(obj)
    args = argdata[0][1:]
    if argdata[1]: args += ['*' + argdata[1]]
    if argdata[3]: 
      for i, a in enumerate(argdata[3][::-1]):
        args[-i-1] += '=' + str(a)        
    methods.append( (name, args, obj.__doc__ ) )   
    
  elif inspect.isdatadescriptor(obj):
    getset.append( (name, obj.__doc__) )


print '<dl>'
print '<dt>class Scanner</dt>'
print '<h1>About</h1>'
print '<dd>'
print format_doc(scanner.Scanner.__doc__)

print '<h1>Properties</h1>'
print '<dl>'
for m, doc in getset:
  print '<dt id="{0}">{0}</dt> <dd>{1}</dd>'.format(m, format_doc(doc))
print '<h1>Methods</h1>'  
for m, args, doc in methods:
  print '<dt id="{0}">{0}({1})</dt><dd>{2}</dd>'.format(m, ', '.join(args), format_doc(doc))

print '</dl>'
print '</dd>'
print '</dl>'