#
#   Copyright 2016 Matt Shanker
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

import sys
import time
import importlib
import requests
from bottle import request, response, HTTPError
from os.path import abspath, dirname

projdir = dirname(abspath(__file__+'/..'))

sys.path.append(projdir)
import config

_handlers = []

def register_handler(match_fn):
    """ Add a plugin to the list of handlers queried
        for each request.
    """
    _handlers.append(match_fn)

def proxy_request():
    """ Called from a bottle request context.
        Proxies the call transparently to the graphite server.
    """
    url = config.graphite_url+request.path+'?'+request.query_string
    r = requests.get(url)
    response.status = r.status_code
    return r.content

def query_graphite(query, from_=10):
    """ Invoke query on graphite server for data
        within the last 'from_' minutes.
    """
    retries = 3
    last_e = None
    r = None
    while retries > 0:
        try:
            opts = {'format': 'json', 'target': query, 'from': '-{}minutes'.format(from_)}
            r = requests.get(config.graphite_url+'/render', params=opts)
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            print('query_graphite: Error: {}, Retries: {}'.format(e, retries))
            last_e = e
        time.sleep(1.0)
        retries -= 1

    print(r.url)
    raise HTTPError(r.status_code, r.text, last_e)

def get_handler():
    """ Calls the registered handler function for each
        registered plugin and returns the first non-None
        result or None if no handlers respond.
    """
    for fn in _handlers:
        handler = fn(request)
        if handler is not None:
            return handler
    return None

def load_plugins():
    plugin_dir = projdir+'/plugins'
    print('Loading plugins:')
    sys.path.append(plugin_dir)
    for pname in config.plugins:
        importlib.import_module(pname)
        print(' - {}'.format(pname))
    sys.path.remove(plugin_dir)
    print('Done.')
