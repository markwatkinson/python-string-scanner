#!/usr/bin/env python

import re
import os
import sys
sys.path.append(os.path.join(os.getcwd(), '..' ))
from scanner import Scanner

class JavaScriptScanner(Scanner):
  """ Simple JavaScript tokenizer using the Scanner class"""
  
  def iskeyword(self, word):
    keywords = [
      'break',
      'case',
      'catch',
      'continue',
      'debugger',
      'default',
      'delete',
      'do',
      'else',
      'finally',
      'for',
      'function',
      'if',
      'in',
      'instanceof',
      'new',
      'return',
      'switch',
      'this',
      'throw',
      'try',
      'typeof',
      'var',
      'void',
      'while',
      'with'
    ]
    return word in keywords
  
  
  def main(self):
    
    tokens = []
    
    while not self.eos():
      """ Scanning is pretty simple in theory: we iterate over the string and
      say 'does this match here?... well how about this? ... ' etc
      
      It pays to do string based checks (isspace, isalpha, etc) before running
      regex methods (scan, check, skip), if possible
      """
      index = self.pos
      c = self.peek()
      tok = None
      
      # whitespace
      if c.isspace() and self.scan(r'\s+'): tok = 'WS'
      # identifiers, including OO x.y notation
      elif (c.isalpha() or c == '_' or c == '$') and self.scan(r'[a-zA-Z_$]+\w*(?:\s*\.\s*[a-zA-Z_$]+\w*)*'):
        # Let's figure out OO notation here.
        m = self.match().split('.')
        for i, t in enumerate(m):
          if i == len(m)-1:
            tok = 'PROPERTY' if i else 'IDENT'
            if not i and self.iskeyword(t): tok = 'KEYWORD'
            tokens += [(tok, t)]
          else:
            tokens += [('OBJECT', t)]
            tokens += [('OP', '.')]        
        # we've done everything, so skip on to the next index now.
        continue
      elif (c.isdigit() or c == '.') and self.check(r'\.?\d'):
        if self.scan('0x[A-Fa-f0-9]+'): pass  # hex
        elif self.scan('0\d*'): pass    # octal
        elif self.scan('(?:\.?\d+|\d+(?:\.\d+)?)(?:[eE][+-]?\d+)?'): pass # real
        else: assert(0) # missed a numeric format
        tok = 'NUMERIC'
      elif c == '"' or c == "'":
        tok = 'STR'
        assert self.scan(r'{0} (?: [^{0}\\]+ | \\.)* (?: {0}|$)'.format(c), re.X|re.S)
      elif c == ']' or c == '}' or c == ')':
        tok = 'CLOSE_BRACKET'
        self.get()
      elif c == '[' or c == '{' or c == '(':
        tok = 'OPEN_BRACKET'
        self.get()
      elif c == ';': 
        tok = 'SEMI'
        self.get()
      elif c == '/' and self.scan(r'/\* .*? \*/', re.X|re.S) or self.scan(r'//.*'):
        tok = 'COMMENT'
      elif c == '/':
        # a slash represents either a division or a regex.
        for t, s in tokens[::-1]:          
          if t in ('WS', 'COMMENT'): continue
          # operator position, cannot be a regex, must be division
          elif t in ('CLOSE_BRACKET', 'NUMERIC', 'IDENT', 'KEYWORD'): 
            tok = 'OP'
            self.get()
            break
          else:
            assert self.scan(r'/ (?: [^/\\]+ | \\.)* (?:/[ioxm]*|$)', re.X|re.S)
            tok = 'REGEX'
          break
    
      if not tok and self.scan(r'[<>=!+*/%\-&^|~\.,:?]+'):
        tok = 'OP'
        
      if not tok: 
        tok = 'UNKNOWN'
        self.get()
        
      assert(index < self.pos)
      tokens += [(tok, self.string[index:self.pos])]
      
    return tokens
    
    
    
if __name__ == '__main__':
  f = open('input/jquery-1.4.4.js')
  s = f.read()
  f.close()
  
  scanner = JavaScriptScanner(s)
  out = scanner.main()

  s_ = ''
  for t, s in out:
    s_ +=  '{0}:'.format(t).ljust(20, ' ') + '\t[{0}]\n'.format(s)
    
  f = open('output/jsscanner_out', 'w')
  f.write(s_)
  f.close()
  print ('wrote output to output/jsscanner_out')
