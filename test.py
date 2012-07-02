import unittest
import json
import time
import random
from PynyTwitter import *

class TestPynyTwitter(unittest.TestCase):
	def setUp(self):
		self.oauth = OAuthInfo()
		self.pyny = PynyTwitter(self.oauth)

	def test_time_line_def(self):
		tweets = self.pyny.home_timeline()
		self.assertEqual(len(tweets),20)

	def test_time_line_5(self):
		tweets = self.pyny.home_timeline(count=5)
		self.assertEqual(len(tweets),5)

	def test_user_timeline(self):
		tweets = self.pyny.user_timeline(count=3)
		self.assertEqual(len(tweets),3)

	def test_update_status(self):
		n = random.randint(1, 999999999)
		tweet_text = "this is a test-tweet rand=" + str(n)
		self.pyny.update_status(tweet_text)
		time.sleep(3) #waits for consistence in API calls
		tweet = self.pyny.user_timeline(count=1)[0]
		self.assertEqual(tweet.text, tweet_text)
	
	def test_mentions(self):
		tweets = self.pyny.mentions()
		self.assertEqual(len(tweets), 1)

		
if __name__ == '__main__':
    unittest.main()