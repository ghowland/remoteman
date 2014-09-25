#!/usr/bin/python
"""
RemoteMan - Remote management of dynamic files, directories and other recurring post-system install

Copyright Geoff Howland, 2014.  MIT License.

TODO:
  - ...
  -
"""


import sys
import os
import getopt
import yaml
import json
import pprint


import utility
from utility.log import log


# Output formats we support
OUTPUT_FORMATS = ['json', 'yaml', 'pprint']

# Built-In Remote Commands we support
COMMANDS = {
  'file':'Ensure a file has the proper contents, permissions (default)',
  'directory':'Ensure a directory exists, and has the proper permissions (default)',
}


def FormatAndOuput(result, command_options):
  """Format the output and return it"""
  # PPrint
  if command_options['format'] == 'pprint':
    pprint.pprint(result)
  
  # YAML
  elif command_options['format'] == 'yaml':
    print yaml.dump(result)
  
  # JSON
  elif command_options['format'] == 'json':
    print json.dumps(result)
  
  else:
    raise Exception('Unknown output format "%s", result as text: %s' % (command_options['format'], result))


def Usage(error=None):
  """Print usage information, any errors, and exit.

  If errors, exit code = 1, otherwise 0.
  """
  if error:
    print '\nerror: %s' % error
    exit_code = 1
  else:
    exit_code = 0
  
  print
  print 'usage: %s [options] <remote_spec.yaml>' % os.path.basename(sys.argv[0])
  print
  print 'example usage: "python %s ./data/remote_spec.yaml"' % os.path.basename(sys.argv[0])
  print
  print
  print 'Options:'
  print
  print '  -h, -?, --help              This usage information'
  print '  -v, --verbose               Verbose output'
  print '  -n, --nocommit              Do not commit any changes, just test them'
  print '  --override-host <hostname>  Hostname to run jobs as.  Allows testing different hosts.'
  print '  --handler-directory <path>  Hostname to run jobs as.  Allows testing different hosts.'
  print '  -f, --format <format>       Format output, types: %s' % ', '.join(OUTPUT_FORMATS)
  print
  print 'Remote Instructions Configured:'
  print
  command_keys = list(COMMANDS.keys())
  command_keys.sort()
  for command in command_keys:
    print '  %-23s %s' % (command, COMMANDS[command])
  print
  
  sys.exit(exit_code)


def Main(args=None):
  if not args:
    args = []

  long_options = ['help', 'verbose', 'override-host=', 'nocommit', 'handler-directory=']
  
  try:
    (options, args) = getopt.getopt(args, '?hvn', long_options)
  except getopt.GetoptError, e:
    Usage(e)
  
  # Dictionary of command options, with defaults
  command_options = {}
  command_options['platform'] = utility.platform.GetPlatform()
  command_options['verbose'] = False
  command_options['no_commit'] = False
  command_options['override_host'] = None
  command_options['handler_directory'] = None
  command_options['format'] = 'pprint'
  
  
  # Process out CLI options
  for (option, value) in options:
    # Help
    if option in ('-h', '-?', '--help'):
      Usage()
    
    # Verbose output information
    elif option in ('-v', '--verbose'):
      command_options['verbose'] = True
    
    # Noninteractive.  Doesnt use STDIN to gather any missing data.
    elif option in ('-n', '--nocommit'):
      command_options['no_commit'] = True
    
    # Overrride: Host name for running jobs
    elif option == '--override-host':
      command_options['override_host'] = value
    
    # Overrride: Specify a directory for finding handlers.
    #NOTE(g): Will check this directory first, and then check the "base" directory
    #   (where the remoteman.py file resides) for the path for default handlers.
    elif option == '--handler-directory':
      command_options['handler_directory'] = value
    
    # Format output
    elif option in ('-f', '--format'):
      if value not in (OUTPUT_FORMATS):
        Usage('Unsupported output format "%s", supported formats: %s' % (value, ', '.join(OUTPUT_FORMATS)))
      
      command_options['format'] = value
    
    # Invalid option
    else:
      Usage('Unknown option: %s' % option)
  
  
  # Store the command options for our logging
  utility.log.RUN_OPTIONS = command_options
  
  
  # Ensure we at least have a spec file, it's required
  if len(args) < 1:
    Usage('No remote spec specified')
  
  # Get the command
  remote_spec_path = args[0]
  
  if not os.path.isfile(remote_spec_path):
    Usage('Remote spec file does not exist: %s' % remote_spec_path)
  
  try:
    remote_spec = yaml.load(open(remote_spec_path))
  
  except Exception, e:
    Usage('Failed to load remote_spec: %s: %s' % (remote_spec_path, e))
    
  
  # Request the Remote Instructions for this machine
  if 1:
  #try:
    # Process the command and retrieve a result
    result = utility.client.RequestRemoteInstructions(remote_spec, command_options)
    
    # Format and output the result (pprint/json/yaml to stdout/file)
    FormatAndOuput(result, command_options)
  
  #NOTE(g): Catch all exceptions, and return in properly formatted output
  #TODO(g): Implement stack trace in Exception handling so we dont lose where this
  #   exception came from, and can then wrap all runs and still get useful
  #   debugging information
  #except Exception, e:
  else:
    utility.error.Error({'exception':str(e)}, command_options)


if __name__ == '__main__':
  #NOTE(g): Fixing the path here.  If you're calling this as a module, you have to 
  #   fix the utility/handlers module import problem yourself.
  sys.path.append(os.path.dirname(sys.argv[0]))

  Main(sys.argv[1:])
