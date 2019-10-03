#!/usr/bin/env python3

########################################
# IMPORTS                              #
########################################

# A-Z Built-in
from http.server import BaseHTTPRequestHandler,HTTPServer
import multiprocessing
import os
import platform
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
    sys.stderr.write(self.title)

    if self.message != '':
      sys.stderr.write(': %s' % (self.message))

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
  def send_httpstatus(self, code, default):
    global configurations
    r_data_list = configurations['r'].get(str(code), [])
    if len(r_data_list) >= 1:
      return open(r_data_list[0], 'r')
    return open(default, 'r')

  def get_trigger(self, file):
    global configurations
    t_data_list = configurations['t']

    for e in t_data_list:
      code_data_list = t_data_list[e]

      for e_ in range(len(code_data_list)):
        if code_data_list[e_] == configurations['pub:'][:-1] + file:
          return e

    return None

  def do_GET(self):
    data = None
    code = 100

    if self.path.endswith('/'):
      self.path += 'index.html'
    
    trigger_code = self.get_trigger(self.path)

    if trigger_code is not None:
      code = int(trigger_code)
      try:
        data = self.send_httpstatus(code, (os.environ['OPENXPATH'] + 'defaults/403.html'))
      except FileNotFoundError:
        data = self.send_httpstatus(404, (os.environ['OPENXPATH'] + 'defaults/404.html'))
        code = 404
    else:
      try:
        data = self.send_httpstatus(200, (configurations['pub:'][:-1*len(os.path.sep)] + self.path))
        code = 200
      except FileNotFoundError:
        data = self.send_httpstatus(404, (os.environ['OPENXPATH'] + 'defaults/404.html'))
        code = 404

    self.send_response(code)

    self._headers_buffer.pop(1)
    self.send_header('Server', 'OpenX/0.1 Python/' + str(sys.version_info[0]) + '.' + str(sys.version_info[1]) + '.' + str(sys.version_info[2]) + ' (' + platform.system() + ')')

    if data.name.endswith('.html'):
      self.send_header('Content-Type', 'text/html')

    self.send_header('Content-Length', str(os.path.getsize(data.name)))

    # print(self._headers_buffer)

    self.end_headers()

    self.wfile.write(bytes(data.read(), 'utf-8'))

  def log_message(self, format, *args):
    sys.stderr.write("%s [%s] %s\n" %
                     (self.address_string(),
                      self.log_date_time_string(),
                      format%args))

########################################
# OPENXSERVER                          #
########################################

class OpenXServer(HTTPServer):
  def __init__(self, address_family, handler_class):
    super().__init__(address_family, handler_class)

httpd = None

def server_spawner():
  global httpd
  global configurations
  try:
    print('Serving HTTP%s at address %s:%s ...' % ('S' if OPTIONS['certfile'] is not None else '', configurations['ipa:'], configurations['prt:']))
    httpd.serve_forever()
  except KeyboardInterrupt:
    httpd.shutdown()

########################################
# MAIN                                 #
########################################

def main(argc, argv):
  arg_decode(argv)
  global configurations
  if OPTIONS['configfile'] is not None:
    configurations = config.configparse(OPTIONS['configfile'][:OPTIONS['configfile'].rfind('/')], OPTIONS['configfile'][OPTIONS['configfile'].rfind('/')+1:])
  else:
    configurations = config.configparse(default=True)
  
  try:
    int(configurations['prt:'])
  except ValueError:
    Error('Port number given is not an integer.').r()

  if not OPTIONS['super'] and int(configurations['prt:']) < 1024:
    Error('Starting a server on port %s requires root.' % (configurations['prt:'])).r()

  if int(configurations['prt:']) > 65535:
    Error('Port integer (16-bit) overflow error: %s' % (configurations['prt:'])).r()

  if OPTIONS['verbose']:
    print('Validation of Port number complete: %s' % (configurations['prt:']))

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
  
  global httpd
  httpd = OpenXServer((configurations['ipa:'], int(configurations['prt:'])), OpenXHTTPRequestHandler)
  if OPTIONS['certfile'] is not None:
    httpd.socket = ssl.wrap_socket(httpd.socket, certfile=OPTIONS['certfile'], server_side=True)
  
  server_proc = multiprocessing.Process(target=server_spawner)
  server_proc.start()

  try:
    server_proc.join()
  except KeyboardInterrupt:
    server_proc.terminate()
    server_proc.join()
    print('\033[G\033[KShutdown server ...')
    print('Server shutdown successfully.')

  return 0

if __name__ == "__main__":
  sys.exit(main(len(sys.argv), sys.argv) or 255)
