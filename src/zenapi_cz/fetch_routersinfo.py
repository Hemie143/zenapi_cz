import os
import yaml
from src.zenapi_cz.zenapi_basic_client import ZenAPIClient


API_KEY = os.environ.get('ZENOSS_API_KEY', None)
DOMAIN = os.environ.get('ZENOSS_DOMAIN', None)

zenapi = ZenAPIClient(DOMAIN, API_KEY)

# Fetch information about all routers
print('Fetching list of routers')
response = zenapi._request('IntrospectionRouter', 'getAllRouters', data=[{}])

result = response['result']
data = result['data']
allrouters = {}
for router in data:
    allrouters[router['action']] = {
        'name': router['name'],
        'endpoint': router['urlpath'],
        'permission': router['permission'],
        'documentation': router['documentation'],
        'namespace': router['namespace'],
        'filename': router['filename'],
    }

with open(r'routers/allrouters.yaml', 'w') as file:
    yaml.dump(allrouters, file)

# Fetch methods per router
for router in data:
    router_name = router['action']
    print(f'Fetching methods for router {router_name}')
    response = zenapi._request('IntrospectionRouter', 'getRouterMethods', data=[{'router': router_name}])
    filename = f'./routers/{router_name}.yaml'
    with open(filename, 'w') as f:
        yaml.dump(response['result']['data'], f)
