#!/usr/bin/env python3
#    textplate - A LaTeX-inspired templating language for plaintext
#    Copyright © 2017  RunasSudo (Yingtong Li)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys

string_specials = str.maketrans({'\\': r'\\', "'": r"\'", '"': r'\"', '\n': r'\n'})
def escape(s):
	return s.translate(string_specials)

class Template:
	...

class TemplateParser:
	def __init__(self):
		self.code = []
	
	def parse(self, filename):
		with open(filename, 'r') as f:
			#self.code.append('import textplate')
			self.code.append('def template():') # To avoid requiring global declarations everywhere
			self.code.append("	_text = lambda x: print(x, end='')")
			self.code.append('	_commands = {}')
			self.code.append('	def command(func):')
			self.code.append('		_commands[func.__name__] = func')
			
			self.indent = 1
			
			self.line_no = 0
			
			for line in f:
				line = line[:-1] # Strip trailing newline
				self.line_no += 1
				
				if line.startswith('\t'):
					# Code
					
					if line[self.indent-1:] == 'end':
						self.indent -= 1
						continue
					
					if line[:self.indent] != ('\t' * self.indent):
						raise TemplateSyntaxError('Incorrect level of indentation at line {}'.format(self.line_no))
					
					self.code.append(line)
					
					if line.endswith(':'):
						self.indent += 1
				else:
					# Text
					
					text_iter = iter(line)
					
					while True:
						# Read until command
						char, text = self.read_until(text_iter, '\\')
						
						if char is None:
							text.append('\n')
						if len(text) > 0:
							self.code.append("{}_text('{}')".format('\t' * self.indent, escape(''.join(text))))
						if char is None:
							break
						
						# Got a command
						char, command_name = self.read_until(text_iter, '{ ')
						command_args = []
						while char == '{':
							# Read arguments
							# TODO: Account for nested structures
							# TODO: Span multiple lines
							char, arg = self.read_until(text_iter, '}')
							if char is None:
								raise TemplateSyntaxError('Unexpected EOF at line {} while reading argument'.format(self.line_no))
							command_args.append(arg)
							char = next(text_iter, None)
						
						self.code.append("{}_commands['{}']({})".format('\t' * self.indent, escape(''.join(command_name)), ', '.join(["'{}'".format(escape(''.join(arg))) for arg in command_args])))
			
			if self.indent > 1:
				raise TemplateSyntaxError('Not enough ends')
			if self.indent < 1:
				raise TemplateSyntaxError('Too few ends')
			
			self.code.append('template()')
	
	# Helper function to read characters from an iterator until a character is met
	def read_until(self, text_iter, stop_at):
		text_buf = []
		
		while True:
			try:
				char = next(text_iter)
				if char in stop_at:
					return char, text_buf
				text_buf.append(char)
			except StopIteration:
				return None, text_buf

class TemplateSyntaxError(Exception):
	pass

def main(filename):
	parser = TemplateParser()
	parser.parse(filename)
	
	print('# BEGIN CODE')
	print()
	
	for line in parser.code:
		print(line)
	
	print()
	print('# BEGIN OUTPUT')
	print()
	
	code = '\n'.join(parser.code)
	exec(code)

if __name__ == '__main__':
	main(sys.argv[1])
