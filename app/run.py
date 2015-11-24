import falcon
import requests
import json
from socket import gethostbyname, gaierror
from urlparse import urlparse
from geoip import geolite2
from ipwhois import IPWhois

class defaultResource:
    def on_get(self, req, resp):
        resp.data = json.dumps({'message': 'Api Web Profile Ready!'})
        resp.content_type = 'application/json'
        resp.status = falcon.HTTP_200

class profileResource:
    def on_post(self, req, resp):
         try:
             raw_json = req.stream.read()
         except Exception as ex:
             raise falcon.HTTPError(falcon.HTTP_400,'Error',ex.message)

         try:
            result = json.loads(raw_json, encoding='utf-8')
         except ValueError:
            raise falcon.HTTPError(falcon.HTTP_400,'Invalid JSON','Could not decode the request body. The JSON was incorrect.')
            result = false

         if bool(result):
            analise = result['url']

            if analise:
                o = urlparse(analise)

                url = o.geturl()
                status = False
                headers = False
                encoding = False
                scheme = o.scheme

                if not scheme:
                    scheme = 'http'
                    analise = 'http://' + analise
                    o = urlparse(analise)
                    url = o.geturl()
                    scheme = o.scheme

                try:
                    r = requests.get(url)
                    response = 'Ok'
                    status = r.status_code
                    encoding = r.encoding
                    headers = dict(r.headers)
                except requests.exceptions.Timeout:
                    response = 'TimeOut'
                except requests.exceptions.TooManyRedirects:
                    response = 'TooManyRedirects'
                except requests.exceptions.ConnectionError as e:
                    response = 'NoResponse'

                geo = False
                match = False

                try:
                    ip = gethostbyname(o.netloc)
                    match = geolite2.lookup(ip)
                    if match is not None:
                        geo = {
                            'country': match.country,
                            'continent': match.continent,
                            'timezone': match.timezone
                        }
                    obj = IPWhois('74.125.225.229')
                    results = obj.lookup_rdap(depth=1)
                    
                except gaierror:
                    ip = False

                data = {
                        'response': response,
                        'scheme': scheme,
                        'url': url,
                        'port': o.port,
                        'netloc': o.netloc,
                        'path': o.path,
                        'encoding': encoding,
                        'status': status,
                        'headers': headers,
                        'ip': ip,
                        'geo': geo
                    }

                resp.body = json.dumps(data)

api = falcon.API()

profile = profileResource()
df = defaultResource()

api.add_route('/', df)
api.add_route('/profile', profile)