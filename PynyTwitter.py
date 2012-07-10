import urllib
import urllib2
import time
import hmac
import hashlib
import random
import base64
import json
from datetime import datetime
from sys import stdout

class OAuthInfo:
	def __init__(self, ConsumerKey, ConsumerSecret, AccessToken, AcessSecret):
		self.ConsumerKey = ConsumerKey
		self.ConsumerSecret = ConsumerSecret
		self.AccessToken = AccessToken
		self.AcessSecret = AcessSecret
		self.Version = "1.0"
		self.SignatureMethod = "HMAC-SHA1"


	def __init__(self):
		json_data = json.load(open("credentials.json"))
		self.ConsumerKey = json_data["consumer_key"]
		self.ConsumerSecret = json_data["consumer_secret"]
		self.AccessToken = json_data["access_token"]
		self.AcessSecret = json_data["acess_secret"]
		self.Version = "1.0"
		self.SignatureMethod = "HMAC-SHA1"



class Tweet:
	def __init__(self, user_name, screen_name, created_at, text):
		self.user_name = user_name
		self.screen_name = screen_name
		self.created_at = created_at
		self.text = text

class PynyTwitter:
	def __init__(self, oauthinfo):
		self.oauth = oauthinfo

	def mentions(self, count = 20, sinceId = None):
		tweets = self._get_timeline("https://api.twitter.com/1/statuses/mentions.json", count, sinceId)
		return tweets


	def update_status(self, status):
		return self._update_status(status)


	def home_timeline(self, count = 20, sinceId = None):
		tweets = self._get_timeline("https://api.twitter.com/1/statuses/home_timeline.json", count, sinceId)
		return tweets


	def user_timeline(self, count = 20, sinceId = None):
		tweets = self._get_timeline("https://api.twitter.com/1/statuses/user_timeline.json", count, sinceId)
		return tweets


	def _get_timeline(self, url, count = 20, sinceId = None):
		builder = RequestBuilder(self.oauth, url, "GET")

		if sinceId is not None:
			builder._add_parameter("since_id", str(sinceId))
		if count is not None:
			builder._add_parameter("count", str(count))

		response = builder.execute()
		tweets = builder._parse_json_response(response)
		return tweets


	def _update_status(self, status):
			builder = RequestBuilder(self.oauth,"https://api.twitter.com/1/statuses/update.json")
			builder._add_parameter("status", status[:140])
			response = builder.execute()
			return True



class RequestBuilder:
	def __init__(self, oauthinfo, url, method = "POST"):
		self.oauth = oauthinfo
		self.method = method
		self.url = url
		self.custom_parameters = {}
		self.oauth_parameters = {}


	def execute(self):
		timestamp = self._get_timestamp();
		nonce = self._get_nonce()
		self._add_oauth_parameters(timestamp, nonce)

		base_string = self._get_base_string()
		signature = self._get_signature("&".join([self._encode(self.oauth.ConsumerSecret), self._encode(self.oauth.AcessSecret)]), base_string)
		self._add_oauth_parameter("oauth_signature", signature)
		oauth_headers = self._build_oauth_headers()

		request_url = self._get_request_url()
		request_data = self._get_request_data()

		if request_data is None:
			httpRequest = urllib2.Request(request_url)
		else:
			httpRequest = urllib2.Request(request_url, request_data)
		
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
			print "--Response Error: %s" % e
			return None
		return httpResponse


	def _get_request_data(self):
		if self.method == "GET":
			return None
		return urllib.urlencode(self.custom_parameters)


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


	def _get_base_string(self):
		params_list = []
		for k, v in self.custom_parameters.items() + self.oauth_parameters.items():
			params_list.append("=".join([self._encode(k), self._encode(v)]))
		
		items_list = [self.method, self._encode(self.url), self._encode("&".join(sorted(params_list)))]
		base_string = "&".join(items_list)
		return base_string


	def _get_request_url(self):
		if self.method != "GET" or self.custom_parameters.keys().count == 0:
			return self.url
		return "?".join([self.url, urllib.urlencode(self.custom_parameters)])


	def _add_oauth_parameters(self, timestamp, nonce):
		self._add_oauth_parameter("oauth_consumer_key",self.oauth.ConsumerKey)
		self._add_oauth_parameter("oauth_token",self.oauth.AccessToken)
		self._add_oauth_parameter("oauth_version",self.oauth.Version)
		self._add_oauth_parameter("oauth_nonce",str(nonce))
		self._add_oauth_parameter("oauth_timestamp",str(timestamp))
		self._add_oauth_parameter("oauth_signature_method",self.oauth.SignatureMethod)
		return self


	def _add_parameter(self, key, value):
		self.custom_parameters[key] = value
		return self


	def _add_oauth_parameter(self, key, value):
		self.oauth_parameters[key] = value
		return self


	def _get_signature(self,signingKey, stringToHash):
		hmacAlg = hmac.HMAC(signingKey, stringToHash, hashlib.sha1)
		return base64.b64encode(hmacAlg.digest())


	def _build_oauth_headers(self):
		header_params = []
		for k, v in self.oauth_parameters.items():
			header_params.append("=".join([k, "\"" + self._encode(v) + "\""]))
		return "OAuth " + ",".join(sorted(header_params))


	def _get_nonce(self):
		return random.randint(1, 999999999)


	def _get_timestamp(self):
		return int(time.time())


	def _encode(self,string):
		return urllib.quote(string, safe="")



class PynyTwitterUI:
	def __init__(self, writer):
		self.oauth = OAuthInfo()
		self.pyny = PynyTwitter(self.oauth)
		self.writer = writer


	def get_home_timeline(self,count=20):
		self.writer.write_timeline(self.pyny.home_timeline())


	def get_user_timeline(self,count=20):
		for t in self.pyny.user_timeline(count):
			print t.format()


	def get_mentions(self):
		for t in self.pyny.mentions():
			print t.format()


	def update_status(self, status):
		if self.pyny.update_status(status):
			print "Status Updated: " + status



class PynyWriter:
	def __init__(self, file = None , mode = None):
		self.file = file
		self.mode = mode

	def write_tweet(self, tweet):
		raise NotImplementedError
	def write_timeline(self, timeline):
		raise NotImplementedError
	def _open(self):
		if self.file is not None:
			if self.mode is not None:
				self.output = open(self.file, self.mode)
			else:
				self.output = open(self.file, "w")
		else:
			self.output = stdout

	def _close(self):
		if self.output != stdout:
			self.output.close()


class PlainTextWriter(PynyWriter):
	def write_tweet(self, tweet):
		self._open()
		self._write_tweet(tweet)
		self._close()

	def write_timeline(self, timeline):
		self._open()
		for t in timeline:
			self._write_tweet(t)
		self._close()

	def _write_tweet(self, tweet):
		text = tweet.text + "\n" + tweet.screen_name + "\t" + tweet.created_at.strftime("%H:%M:%S %d/%m/%y")+"\n"
		self.output.write(text.encode("utf-8"))