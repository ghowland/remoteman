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


# Remote Commands we support
COMMAND = {
  'file':'Ensure a file has the proper contents, permissions',
  'directory':'Ensure a directory exists, and has the proper permissions',
}


def ProcessCommand(run_spec, command, command_options, command_args):
  """Process a command against this run_spec_path"""
  output_data = {}
  
  # Info: Information about this environment
  if command == 'info':
    output_data['options'] = command_options

  # List: List the jobs to run in this environment
  elif command == 'list':
    output_data['errors'] = []
    
    # Jobs
    #output_data['jobs'] = {}
    for (job, job_path) in run_spec['jobs'].items():
      if os.path.isfile:
        try:
          job_data = yaml.load(open(job_path))
          #output_data['jobs'][job] = {}
          #output_data['jobs'][job]['data'] = job_data['data']
          
          print 'Job: %s: %s: %s' % (job, job_data['data']['component'], job_data['data']['name'])
          
        except Exception, e:
          output_data['errors'].append('Job spec could not be loaded: %s: %s: %s' % (job, job_path, e))
          
      else:
        output_data['errors'].append('Job spec file not found: %s' % job_path)

  # Print: Print out job spec
  elif command == 'print':
    output_data['errors'] = []
    
    # Runspec
    output_data['run_spec'] = run_spec
    
    # Websource: If we have the websource (HTTP based datasource), load its data
    if 'websource' in run_spec:
      try:
        output_data['websource'] = yaml.load(open(run_spec['websource']))
        
      except Exception, e:
        output_data['errors'].append('Could not load run_spec\'s websource: %s: %s' % (run_spec['websource'], e))
    
    # Websource: missing
    else:
      output_data['errors'].append('No websource block specified in the run_spec')
    
    # Jobs
    output_data['jobs'] = {}
    for (job, job_path) in run_spec['jobs'].items():
      log('Job: %s' % job)
      if os.path.isfile:
        try:
          output_data['jobs'][job] = yaml.load(open(job_path))
          
        except Exception, e:
          output_data['errors'].append('Job spec could not be loaded: %s: %s: %s' % (job, job_path, e))
          
      else:
        output_data['errors'].append('Job spec file not found: %s' % job_path)
  
  # Run a job
  elif command == 'run':
    utility.run.Run(run_spec, command_options, command_args)
  
  # Client - Run forever processing server requests
  elif command == 'client':
    utility.client.ProcessRequestsForever(run_spec, command_options, command_args)
  
  # Unknown command
  else:
    output_data['errors'] = ['Unknown command: %s' % command]
    
  
  return output_data


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
  print
  print 'Commands:'
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

  long_options = ['help', 'verbose', 'override-host=', 'nocommit']
  
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
    result = RequestRemoteInstructions(remote_spec, command, command_options)
    
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
