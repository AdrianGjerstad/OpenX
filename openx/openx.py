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


########################################
# DISPLAY ERROR                        #
########################################

class Error:
  def __init__(self, message='', title='Error', ec=1):
    self.title = title
    self.message = message
    self.ec = ec

  def r(self):
    sys.stderr.write(f'{self.title}')

    if self.message != '':
      sys.stderr.write(f': {self.message}')

    sys.stderr.write('\n')

    sys.exit(self.ec)

########################################
# ARGUMENT DECODER                     #
########################################

OPTIONS = {
  'verbose': False,
  'certfile': None,
  'super': False
}

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
        else:
          Error('Invalid option --%s' % (arg)).r()

        continue

      # Flag Field
      if arg == 'v':
        OPTIONS['verbose'] = True
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
      data = open(os.environ['PWD'] + self.path, 'r').read()
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

  print(OPTIONS)

  httpd = OpenXServer(('127.0.0.1', 3000), OpenXHTTPRequestHandler)
  if OPTIONS['certfile'] is not None:
    httpd.socket = ssl.wrap_socket(httpd.socket, certfile=OPTIONS['certfile'], server_side=True)
  httpd.serve_forever()

  return 0

if __name__ == "__main__":
  sys.exit(main(len(sys.argv), sys.argv) or 255)
