#!/usr/bin/env python3

from PyRedactedCompanyName import *

import numpy as np
import cv2
import time

print("Finished importing")

imei   = "1234123412341234"
code   = "RedactedLicense"
imtype = 1
height = 480
width  = 640

rcn = RedactedCompanyNameSdk(imei, code, debug=True)
rcn.set_image_params(imtype, height, width)
rcn.initUser("RedactedUsername")
print("Initialized successfully")

cap = cv2.VideoCapture(2)
cap.set(3,width)
cap.set(4,height)

def wake_camera():
	ret, _ = cap.read()
	return ret

def cap_camera():
	_, buf = cap.read()
	res = cv2.imwrite("tmp.bmp", buf)

def init():
	rcn = RedactedCompanyNameSdk(imei, code, debug=True)
	rcn.set_image_params(imtype, height, width)
	rcn.initUser("RedactedUsername")
	print("Initialized successfully")

def initUser(userID):
	return rcn.initUser(userID)

def wrap_image_operation(func):
	def param_wrapper():
		started = time.time()
		frame = cap.read()[1]
		res = func(frame)
		finished = time.time()
		print("Result: "+str(res))
		print("Elapsed: "+str(finished-started))

	return param_wrapper

@wrap_image_operation
def detect(frame):
	return rcn.detect_face(frame)

@wrap_image_operation
def enroll(frame):
	return rcn.regular_enroll(frame)

@wrap_image_operation
def match(frame):
	return rcn.match(frame)

@wrap_image_operation
def match_quick(frame):
	return rcn.match_quick(frame)

@wrap_image_operation
def test_match_with_enroll(frame):
	return rcn.test_match_with_enroll(frame)

print("Woke" if wake_camera() else "Could not wake")

while True:
	com = input("> ").split(" ")
	first = com[0].lower()
	if   first == "init":
		init()
	elif first == "user":
		userID = com[1]
		print(initUser(userID))
	elif first == "detect":
		detect()
	elif first == "enroll":
		enroll()
	elif first == "match":
		match()
	elif first == "qm":
		match_quick()
	elif first == "cap":
		cap_camera()
	elif first == "tme":
		test_match_with_enroll()
	elif first == "nanas":
		print(rcn.test_nanas())
	elif first == "exit":
		exit()
	else:
		print("Unknown input: "+first)
