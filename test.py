import unittest
import json
from PynyTwitter import *

class TestPynyTwitter(unittest.TestCase):
	def setUp(self):
		consumer_key = ""
		access_token = ""
		consumer_secret = ""
		acess_secret = ""
		self.oauth = OAuthInfo(consumer_key, consumer_secret, access_token, acess_secret)

	def test_time_line(self):
		tw = PynyTwitter(self.oauth)
		tweets = tw.time_line()
		self.assertEqual(len(tweets),20)
		

if __name__ == '__main__':
    unittest.main()