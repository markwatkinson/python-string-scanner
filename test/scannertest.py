#!/usr/bin/env python


import re
import os
import sys
sys.path.append(os.path.join(os.getcwd(), '..' ))
from scanner import Scanner

class ScannerTest(Scanner):
  
  def assert_exception(self, method, e, args=None):
    if args is None:
      args = tuple()
    try: 
      method(*args)
    except e: return True
    return False
    
  
  def main(self):
    
    # run with nothing
    exception_thrown = False
    try: self.scan('\s+')
    except: exception_thrown = True
    assert exception_thrown
    
    
    s = 'This is a test string'
    self.string = s
    assert self.string == s
    assert self.bol()
    assert self.scan('\w+') == 'This'
    assert self.match() == 'This'
    assert self.match_len() == 4
    assert self.rest() == ' is a test string'
    assert not self.scan('\w+') 
    
    assert self.scan('\s+')
    assert self.match() == ' '
    assert self.match_pos() == 4
    assert self.match_len() == 1
    assert self.pre_match() == 'This', self.pre_match()
    assert self.rest() == 'is a test string'
    assert self.post_match() == 'is a test string'
    pos = self.pos
    
    # Check doesn't move us along but it does record matches
    assert self.check('\w+')
    assert self.match() == 'is'
    assert self.match_pos() == 5
    assert self.match_len() == 2
    assert self.pre_match() == 'This ', self.pre_match()
    assert self.rest() == 'is a test string'
    assert self.post_match() == ' a test string'
    assert self.pos == pos
    
    assert self.skip('\w+') == 2
    assert self.match() == 'is'
    assert self.match_pos() == 5
    assert self.match_len() == 2
    assert self.pre_match() == 'This ', self.pre_match()
    assert self.rest() == ' a test string'
    assert self.post_match() == ' a test string'
    assert self.pos == pos+2
    
    pos += 2
    
    assert self.peek() == ' '
    assert self.peek(2) == ' a'
    assert self.get() == ' '
    assert self.get(2) == 'a '
    assert self.rest() == 'test string'
    
    # matches shouldn't have changed
    assert self.match() == 'is'
    assert self.match_pos() == 5
    assert self.match_len() == 2
    assert self.pre_match() == 'This '
    assert self.post_match() == ' a test string'
    
    # consumed 3 with get
    assert self.pos == pos + 3
    pos+=3
    
    self.reset()
    assert self.rest() == 'This is a test string', self.rest()
    assert self.scan('\w') == 'T'
    assert self.scan_until('\d') is None
    assert not self.matched() 
    
    assert self.rest() == 'his is a test string'
    self.unscan()
    self.unscan()    
    assert self.rest() == 'This is a test string'
    
    assert self.check_until(r'(?<=\s)is') == 'This is'
    assert self.match() == 'This is'
    assert self.pre_match() == '', self.pre_match()
    assert self.post_match() == ' a test string'
    # but we haven't actually moved...
    assert self.pos == 0
    assert self.rest() == 'This is a test string'
    
    
    assert self.scan_until(r'\sa\s') == 'This is a '
    assert self.match() == 'This is a '
    assert self.pre_match() == ''
    assert self.post_match() == 'test string'
    assert self.pos == 10
    assert self.rest() == 'test string'
    
    assert self.skip_until('st') == 4
    
    assert self.pos == 14

    
    assert not self.eos()
    self.terminate()
    assert self.eos()
    
    
    self.reset()
    assert self.scan('(Th)(is)')
    assert self.match_groups() == ('Th', 'is'), self.match_groups()
    assert self.match_groupdict() == {} # no named arguments
    assert self.match_group() == 'This'
    assert self.match_group(1) == 'Th'
    assert self.match_group(2) == 'is'
    
    self.unscan()
    # second group won't match
    assert self.scan('(th)(e)?', re.I)
    assert self.match_groups() == ('Th', None)
    # default value
    assert self.match_groups('123') == ('Th', '123')
    
    self.unscan()
    
    self.scan('(?P<leading>\w+)(?P<whitespace>\s+)(?P<nomatch>\d+)?')
    assert self.match_groups() == ('This', ' ', None)
    assert self.match_group(0) == 'This '
    
    assert self.match_group(1) == 'This'
    assert self.match_group('leading') == 'This'    
    assert self.match_group(2) == ' '
    assert self.match_group('whitespace') == ' '    
    assert self.match_group(3) == None
    assert self.match_group('nomatch') == None
    
    assert self.assert_exception(self.match_group, IndexError, (5,))
    
    
    assert self.match_groupdict() == {'leading': 'This', 'whitespace': ' ',
      'nomatch' : None}
    assert self.match_groupdict(False) == {'leading': 'This', 'whitespace': ' ',
      'nomatch' : False}

    
    self.reset()
    assert self.scan('T') and self.matched() == True
    assert not self.scan('T') and self.matched() == False
    
    assert self.assert_exception(self.match, Exception)
    assert self.assert_exception(self.match_len, Exception)
    assert self.assert_exception(self.match_pos, Exception)
    assert self.assert_exception(self.match_info, Exception)
    assert self.assert_exception(self.match_groups, Exception)
    assert self.assert_exception(self.match_groupdict, Exception)
    assert self.assert_exception(self.match_group, Exception)
    assert self.assert_exception(self.pre_match, Exception)
    assert self.assert_exception(self.post_match, Exception)


    self.reset()
    
    assert self.assert_exception(self.match, Exception)
    assert self.assert_exception(self.match_len, Exception)
    assert self.assert_exception(self.match_pos, Exception)
    assert self.assert_exception(self.match_info, Exception)
    assert self.assert_exception(self.match_groups, Exception)
    assert self.assert_exception(self.match_groupdict, Exception)
    assert self.assert_exception(self.match_group, Exception)
    assert self.assert_exception(self.pre_match, Exception)
    assert self.assert_exception(self.post_match, Exception)
    
    assert self.scan('A?') == ''
    assert self.matched()
    assert self.match_len() == 0
    assert self.match_pos() == 0
    assert self.pre_match() == ''
    assert self.post_match() == 'This is a test string'
    
    
    self.string = '''line1
line2
line3'''
    assert self.bol()
    assert self.scan('line1')
    assert not self.bol()
    assert self.get() == '\n'
    assert self.bol()
    assert self.scan_until('\d.', re.S) == 'line2\n'    
    assert self.bol()
    assert self.scan_until('\d') == 'line3'
    assert not self.bol()
    assert not self.peek()
    assert not self.get()    
    assert self.eos()
    
    self.string = '''line1

line3
line4
line5          \t

line7
line8
line9
line10'''
    assert self.bol()
    assert self.skip_lines() == 1
    assert self.pos == 6
    assert self.bol()    
    assert self.skip_lines() == 1
    assert self.pos == 7
    assert self.bol()
    assert not self.eol()
    # we're at the start of line 3
    assert self.skip_bytes(1) == 1
    assert self.skip_bytes(2) == 2
    assert not self.bol()
    assert self.check('e3')
    assert self.skip_lines(2) == 2
    assert self.peek(5) == 'line5'
    assert self.skip_whitespace() == 0
    assert self.skip_bytes(5) == 5
    assert self.skip_whitespace(2) == 2
    assert self.skip_whitespace(multiline=False) == 9
    assert self.check('$', re.M) is not None
    assert self.eol()
    assert self.skip_whitespace() == 2
    assert self.check('line7')
    
    assert self.scan( re.compile('line\d') ) == 'line7'
    assert self.eol()
    assert self.assert_exception(self.scan, ValueError, (12,))
    assert self.skip_lines(100) == 3
    assert self.bol()
    assert self.peek(6) == 'line10'
    assert self.skip_lines() == 0
    
    self.reset()
    self.string = '0123456789'
    assert self.scan_to('3') == '012'
    assert self.matched()
    assert self.match() == '012'
    assert self.pos == 3
    assert self.skip_to('5') == 2    
    # match shouldn't change with skip
    assert self.match() == '012'
    assert self.pos == 5
    assert self.check_to('7') == '56'
    assert self.pos == 5
    
    self.reset()
    self.string = '''line1
line2
line3
line4
line5
line6
line7
line8'''

    assert self.location() == (1, 1)
    self.get()
    assert self.location() == (1, 2)
    self.get(2)
    assert self.location() == (1, 4)    
    assert self.skip_lines()
    assert self.location() == (2, 1), self.location()
    
    self.skip_lines(3)
    assert self.location() == (5, 1)
    
    # get something in the match history
    self.scan('.')    
    pos = self.pos    
    matched = (self.matched(), self.match_pos())
    
    assert self.exists('line7')
    assert self.pos == pos    
    assert not self.exists('line70')
    assert matched ==  (self.matched(), self.match_pos())
    
    
    

s = ScannerTest()
s.main()