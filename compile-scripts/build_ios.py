# -*- coding:utf-8 -*-
# sundayliu
# 2016.06.07

import os
import sys

g_cur_file = os.path.realpath(__file__)
g_cur_dir = os.path.dirname(g_cur_file)

XCODE_DIR="/Applications/Xcode.app/Contents/Developer"

def is_executable(fpath):
	return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

def check_env():
	if not os.path.isdir(XCODE_DIR):
		print ("You have to install Xcode and the command line tools first")
		exit(1)
	curl_dir = os.path.join(g_cur_dir, "../curl")
	curl_dir = os.path.realpath(curl_dir)

	buildconf_path = os.path.join(curl_dir, "buildconf")
	buildconf_path = os.path.realpath(buildconf_path)

	print is_executable(buildconf_path)


	configure_path = os.path.join(curl_dir, "configure")
	if not os.path.isfile(configure_path):
		print ("Curl needs external tools to be compiled")
		print ("Make sure you have autoconf, automake and libtool installed")
		exit(1)

if __name__ == "__main__":
	print ("Building curl for ios ...")
	print ("Current dir:%s" % g_cur_dir)

	check_env()