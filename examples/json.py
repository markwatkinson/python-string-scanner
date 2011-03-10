#!/usr/bin/env python

import re
import os
import sys
sys.path.append(os.path.join(os.getcwd(), '..' ))

from scanner import Scanner

class JSONScanner(Scanner):
  """ Very simple recursive descent JSON parser using the Scanner class.  
  This is not a thoroughly useful JSON parser as (obviously, Python already
  provides one anyway, but also) it's very error intolerant and doesn't 
  provide useful hints/recovery to obvious error cases (like invalid escape
  sequences or using single quotes as a string delimiter).
  
  Instead, it's just provided as a non-trivial demonstration of the Scanner 
  class.
  """
  
  def byte_to_line_char_no(self, byte):
    substr = self.string[:byte]
    line_endings = '\r\n' if substr.count('\r\n') else \
      '\n' if substr.count('\n') else '\r'    
    lines = substr.count(line_endings) + 1
    char = byte - substr.rfind(line_endings) if lines else byte
    return (lines, char)    
  
  def error(self, message):
    line, char = self.byte_to_line_char_no(self.pos)    
    raise ValueError('JSON: Error at {0}:{1} - {2}'.format(line, char, message))
  
  def error_if_fail(self, message):
    if not self.matched(): 
      self.error(message)
      
  def consume_ident(self):
    assert self.scan('\w+')
    if self.match() not in ('true', 'false', 'null'):    
      self.error('Invalid identifier {0}'.format(self.match()))
    return self.match()

  def __consume_string_callback(self, matchobj):
    m = matchobj.group(0)
    c = m[1]
    if c in ('"', '\\', '/'): return c
    elif c == 'b': return '\b'
    elif c == 'f': return '\f'
    elif c == 'n': return '\n'
    elif c == 'r': return '\r'
    elif c == 't': return '\t'
    elif c == 'u': return unichr(int(m[2:], 16))
    else: assert 0
    
  def consume_string(self):
    self.scan(r'" ((?: [^"\\]+ | \\(?: ["\\/bfnrt] | u[a-fA-F0-9]{4}) )*) "', re.X)
    self.error_if_fail('Invalid string (Missing terminator or invalid escape sequence?)')
    return re.sub(r'\\(u[a-fA-F0-9]{4}|.)', self.__consume_string_callback, self.match_group(1))
    
  def consume_num(self):
    self.scan(r'(?: -)?(?: 0|\d+ )(?P<point>\.\d+)?(?P<exp>[eE][+\-]?\d+)?', re.X)
    self.error_if_fail('Invalid numeric type')
    if self.match_group('point') is not None or self.match_group('exp') is not None:
      return float(self.match())
    return int(self.match())
    
  def consume_array(self):
    assert self.get() == '['
    a = []
    while True:
      self.skip_whitespace()
      a.append(self.main())
      self.skip_whitespace()
      c = self.get() 
      if c == ']': break
      elif c == ',': 
        if self.scan(r'\s*\]'): break # allow a trailing comma, else a comma
        # is simply a pass
      elif not c: self.error('Unexpected end of stream')
      else: self.error('Unexpected token {0}'.format(c))
    return a
        
  def consume_object(self):
    assert self.get() == '{'
    obj = {}
    while True:
      self.skip_whitespace()
      c = self.peek()
      if not c: 
        self.error('Unexpected end of stream')
        break
      elif c == '}': 
        self.get()
        break
      else:
        # consume key and value here
        if c != '"': self.error('Object keys should be valid strings')
        key = self.consume_string()
        if not self.scan(r'(\s*):(\s*)'): self.error('Expected ":"')
        value = self.main()
        obj[key] = value
        self.skip_whitespace()
        # consume a comma or check to see the next char is a closing brace
        # the latter will be consumed later, but we need it to be one or the 
        # other
        if self.scan(',|(?=})') is None: 
          self.error('Unexpected token {0}'.format(self.peek()))    
    return obj
  
  def main(self):
    # top level function
    self.skip_whitespace()
    c = self.peek()
    if not c: self.error('Unexpected end of stream')
    elif c == '"': return self.consume_string()
    elif c == '[': return self.consume_array()
    elif c == '{': return self.consume_object()
    elif c.isdigit(): return self.consume_num()
    elif c.isalpha(): return self.consume_ident()
    else: self.error('Unexpected symbol {0}'.format(c))
    
    
    
if __name__ == '__main__':
  f = open('input/json')
  json = f.read()
  f.close()
  json_scanner = JSONScanner(json)
  out = json_scanner.main()
  print (out)
  
    
    
  