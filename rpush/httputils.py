"""
This file is part of PyBBPush.

PyBBPush is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PyBBPush is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PyBBPush.  If not, see <http://www.gnu.org/licenses/>.
"""
import re
import urllib
import httplib
import mimetypes
import os

regex_url = re.compile("^(?:(?P<scheme>https?|ftps?):\/\/)?(?:(?:(?P<username>[\w\.\-\+%!$&'\(\)*\+,;=]+):*(?P<password>[\w\.\-\+%!$&'\(\)*\+,;=]+))@)?(?P<host>[a-z0-9-]+(?:\.[a-z0-9-]+)*(?:\.[a-z\.]{2,6})+)(?:\:(?P<port>[0-9]+))?(?P<path>\/(?:[\w_ \/\-\.~%!\$&\'\(\)\*\+,;=:@]+)?)?(?:\?(?P<query>[\w_ \-\.~%!\$&\'\(\)\*\+,;=:@\/]*))?(?:(?P<fragment>#[\w_ \-\.~%!\$&\'\(\)\*\+,;=:@\/]*))?$", re.IGNORECASE)

def parse_url(url):
	match = re.match(regex_url, url)
	if match == None:
		return False
	return match.groupdict()

def get(url, body = {}, header = {}, **kwargs):
	purl = parse_url(url)
	
	secure = False
	timeout = kwargs.get('timeout', None)
	if purl['scheme'] == 'https':
		secure = True
		
	if secure:
		port = kwargs.get('port', None) or purl.get('port', None) or 443
		conn = httplib.HTTPSConnection(purl['host'], port, None, timeout)
	else:
		port = kwargs.get('port', None) or purl.get('port', None) or 80
		conn = httplib.HTTPConnection(purl['host'], port, None, timeout)
	
	query = urllib.urlencode(body)
	if len(query) > 0 and purl.get('query', None) is not None:
		query += '&'
		
	if purl.get('query', None) is not None:
		query += purl['query']
	
	purl['path'] += '?' + query
	conn.request("GET", purl['path'], None, header)
	response = conn.getresponse()
	
	response_header = {}
	for h in response.getheaders():
		response_header[h[0]] = h[1]
	
	response_body = response.read()
	
	conn.close()
	
	rv = {
		'header': response_header,
		'body': response_body
	}
	return rv
	
def post(url, body = {}, header = {}, **kwargs):
	if header == None:
		header = {}
	purl = parse_url(url)
	
	secure = False
	timeout = kwargs.get('timeout', None)
	if purl['scheme'] == 'https':
		secure = True
		
	files = kwargs.get('files')
			
	if files is not None:
		header['Content-type'], body = encode_post_file(files, body)
	elif isinstance(body, dict):
		for k, v in body.iteritems():
			if isinstance(v, (str, unicode)):
				try:
					body[k] = v.encode('utf-8')
				except Exception:
					pass
		body = urllib.urlencode(body)
		
		
	if secure:
		port = kwargs.get('port', None) or purl.get('port', None) or 443
		conn = httplib.HTTPSConnection(purl['host'], port, None, timeout)
	else:
		port = kwargs.get('port', None) or purl.get('port', None) or 80
		conn = httplib.HTTPConnection(purl['host'], port, None, timeout)
	
	header['Content-type'] = header.get('Content-type') or header.get('Content-Type') or 'application/x-www-form-urlencoded'

	conn.request("POST", purl['path'], body, header)
	response = conn.getresponse()
	
	response_header = {'Status': '%d %s' % (response.status, response.reason)}
	for h in response.getheaders():
		response_header[h[0]] = h[1]
	
	response_body = response.read()
	
	conn.close()
	
	rv = {
		'header': response_header,
		'body': response_body
	}
	return rv


def encode_post_file(files, fields = {}):
	BOUNDARY = '----------boundary------'
	CRLF = '\r\n'
	body = []
	for key in fields:
		body.extend(
		  ['--' + BOUNDARY,
		   'Content-Disposition: form-data; name="%s"' % key,
		   '',
		   str(fields[key]),
		   ])
	
	for path in files:
		name = os.path.basename(path)
		ext = '.' + name.split('.')[-1]
		fl = open(path, 'rb')
		content = fl.read()
		fl.close()
		body.extend(
		  ['--' + BOUNDARY,
		   'Content-Disposition: form-data; name="file"; filename="%s"' % name,
		   # The upload server determines the mime-type, no need to set it.
		   'Content-Type: %s' % mimetypes.types_map[ext],
		   '',
		   str(content),
		   ])
		# Finalize the form body
		body.extend(['--' + BOUNDARY + '--', ''])
	return 'multipart/form-data; boundary=%s' % BOUNDARY, CRLF.join(body)
