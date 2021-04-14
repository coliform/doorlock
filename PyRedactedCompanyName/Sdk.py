from ctypes import *
import os
import numpy as np
import numpy.ctypeslib as npct
import cv2
import io
import sys
from PIL import Image

def str_to_char_p(string):
	#print("Encoding {}".format(str.encode(string)))
	return c_char_p(str.encode(string))

def get_length_of_char_p(in_pointer):
	return len(ctypes.cast(in_pointer, ctypes.c_char_p).value)

class RedactedCompanyNameSdk:
	def __init__(self, imei, customerCode, height=0, width=0, debug=False, angle=0):
		self._loc_current_dir = os.path.dirname(__file__) + "/"

		#which = "debug" if debug else "release"
		self._loc_librcn = self._loc_current_dir + "/rcnlib/libRedactedCompanyNameCore.debug.so"

		self._soins = CDLL(self._loc_librcn)

		#self._loc_current_dir = os.getcwd()+"/"

		self._savePath     = str_to_char_p(self._loc_current_dir + "rcnsav")
		self._imei         = str_to_char_p(imei)
		self._customerCode = str_to_char_p(customerCode)
		self._assetPath    = str_to_char_p(self._loc_current_dir + "rcndep")
		self._security     = str_to_char_p("Normal")
		self._angle        = angle
		self._height = height
		self._width  = width

		self._soins.new_instance.restype = c_void_p
		self._soins.init.argtypes = [c_void_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
		self._soins.load_users.argtypes = [c_void_p, c_char_p]
		self._soins.initUser.argtypes = [c_void_p, c_char_p, c_char_p, c_char_p]
		self._soins.bmp_to_mat.argtypes = [c_void_p, c_int]
		self._soins.nv21_to_mat.argtypes = [c_void_p, c_int, c_int, c_int]
		self._soins.detect_face.argtypes = [c_void_p, c_char_p, c_int]
		self._soins.regular_enroll.argtypes = [c_void_p, c_char_p, c_int, c_int, c_int]
		self._soins.match.argtypes = [c_void_p, c_ubyte, c_int, c_int, c_int]
		self._soins.match_quick.argtypes = [c_void_p, c_ubyte, c_int, c_int, c_int]
		#self._soins.match_users.argtypes = [c_void_p, c_char_p, c_int]
		self._soins.match_all.argtypes = [c_void_p, c_char_p, c_int]
		self._soins.get_detection_angle.argtypes = [c_void_p, c_ubyte, c_int, c_int, c_int]
		self._soins.rotate_enroll.argtypes = [c_void_p, c_char_p, c_int, c_int, c_int, c_int]
		self._soins.load_enrolls.argtypes = [c_void_p, c_char_p]

		self._sdkins = self._soins.new_instance()
		res = self.init(self._savePath, self._imei, self._customerCode, self._assetPath, self._security, self._angle)
		if int(res) != 1: raise Exception("Could not initialize. Response: "+str(res))
		if height > 0 and width > 0: self.set_image_params(height, width)

		self._users = []

	def refresh_users(self):
		prefix = "enrollsb"
		prefix_len = len(prefix)
		try:
			files = os.listdir(self._loc_current_dir + "rcnsav/Enrolls")
		except Exception as e:
			self._users = []
			self._users_char_p = str_to_char_p("")
			return
		users = []
		for name in files:
			if name[:prefix_len] == prefix:
				users.append(name[prefix_len:].split(".")[0])
		self._users = users
		self._users_char_p = str_to_char_p(','.join(self._users))
		self._soins.load_users(self._sdkins, self._users_char_p)
		print("Users: {}".format(users if len(users) else "NONE"))

	def load_enrolls(self, enrolls):
		enrolls = str_to_char_p(enrolls)
		self._soins.load_enrolls(self._sdkins, enrolls)

	def set_image_params(self, height, width):
		if height < 0 or width < 0:
			raise Exception("Invalid resolution. height & width > 0")
		self._height = height
		self._width  = width
		self._length = (height * width * 3) + 54

	def verify_so(self):
		if self._soins is None: raise Exception("SO is not initialized")

	def init(self, savePath, imei, customerCode, assetPath, security, angle):
		self.verify_so()
		return self._soins.init(self._sdkins, savePath, imei, customerCode, assetPath, security, angle)

	def set_debuggable(self, decision):
		self.verify_so()
		return self._soins.set_debuggable(self._sdkins, decision)

	def set_as(self, decision):
		self.verify_so()
		return self._soins.set_as(self._sdkins, decision)

	def is_as(self):
		self.verify_so()
		return self._soins.is_as(self._sdkins)

	def verify_init(self):
		self.verify_so()
		if self._sdkins is None: raise Exception("SDK is not initialized")

	def initUser(self, userID):
		self.verify_init()
		res = self._soins.initUser(self._sdkins, str_to_char_p(userID), self._security, self._assetPath)
		if userID not in self._users: self._users.append(userID)
		self._user = userID
		return res

	def get_cpp_mat(self, buf):
		self.verify_init()
		buf = cv2.imencode('.bmp', buf)
		buf = buf[1].tostring()
		return buf

	def _detect_face(self, image):
		self.verify_init()
		#print("Passing image of type {0} to face detection with length {1} and imtype {2}".format(type(image), str(len(image)), imtype))
		return self._soins.detect_face(self._sdkins, self.get_cpp_mat(image), self._length)
	
	def match_all(self, image):
		self.verify_init()
		return self._soins.match_all(self._sdkins, self.get_cpp_mat(image), self._length)

	def _get_detection_angle(self, image, imtype, height, width):
		self.verify_init()
		img = Image.open(io.BytesIO(image))
		size = img.size
		#print("h: {0} w: {1} type; {2}".format(size[1], size[0], type(image)))
		return self._soins.get_detection_angle(self._sdkins, image, imtype, size[1], size[0])

	def _regular_enroll(self, image, imtype, height, width, userID):
		self.verify_init()
		self.initUser(userID)
		#print("Passing image of type {0} to enroll with length {1} and imtype {2}".format(type(image), str(len(image)), imtype))
		#print("Enrolling for " + self._user)
		return self._soins.regular_enroll(self._sdkins, image, imtype, height, width)

	def _rotate_enroll(self, image, imtype, height, width, userID):
		self.verify_init()
		self.initUser(userID)
		#print("Passing image of type {0} to enroll with length {1} and imtype {2}".format(type(image), str(len(image)), imtype))
		#print("Enrolling for " + self._user)
		ba = bytearray()
		for byte in image:
			ba.append(byte)
		image = bytes(ba)
		passable_image = c_char_p(image)
		return self._soins.rotate_enroll(self._sdkins, passable_image, imtype, height, width, sys.getsizeof(image))

	def _match(self, image, imtype, height, width):
		self.verify_init()
		return self._soins.match(self._sdkins, image, imtype, height, width)

	def _match_quick(self, image, imtype, height, width):
		self.verify_init()
		res = self._soins.match_all(self._sdkins, image, imtype, height, width)
		if res >= 0: print("Matched successfully with " + self._users[res])
		return res

	def _match_users(self, image, imtype, height, width, users, assetPath):
		self.verify_init()
		return self._soins.match_users(self._sdkins, image, imtype, height, width, users, assetPath)

	def image_operation(self, func, image, userID = None, imtype=4):
		height = self._height if self._height > 0  else len(image[1])
		width  = self._width  if self._width > 0   else len(image[1][0])
		if userID is None: return func(image, imtype, height, width)
		else: return func(image, imtype, height, width, userID)

	def detect_face(self, image):
		return self.image_operation(self._detect_face, image)

	def get_detection_angle(self, image):
		return self.image_operation(self._get_detection_angle, image)

	def regular_enroll(self, image, userID, imtype=4):
		imtype = self._imtype if imtype == 4 else imtype
		return self.image_operation(self._regular_enroll, image, userID, imtype)

	def rotate_enroll(self, image, userID, imtype=4):
		imtype = self._imtype if imtype == 4 else imtype
		return self.image_operation(self._rotate_enroll, image, userID, imtype) == 1

	def match(self, image):
		return self.image_operation(self._match, image)

	def match_quick(self, image):
		return self.image_operation(self._match_quick, image)

	def match_users(self, image):
		imtype = self._imtype if self._imtype <= 2 else 1
		res = self._match_users(self.get_cpp_mat(image), imtype, self._height, self._width, self._users_char_p, self._assetPath)
		return self._users[res] if res >= 0 else res

	def which_user(self, index):
		return None if index < 0 or index >= len(self._users) else self._users[index]
