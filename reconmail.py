#! /usr/bin/python

from threading import Timer
from sys import argv
from time import time, strftime, sleep
from urllib import urlopen
import signal
import re
import smtplib

CHECK_SERVER   = "http://192.241.180.172"
CHECK_PATH     = "/check.txt"
CHECK_PAGE     = CHECK_SERVER + CHECK_PATH
CHECK_VALUE    = "True\n"
OFFLINE_VALUE  = ""
CHECK_TIMEOUT  = 5
CHECK_INTERVAL = 5

GET = "GET"
POST = "POST"
SEARCH = 0
METHOD = 1
URL = 2
DATA = 3

last_message_logged = ""
response = ""
email = ""

def handler(signum, frame):
	log("Hang caught, retrying...")
	check_connection()

def check_connection():
	start_time = time()

	global response
	last_response = response

	try:
		signal.alarm(CHECK_TIMEOUT)
		page = urlopen(CHECK_PAGE)
		signal.alarm(0)
		response = page.read()
		page.close()
	except:
		response = OFFLINE_VALUE
		if last_response != OFFLINE_VALUE:
			try:
				sleep(1)
				signal.alarm(CHECK_TIMEOUT)
				page = urlopen(CHECK_PAGE)
				signal.alarm(0)
				response = page.read()
				page.close()
			except:
				response = OFFLINE_VALUE

	if response != CHECK_VALUE:
		if response == OFFLINE_VALUE:
			log("You are offline.")
		else:
			authenticate(response)
	else:
		log("You are online!")

	if CHECK_INTERVAL >= 0:
		wait_time = CHECK_INTERVAL - (time() - start_time)
		if wait_time < 0:
			wait_time = 0
		Timer(wait_time, check_connection).start()
	

def authenticate(response):
	if "Message from" in response:
		title = re.search('<h1>(.*):</h1>', response).group(1)
		message = re.search('<b>Message #[0-9]*:</b>(.*)<form', response).group(1)
		message = message.replace("<br>", "\n").strip()
		ack = re.search('name="a" value="([a-z]*)"', response).group(1)
		msgid = re.search('name="msgid" value="([0-9]*)"', response).group(1)

		print title
		print message

		try:
			signal.alarm(CHECK_TIMEOUT)
			page = urlopen(CHECK_SERVER + "/index.php?a=" + ack + "&msgid=" + msgid)
			signal.alarm(0)
			sleep(1)
		except:
			log("Unable to authenticate.")
			return
		page.read()
		page.close()

		log("Authenticated!", True)

		global email
		msg  = "From: dan+python@hlavenka.me\r\n"
		msg += "To: " + email + "\r\n"
		msg += "Subject: " + title + "\r\n\r\n"
		msg += message

		s = smtplib.SMTP('localhost')
		s.sendmail("dan+python@hlavenka.me", [email], msg)
		s.quit()
	else:
		log("Unknown response: " + response)

def get_timestamp():
	return strftime("%Y-%m-%d %I:%M %p - ")

def log(message):
	global last_message_logged
	if message != last_message_logged:
		print get_timestamp() + message
		last_message_logged = message

if __name__ == "__main__":
	if len(argv) > 1:
		email = argv[1]
		signal.signal(signal.SIGALRM, handler)
		log("Started.")
		check_connection()
	else:
		print "Usage: reconmail.py <email>"
