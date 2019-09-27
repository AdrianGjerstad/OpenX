#!/usr/bin/env python3

########################################
# IMPORTS                              #
########################################

# A-Z Built-in
from http.server import BaseHTTPRequestHandler,HTTPServer
import os
import ssl
import sys

# A-Z Dev-written
import config

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
# ARGUMENT DECODER                     #
########################################

OPTIONS = {
  'verbose': False,
  'certfile': None,
  'super': False,
  'configfile': None
}

configurations = None

def arg_decode(args):
  skip_flag = 0
  for i in range(1, len(args)):
    if skip_flag > 0:
      skip_flag -= 1
      continue

    arg = args[i]

    if arg[0] == '-':
      arg = arg[1:]

      if arg[0] == '-':
        arg = arg[1:]

        if arg[0] == '-':
          Error('Invalid option --%s' % (arg)).r()

        # Option Field
        if arg == 'verbose':
          OPTIONS['verbose'] = True
        elif arg == 'certfile':
          if os.path.isfile(args[i+1]):
            OPTIONS['certfile'] = args[i+1]
            skip_flag = 1
          else:
            Error('No such file %s' % (args[i+1])).r()
        elif arg == 'config':
          OPTIONS['configfile'] = args[i+1]
          skip_flag = 1
        else:
          Error('Invalid option --%s' % (arg)).r()

        continue

      # Flag Field
      if arg == 'v':
        OPTIONS['verbose'] = True
      elif arg == 'c':
        OPTIONS['configfile'] = args[i+1]
        skip_flag = 1
      else:
        Error('Invalid flag -%s' % (arg)).r()

      continue

    # Argument Field
    if False:
      pass
    else:
      Error('Invalid argument %s' % (arg)).r()

  return

########################################
# SUPER USER                           #
########################################

try:
  os.rename('/etc/foo', '/etc/bar')
  OPTIONS['super'] = True
except IOError as e:
  pass

########################################
# OPENXHTTPREQUESTHANDLER              #
########################################

class OpenXHTTPRequestHandler(BaseHTTPRequestHandler):
  def do_GET(self):
    data = ''
    try:
      data = open(configurations['pub:'] + self.path, 'r').read()
      self.send_response(200)
    except:
      data = '404 Not Found'
      self.send_response(404)
    self.end_headers()
    self.wfile.write(bytes(data, 'utf-8'))

########################################
# OPENXSERVER                          #
########################################

class OpenXServer(HTTPServer):
  def __init__(self, address_family, handler_class):
    super().__init__(address_family, handler_class)

########################################
# MAIN                                 #
########################################

def main(argc, argv):
  arg_decode(argv)
  global configurations
  configurations = {'r':{},'t':{},'pub:':'','prt:':'8000','ipa:':'127.0.0.1'}
  if OPTIONS['configfile'] is not None:
    configurations = config.configparse(OPTIONS['configfile'][:OPTIONS['configfile'].rfind('/')], OPTIONS['configfile'][OPTIONS['configfile'].rfind('/')+1:])

  if not os.path.isdir(configurations['pub:']) or configurations['pub:'].endswith('/'):
    Error('Invalid public designation: ' + configurations['pub:'] + '\n\tIf there is one, please remove the slash from the end.').r()

  try:
    int(configurations['prt:'])
  except ValueError:
    Error('Port number given is not an integer.').r()

  if not OPTIONS['super'] and int(configurations['prt:']) < 1024:
    Error('Starting a server on port %s requires root.' % (configurations['prt:'])).r()

  tmp = configurations['ipa:'].split('.')
  if len(tmp) == 1:
    if tmp[0] == 'localhost':
      configurations['ipa:'] = '127.0.0.1'
      Error('Use of IP address \'localhost\'. Use 127.0.0.1 next time.', 'Warning', fatal=False).r()
    else:
      Error('Invalid IPv4. Length=1.').r()
  elif len(tmp) == 4:
    for i in range(4):
      try:
        if int(tmp[i]) < 0 or int(tmp[i]) > 255:
          Error('Byte overflow of IPv4 byte=' + str(i)).r()
      except:
        Error('Unknown IPv4 Address: ' + configurations['ipa:']).r()

    if OPTIONS['verbose']:
      print('Validation of IPv4 complete: ' + configurations['ipa:'])
  else:
    Error('Invalid IPv4 Length=' + str(len(tmp)))


  httpd = OpenXServer((configurations['ipa:'], int(configurations['prt:'])), OpenXHTTPRequestHandler)
  if OPTIONS['certfile'] is not None:
    httpd.socket = ssl.wrap_socket(httpd.socket, certfile=OPTIONS['certfile'], server_side=True)
  httpd.serve_forever()

  return 0

if __name__ == "__main__":
  sys.exit(main(len(sys.argv), sys.argv) or 255)
