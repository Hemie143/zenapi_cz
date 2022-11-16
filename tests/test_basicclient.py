#!/usr/bin/env python

from zenapi_cz import ZenAPIClient
from pytest import fixture
import os
import vcr

API_KEY = os.environ.get('ZENOSS_API_KEY', None)
DOMAIN = os.environ.get('ZENOSS_DOMAIN', None)


class APIKeyMissingError(Exception):
    pass


class DomainMissingError(Exception):
    pass


if API_KEY is None:
    raise APIKeyMissingError(
        "All methods require an API key. Connect to your Zenoss Cloud instance with an Admin account to generate an"
        "API key"
    )

if DOMAIN is None:
    raise DomainMissingError(
        "All methods require a Zenoss Cloud instance."
    )


@fixture
def std_keys():
    return ['uuid', 'action', 'result', 'tid', 'type', 'method']

@fixture
def router_keys():
    return ['name', 'permission', 'urlpath', 'documentation', 'namespace', 'filename', 'action']


# @vcr.use_cassette('tests/vcr_cassettes/getDevices.yaml', decode_compressed_response=True, filter_headers=['z-api-key'])
def test_zenapi_connect(std_keys, router_keys):
    """ Test a basic connection to Zenoss Cloud"""
    zenapi = ZenAPIClient(DOMAIN, API_KEY)
    # {"action": "DeviceRouter", "method": "getInfo", "tid": 3, "data": [{"uid": “/zport/dmd"}]}
    # {"action": "IntrospectionRouter", "method": "getAllRouters", "tid": 3, "data": [{}]}
    response = zenapi._request('IntrospectionRouter', 'getAllRouters')

    assert isinstance(response, dict)
    assert set(std_keys).issubset(response.keys()), "All keys should be in the response"
    assert isinstance(response['result'], dict)
    assert isinstance(response['result']['data'], list)
    assert isinstance(response['result']['data'][0], dict)
    assert set(router_keys).issubset(response['result']['data'][0].keys())

# TODO: Test errors

def test_zenapi_query():
    """ Test a standard query from the API"""
    zenapi = ZenAPIClient(DOMAIN, API_KEY)
    response = zenapi.query('IntrospectionRouter', 'getAllRouters')

    assert isinstance(response, dict)
