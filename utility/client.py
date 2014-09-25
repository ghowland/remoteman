"""
RemoteMan Client: Poll the RPC server for what we need to ensure exists on this system
"""


import yaml
import urllib2
import urllib
import base64
import json
import hashlib
import time
import signal
import sys

from log import log
from error import Error

import run
import platform


class RPCException(Exception):
  """We failed to get the RPC server data."""


def RequestRemoteInstructions(remote_spec, command_options):
  """Request a set of remote instructions from our RPC server."""
  output_data = {}
  
  format_data = {'hostname': platform.GetHostname(command_options)}
  
  # Inspect remote_spec, fail with message if it is not formatted properly
  if type(remote_spec) != dict:
    Error('The remote spec file given is not in the proper YAML format.  Please review the documentation and update this file.  It should be a Dictionary/Associative Array/Map at the top level, containing a key for "server" with a Dictionary of keys "url", and "commands" with a Dictionary of the various remote commands.')
  
  # No server section
  if 'server' not in remote_spec:
    Error('The remote spec file given does not have a "server" key in it.  Please refer to the documentation and update this file.')
  
  # No server: url section
  if 'url' not in remote_spec['server']:
    Error('The remote spec file given does not have a "url" key in the the "server" section.  Please refer to the documentation and update this file.')
  
  
  # Update the remote spec, using format data
  remote_spec['server']['url'] = remote_spec['server']['url'] % format_data
  
  # Our instructions
  server_result = WebGet(remote_spec['server'])
  
  remote_instructions = json.loads(server_result)
  
  print 'TEST %s' % remote_instructions
  
  return output_data


def WebGet(websource, args=None):
  """Wrap dealing with web requests.  The job server uses this to avoid giving out database credentials to all machines."""
  #log('WebGet: %s' % websource)
  #try:
  if 1:
    http_request = urllib2.Request(websource['url'])
    
    # If Authorization
    if websource.get('username', None):
      auth = base64.standard_b64encode('%s:%s' % (websource['username'], websource['password'])).replace('\n', '')
      http_request.add_header("Authorization", "Basic %s" % auth)
    
    
    # If args (POST)
    if args:
      http_request.add_data(urllib.urlencode(args))
    
    
    result = urllib2.urlopen(http_request)
    data = result.read()
    
    return data

  #except Exception, e:
  #  raise RPCException('WebGet error: %s' % (e))



