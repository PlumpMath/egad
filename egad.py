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

from argparse import ArgumentParser
from bottle import request, route, run

import egadlib


@route('/render')
def render():
    handler = egadlib.get_handler()
    if handler is not None:
        return handler(request)
    else:
        return default_route(None)

@route('<_:path>')
def default_route(_):
    return egadlib.proxy_request()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-c', '--config', dest='cfgfile', default='/etc/egad.cfg', help='Path to config file. Default: /etc/egad.cfg')
    parser.add_argument('-p', '--port', dest='port', default=8080, type=int, help='Port number to listen on. Default: 8080')
    args = parser.parse_args()

    egadlib.load_config(args.cfgfile)
    egadlib.load_plugins()
    print('\nStarting web server\n')
    run(host='0.0.0.0', port=args.port, debug=True)
