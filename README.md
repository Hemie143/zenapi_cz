zenapi_cz
---------

This is an API for Zenoss Collection Zone. 
Zenoss is providing an API wrapper, however it is based on Python 2. It is now time to develop a more modern wrapper based on Python 3. 
I don't intend to make this wrapper work with any On-Premises version of Zenoss. 

This wrapper has been tested with Zenoss Cloud.

Concepts
--------
1. The library provides two types of API wrappers, one with basic implementation and the second one which is more 
object-oriented.
2. The credentials and all other connection data are provided by the client, not with a configuration located in the library folder. 
3. The development should be test-driven.
4. The library should be published on PyPI (not like zenapilib).

Other related projects
----------------------
Official API wrapper and CLI from Zenoss:
https://github.com/zenoss/zenoss-RM-api

This project hasn't been updated since 2019. 
https://github.com/Zuora-TechOps/ZenossAPIClient

This project hasn't be updated since 2010.
https://github.com/ekarlso/python-zenoss-api
