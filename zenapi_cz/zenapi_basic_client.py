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
    @property
    def url(self):
        base = f'https://{self.domain}'
        return urljoin(base, '/cz0/zport/dmd/device_router')

    # Perform an API request.
    def _request(self, action, method, tid=1, **payload):
        endpoint = getendpoint(action)
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
        resp = self.session.request('POST', url, json=body)

        # If something goes wrong, we'll pass the response off to the error-handling code
        if resp.status_code >= 400:
            handle_error_response(resp)

        # TODO: Test if output is really a JSON
        # TODO: return result of full response
        # Otherwise return the result dictionary.
        return resp.json()
        # return resp.json()['result']

    # API basic methods
    # TODO: data should become **
    def query(self, action, method, **payload):
        # TODO: create exception class
        if action not in self.routerslist:
            raise Exception(
                f'Router {action} does not exist'
            )
        if action not in self.routermethods:
            self.listmethods(action)
        if method not in self.routermethods[action]:
            raise Exception(
                f'Specified router method {method} is not an option. Available methods for {action} router are: '
                f'{self.routermethods[action]}'
                )
        self._tid += 1

        # TODO : try ... except
        response = self._request(action, method, payload=payload, tid=self._tid)

        '''
                except Exception as e:
            msg = 'Reqests exception: %s' % e
            self.log.error(msg)
            rJson = {'result': {'success': False}, 'msg': msg}
            apiResultsTotal = -1
            return rJson
        '''

        return response

    def listmethods(self, router_name):
        print(router_name)
        filename = os.path.join(os.path.dirname(__file__), f'routers/{router_name}.yaml')
        with open(filename, 'r') as f:
            data = yaml.load(f, Loader=yaml.Loader)
        self.routermethods[router_name] = data.keys()
