import yaml
import os

from urllib.parse import urljoin

from .zenapi_basic_session import zenAPISession
from .zenapi_exceptions import handle_error_response
from .routermap import getendpoint

# TODO: Add logging

class ZenAPIClient(object):

    def __init__(self, domain=None, apikey=None):
        """
        Instantiate a new API client.
        Args:
            domain (str): Domain of the Zenoss Cloud instance
            apikey (str): API key
        """
        self.domain = domain

        # Initialize the session.
        self.session = zenAPISession()
        self._tid = 0
        # TODO: is this one used ?
        self.routermethods = {}

        # If authentication credentials are provided, pass them along to the session.
        if apikey:
            self.session.init_api_auth(apikey)

        filename = os.path.join(os.path.dirname(__file__), 'routers/allrouters.yaml')
        # TODO: check presence of file and content
        with open(filename, 'r') as routerfile:
            # print(routerfile.read())
            self.routerslist = yaml.load(routerfile, Loader=yaml.Loader)

    # Convenience method for building request URLs.
    # TODO: still needed ?
    @property
    def url(self):
        base = f'https://{self.domain}'
        return urljoin(base, '/cz0/zport/dmd/device_router')

    # Perform an API request.
    def _request(self, action, method, tid=1, **payload):
        """ This method is used internally without any check on the input, nor output"""
        """ The method build the URL and the JSON object of the body"""
        endpoint = getendpoint(action)
        # TODO: disabled_saml => ?saml=0 ???
        url = urljoin(f'https://{self.domain}', f'/cz0/zport{endpoint}')
        body = {
            'action': action,
            'method': method,
            'tid': tid,
        }
        if len(payload) == 1 and "override" in payload:
            # override method
            body.update(payload['override'])
        else:
            # preferred method
            body['data'] = [payload]

        '''
                r = self.requestSession.post(self._url,
                                             verify=self.config['ssl_verify'],
                                             timeout=self.config['timeout'],
                                             headers={'content-type': 'application/json',
                                                      'z-api-key': self.config['apikey']},
                                             data=json.dumps(apiBody),
                                             )
        '''

        # Ask the session to perform a JSON-RPC request with the parameters provided.
        # TODO: try...except
        # TODO: make timeout a variable
        # TODO: post method ?
        response = self.session.request('POST', url, verify=True, timeout=30, json=body)

        # TODO: Should probably just return the response
        # If something goes wrong, we'll pass the response off to the error-handling code
        if response.status_code >= 400:
            handle_error_response(response)

        # TODO: Test if output is really a JSON
        # TODO: return result of full response
        # Otherwise return the result dictionary.
        return response
        # return resp.json()['result']

    # API basic methods
    def query(self, action, method, **payload):
        # TODO: create exception class
        # Check whether router is available
        if action not in self.routerslist:
            raise Exception(
                f'Router {action} does not exist'
            )
        # Check whether the router method is available
        if action not in self.routermethods:
            # TODO: list actions / routers ?
            self.listmethods(action)
            # TODO: check again action after fetching ? Maybe not
        if method not in self.routermethods[action]:
            raise Exception(
                f'Specified router method {method} is not an option. Available methods for {action} router are: '
                f'{self.routermethods[action]}'
                )

        # Increase the transaction ID
        self._tid += 1

        # TODO : try ... except
        response = self._request(action, method, payload=payload, tid=self._tid)

        return self._validateresponse(response)

    def query_generate(self, action, method, **payload):
        '''
        Returns an iterative, generator type object of API call results.
        Queries that return a large # of results (>50, default) will be broken
        up entries. Note not all API router method calls support splitting up
        large results into manageable chunks (e.g. getDevices vs. getTriggers)
        '''
        '''
        start: integer - (optional) Offset to return the results from; used in
        pagination (default: 0)
        limit: integer - (optional) Number of items to return; used in pagination
        (default: 50)
        '''

        # Default values if not found in payload
        resultscounttotal = 1
        resultscountoffset = 0
        # TODO: default value of 100
        resultscountlimit = 50
        if 'start' in payload:
            resultscountoffset = payload['start']
        if 'limit' in payload:
            resultscountlimit = payload['limit']

        while resultscountoffset < resultscounttotal:
            response = self.query(action, method, **payload)
            # TODO: With validate, make sure that there is a result
            if 'totalCount' in response['result']:
                resultscounttotal = response['result']['totalCount']
            elif 'total' in response['result']:
                resultscounttotal = response['result']['total']
            else:
                resultscounttotal = -1

            # TODO: test if >= -1 ?
            if resultscounttotal != -1:
                if 'start' in payload:
                    resultscountoffset = payload['start'] + resultscountlimit
                    payload['start'] += resultscountlimit
                else:
                    resultscountoffset = resultscountlimit
                    payload['start'] = resultscountlimit
            yield response

    def listmethods(self, router_name):
        filename = os.path.join(os.path.dirname(__file__), f'routers/{router_name}.yaml')
        with open(filename, 'r') as f:
            data = yaml.load(f, Loader=yaml.Loader)
        self.routermethods[router_name] = data.keys()

    @staticmethod
    def _validateresponse(response):
        if response.status_code != 200:
            return {'result': {'success': False}}
        else:
            if 'Content-Type' in response.headers:
                if 'application/json' in response.headers['Content-Type']:
                    return response.json()
                elif 'test/html' in response.headers['Content-Type']:
                    # TODO: retrieve info (title) from HTML response
                    msg = 'HTML response from API call.'
                    return {'result': {'success': False}, 'msg': msg}
                else:
                    msg = f"Unknown 'Content-Type' response header returned: '{r.headers['Content-Type']}'"
                    return {'result': {'success': False}, 'msg': msg}
            else:
                msg = "Missing 'Content-Type' in API response's header"
                return {'result': {'success': False}, 'msg': msg}
