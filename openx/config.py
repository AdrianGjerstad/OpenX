#!/usr/bin/env python3

########################################
# IMPORTS                              #
########################################

import os
import string
import sys

import path

########################################
# DISPLAY ERROR                        #
########################################

class Error:
  def __init__(self, message='', title='Error', fatal=True, ec=1):
    self.title = title
    self.message = message
    self.ec = ec
    self.fatal = fatal

  def r(self):
    sys.stderr.write(f'{self.title}')

    if self.message != '':
      sys.stderr.write(f': {self.message}')

    sys.stderr.write('\n')

    if self.fatal:
      sys.exit(self.ec)

########################################
# CONFIGPARSE                          #
########################################

REQUIRE_VALID_DIR = [
  'pub:'
]

def configparse_a(line, result, line_num, directory):
  line = line.strip()

  try:
    line = line[:line.index('#')].strip()
  except:
    pass

  if line == '':
    return

  if line[0] in string.ascii_lowercase and line[1] in string.ascii_lowercase and line[2] in string.ascii_lowercase:
    rule_name = line[:3]
    line = line[3:].lstrip()

    if line[0] != ':':
      Error('OpenX_Config: Expected a \':\' character after three-character code on line %i' % (line_num), fatal=False).r()
      return

    line = line[1:].lstrip()

    if (rule_name + ':') in REQUIRE_VALID_DIR:
      if not line.startswith(os.path.sep):
        Error('OpenX_Config: Expected an absolute path for rule %s' % (rule_name)).r()
      if not os.path.isdir(line):
        Error('OpenX_Config: Expected a valid directory for rule %s' % (rule_name)).r()
      line = path.fixpath(line)[0]

    result[rule_name + ":"] = line

    return

  modifier = 'r'

  if line[0] in string.ascii_lowercase:
    modifier = line[0]
    line = line[1:].lstrip()

  for i in range(3):
    if line[i] not in string.digits:
      Error('OpenX_Config: Expected a three-digit code at the start of the line on line %i' % (line_num), fatal=False).r()
      return

  if line[0] not in '12345':
    Error('OpenX_Config: HTTP Response Code cannot start with %s on line %i' % (line[0], line_num), fatal=False).r()
    return

  code = int(line[:3])
  line = line[3:].lstrip()

  if line[0] != ':':
    Error('OpenX_Config: Expected a \':\' character after three-digit code on line %i' % (line_num), fatal=False).r()
    return

  line = line[1:].lstrip()

  if not line.startswith(os.path.sep):
    Error('OpenX_Config: Expected an absolute path for line %i' % (line_num)).r()
  if not os.path.isfile(result['pub:'] + line):
    Error('OpenX_Config: Expected a valid file for line %i' % (line_num)).r()
  tmp = path.fixpath(line)
  line = tmp[0] + tmp[1]

  if not os.path.isfile(result['pub:'] + line):
    Error('OpenX_Config: File on line %i is not a valid file' % (line_num), fatal=False).r()
    return

  try:
    result[modifier][str(code)].append(result['pub:'] + line)
  except KeyError:
    result[modifier][str(code)] = [result['pub:'] + line]

def configparse(directory, file, default=False):
  result = {
    'r': {},
    't': {},
    'pub:': '',
    'prt:': '8000',
    'ipa:': '127.0.0.1'
  }

  if default:
    return result

  with open(directory + os.path.sep + file, 'r') as f:
    line_num = 0
    for line in f:
      line_num += 1
      configparse_a(line, result, line_num, directory)

    else:
      # No more lines to be read from file
      return result
