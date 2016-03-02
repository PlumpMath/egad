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

import egadlib
import config


def _strip_outer_fn(target):
    lp = target.find('(')
    rp = target.rfind(')')
    assert lp >= 0 and rp >= 0
    return target[lp+1:rp]

def _enumerate_wildcard(target):
    return [x['target'] for x in egadlib.query_graphite(target)
            if any([_[0] is not None for _ in x['datapoints']])]

def _set_target(request, new_target):
    """ Bottle request objects assume there are no repeating
        parameters. However repeating the 'target' param is
        how graphite handles multiple series in a query. This
        is a helper function to do the dirty work of replacing
        the existing target parameter in the bottle request
        with the new targets, adding repeating params as required
    """
    cur_params = request.query
    cur_params.pop('target', None)
    if not isinstance(new_target, list):
        new_target = [new_target]
    tgt_str = '&'.join(['target={}'.format(t) for t in new_target])

    new_qstr = '&'.join(['{}={}'.format(k,v) for k,v in cur_params.items()])
    new_qstr += '&{}'.format(tgt_str)
    request['QUERY_STRING'] = new_qstr

def divide_series(request):
    """ The denominator for divideSeries is required to be a
        single series. For our use-case of using wildcards the
        following steps will be taken to account for this:

          1. Resolve wildcards into list of available metrics
          2. Replace single divideSeries call with a call for
             each pair of series, grouped by app/host.
          3. Forward this request to graphite for resolution.

    """
    t = _strip_outer_fn(request.query.target)
    num_wc,den_wc = t.split(',')
    num_tgts = {}
    den_tgts = {}
    for target in _enumerate_wildcard(num_wc):
        num_tgts['.'.join(target.split('.')[:3])] = target
    for target in _enumerate_wildcard(den_wc):
        den_tgts['.'.join(target.split('.')[:3])] = target

    new_tgts = []
    for k,v in num_tgts.items():
        if k in den_tgts:
            new_tgts.append('divideSeries({},{})'.format(v, den_tgts[k]))

    _set_target(request, new_tgts)
    print(config.graphite_url+request.path+'?'+request.query_string)
    return egadlib.proxy_request()

def series_calc(request):
    if request.query.target is not None:
        if request.query.target.startswith('divideSeries('):
            return divide_series
    else:
        return None

egadlib.register_handler(series_calc)
