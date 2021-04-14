import sys

ver = sys.hexversion
if ver < 30000000:
	raise Exception("This package doesn't work below Python 3.0")

from .Sdk import RedactedCompanyNameSdk
