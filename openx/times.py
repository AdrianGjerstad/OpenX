#!/usr/bin/env python3

########################################
# IMPORTS                              #
########################################

from datetime import datetime

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
    sys.stderr.write(self.title)

    if self.message != '':
      sys.stderr.write(': %s' % (self.message))

    sys.stderr.write('\n')

    if self.fatal:
      sys.exit(self.ec)

########################################
# TIMESTAMP                            #
########################################

def timestamp():
  return datetime.utcnow().isoformat()

