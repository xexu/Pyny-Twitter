import urllib
import urllib2
import time
import hmac
import hashlib
import random
import base64
import json
from datetime import datetime

class OAuthInfo:
	def __init__(self, ConsumerKey, ConsumerSecret, AccessToken, AcessSecret):
		self.ConsumerKey = ConsumerKey
		self.ConsumerSecret = ConsumerSecret
		self.AccessToken = AccessToken
		self.AcessSecret = AcessSecret
		self.Version = "1.0"
		self.SignatureMethod = "HMAC-SHA1"

class Tweet:
	def __init__(self, user_name, screen_name, created_at, text):
		self.user_name = user_name
		self.screen_name = screen_name
		self.created_at = created_at
		self.text = text

	def format(self):
		t = self.text + "\n" + self.screen_name + "\t" + self.created_at.strftime("%H:%M:%S %d/%m/%y")
		return t

class PynyTwitter:

	def __init__(self, oauthinfo):
		self.oauth = oauthinfo


	def update_status(self, tweet):
		pass

	def time_line(self, sinceId = None, count = 20):
		tweets = self._get_time_line("https://api.twitter.com/1/statuses/home_timeline.json", sinceId, count)
		return tweets
	
	def _get_time_line(self, url, sinceId = None, count = 5):
		builder = RequestBuilder(self.oauth, url, "GET")

		if sinceId is not None:
			builder.add_parameter("since_id", str(sinceId))
		if count is not None:
			builder.add_parameter("count", str(count))

		response = builder.execute()
		tweets = builder._parse_json_response(response)
		return tweets


class RequestBuilder:

	def __init__(self, oauthinfo, url, method = "POST"):
		self.oauth = oauthinfo
		self.method = method
		self.url = url
		self.custom_parameters = {}

	def execute(self):
		timestamp = self._get_timestamp();
		nonce = self._get_nonce()
		request_url = self._get_request_url()

		self._add_oauth_parameters(timestamp, nonce)
		base_string = self._get_base_string()

		signature = self._get_signature("&".join([self._encode(self.oauth.ConsumerSecret), self._encode(self.oauth.AcessSecret)]), base_string)
		self.add_parameter("oauth_signature", signature)

		oauth_headers = self._build_oauth_headers()


		httpRequest = urllib2.Request(request_url)
		httpRequest.add_header("Authorization", oauth_headers)

		# print base_string
		# print oauth_headers
		# print self.oauth.ConsumerKey
		# print self.oauth.ConsumerSecret
		# print self.oauth.AccessToken
		# print self.oauth.AcessSecret
		# print httpRequest.get_type()
		# print httpRequest.get_full_url()
		# print "-"*25
		# print httpRequest.get_data()
		# print httpRequest.get_host()
		# print httpRequest.get_method()

		try:
			httpResponse = urllib2.urlopen(httpRequest)
		except urllib2.HTTPError, e:
			return "--Response Error: %s" % e

		return httpResponse

	def _parse_json_response(self, response):
		tweets = []
		li = json.load(response)
		for item in li:
			try:
				rt = item["retweeted_status"]
				text = rt["text"]
				screen_name = item["user"]["screen_name"] + " RT @" + rt["user"]["screen_name"]
			except Exception, e:
				screen_name = item["user"]["screen_name"]
				text = item["text"]
			finally:
				user_name = item["user"]["name"]
				time_data = item["created_at"].split(" ")
				del time_data[4]
				time_string = " ".join(time_data)
				created_at = datetime.strptime(time_string, '%a %b %d %H:%M:%S %Y')
				tweets.append(Tweet(user_name, screen_name, created_at, text))
		return tweets
				


		return tweets
	def _get_base_string(self):
		params_list = []
		for tup in self.custom_parameters.items():
			params_list.append("=".join(tup))
		
		items_list = [self.method, self._encode(self.url), self._encode("&".join(sorted(params_list)))]
		base_string = "&".join(items_list)
		return base_string

	def _get_request_url(self):
		if self.method != "GET" or self.custom_parameters.keys().count == 0:
			return self.url
		params_dict = {}
		for k, v in self.custom_parameters.items():
			params_dict[k] = v
		return "?".join([self.url, urllib.urlencode(params_dict)])


	def _add_oauth_parameters(self, timestamp, nonce):
		self.add_parameter("oauth_consumer_key",self.oauth.ConsumerKey)
		self.add_parameter("oauth_token",self.oauth.AccessToken)
		self.add_parameter("oauth_version",self.oauth.Version)
		self.add_parameter("oauth_nonce",str(nonce))
		self.add_parameter("oauth_timestamp",str(timestamp))
		self.add_parameter("oauth_signature_method",self.oauth.SignatureMethod)


	def add_parameter(self, key, value):
		self.custom_parameters[key] = value


	def _get_signature(self,signingKey, stringToHash):
		hmacAlg = hmac.HMAC(signingKey, stringToHash, hashlib.sha1)
		return base64.b64encode(hmacAlg.digest())


	def _build_oauth_headers(self):
		header_params = []
		for k, v in self.custom_parameters.items():
			if k.find("oauth_") != -1:
				header_params.append("=".join([k, "\"" + self._encode(v) + "\""]))
		return "OAuth " + ",".join(sorted(header_params))

	def _get_nonce(self):
		return random.randint(1, 999999999)

	def _get_timestamp(self):
		return int(time.time())

	def _encode(self,string):
		return urllib.quote(string, safe="")


class PynyTwitterUI:
	def __init(self):
		self.oauth = OAuthInfo(consumer_key, consumer_secret, access_token, acess_secret)

	def get_timeline(self):
		pyny = PynyTwitter(self.oauth)
		for t in pyny.get_timeline():
			print t.format()