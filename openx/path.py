#!/usr/bin/env python3

########################################
# IMPORTS                              #
########################################

import os
import sys

########################################
# OPTIONS                              #
########################################

FILE_OMIT_MODES = {
  'OMIT': 'OMIT',
  'SEND_TUPLE': 'SEND_TUPLE',
  'KEEP': 'KEEP'
}

PATH_OPTIONS = {
  'TRAILING_SLASH': True,
  'OMIT_FILE': FILE_OMIT_MODES['SEND_TUPLE']
}

########################################
# FIXPATH                              #
########################################

def fixpath(path):
  if path.find('/') == -1:
    if PATH_OPTIONS['OMIT_FILE'] == FILE_OMIT_MODES['SEND_TUPLE']:
      return ('', path)
    return path

  if os.path.isdir(path):
    if not path.endswith(os.path.sep) and PATH_OPTIONS['TRAILING_SLASH']:
      path += os.path.sep
    elif path.endswith(os.path.sep) and not PATH_OPTIONS['TRAILING_SLASH']:
      path = path[:-1*len(os.path.sep)]

    return path
  elif os.path.isfile(path):
    if PATH_OPTIONS['OMIT_FILE'] == FILE_OMIT_MODES['OMIT']:
      path = path[:path.rfind(os.path.sep)]
      # Path doesn't have trailing slash

      if PATH_OPTIONS['TRAILING_SLASH']:
        path += os.path.sep
    elif PATH_OPTIONS['OMIT_FILE'] == FILE_OMIT_MODES['SEND_TUPLE']:
      path = (path[:path.rfind(os.path.sep)], path[path.rfind(os.path.sep)+1:])
      # Path[0] doesn't have trailing slash

      if PATH_OPTIONS['TRAILING_SLASH']:
        path = (path[0] + '/', path[1])

  return path
