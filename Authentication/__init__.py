import re
import urllib.request
from urllib.parse import urlencode
from flask import *

class SteamSignIn():

	_provider = 'https://steamcommunity.com/openid/login'

	
	def RedirectUser(self, strPostData):
		resp = redirect('{0}?{1}'.format(self._provider, strPostData), 303)
		resp.headers["Content-Type"] = 'application/x-www-form-urlencoded'
		return resp
	
	# This is the basic setup for getting steam to acknowledge our request for OpenID (2).
	# Our responseURL is where we want Steam to send us back to once the user has done something.
	# Returns a string that is safe to use via a POST.	
	def ConstructURL(self, responseURL):

		# Ensure the protocol is at least http (spec requirement). You should use https but often test environments don't guarantee this...
		if responseURL[0:4] != 'http':
			errMessage = 'http was not found at the start of the string {0}.'.format(responseURL)
			raise ValueError(errMessage)
	

		authParameters = {
			'openid.ns':'http://specs.openid.net/auth/2.0',
			'openid.mode': 'checkid_setup',
			'openid.return_to': responseURL, 
			'openid.realm': responseURL, 
			'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select', 
			'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select'
		}
		return urlencode(authParameters)


	# Takes a dictionary or a dict-like object. 
	# This should be provided by whatever framework you're using with all the GET variables passed on.
	def ValidateResults(self, results):

	
		validationArgs ={
			'openid.assoc_handle': results['openid.assoc_handle'],
			'openid.signed': results['openid.signed'],
			'openid.sig' : results['openid.sig'],
			'openid.ns': results ['openid.ns']
		}

		# Basically, we split apart one of the args steam sends back only to send it back to them to validate!
		# We also append check_authentication which tells OpenID2 to actually yknow, validate what we send.
		signedArgs = results['openid.signed'].split(',')

		for item in signedArgs:
			itemArg = 'openid.{0}'.format(item)
			if results[itemArg] not in validationArgs:
				validationArgs[itemArg] = results[itemArg]

		validationArgs['openid.mode'] = 'check_authentication'
		parsedArgs = urlencode(validationArgs).encode('utf-8')
	
		with urllib.request.urlopen(self._provider, parsedArgs) as requestData:
			responseData = requestData.read().decode('utf-8')
			cookie = requestData.info().get_all('Set-Cookie')
    		
		print(cookie)
		
		# is_valid:true is what Steam returns if something is valid. The alternative is is_valid:false which obviously, is false. 
		if re.search('is_valid:true', responseData):
			matched64ID = re.search('https://steamcommunity.com/openid/id/(\d+)', results['openid.claimed_id'])
			if matched64ID != None or matched64ID.group(1) != None:
				return matched64ID.group(1)
			else:
				# If we somehow fail to get a valid steam64ID, just return false
				return False
		else:
			# Same again here
			return False