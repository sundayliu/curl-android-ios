# -*- coding:utf-8 -*-
# sundayliu
# 2016.06.07

import os
import sys

g_cur_file = os.path.realpath(__file__)
g_cur_dir = os.path.dirname(g_cur_file)

XCODE_DIR="/Applications/Xcode.app/Contents/Developer"

DST_DIR = os.path.join(g_cur_dir, "../prebuilt-with-ssl/iOS")
DST_DIR = os.path.realpath(DST_DIR)

CURL_DIR = os.path.join(g_cur_dir, "../curl")
CURL_DIR = os.path.realpath(CURL_DIR)

ARCHS = ["armv7", "armv7s", "arm64", "i386", "x86_64"]
HOSTS = ["armv7", "armv7s", "arm", "i386", "x86_64"]
PLATFORMS = ["iPhoneOS", "iPhoneOS", "iPhoneOS" , "iPhoneSimulator", "iPhoneSimulator"]
SDKS = ["iPhoneOS", "iPhoneOS", "iPhoneOS" , "iPhoneSimulator", "iPhoneSimulator"]

IPHONEOS_DEPLOYMENT_TARGET = "6"

def is_executable(fpath):
	return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

def check_env():
	cwd = os.getcwd()

	if not os.path.isdir(XCODE_DIR):
		print ("You have to install Xcode and the command line tools first")
		exit(1)


	buildconf_path = os.path.join(CURL_DIR, "buildconf")
	buildconf_path = os.path.realpath(buildconf_path)

	# print is_executable(buildconf_path)

	os.chdir(CURL_DIR)

	configure_path = os.path.join(CURL_DIR, "configure")
	if not is_executable(configure_path):
		print ("Curl needs external tools to be compiled")
		print ("Make sure you have autoconf, automake and libtool installed")

		return_code = os.system(buildconf_path)
		if return_code != 0 :
			print ("Error running the buildconf program")
			os.chdir(g_cur_dir)
			exit(1)

	os.chdir(cwd)

def set_env():
	os.environ["CC"] = os.path.join(XCODE_DIR, "Toolchains/XcodeDefault.xctoolchain/usr/bin/clang")
	os.environ["IPHONEOS_DEPLOYMENT_TARGET"] = "6"

# Build for all the architectures
def do_build_curl(arch, host, platform, sdk):
	cwd = os.getcwd()

	sysroot = os.path.join(XCODE_DIR, "Platforms/%s.platform/Developer/SDKs/%s.sdk" % (platform, sdk))
	os.environ["CFLAGS"] = "-arch %s -pipe -Os -gdwarf-2 -isysroot %s -miphoneos-version-min=%s -fembed-bitcode" % (arch,sysroot, IPHONEOS_DEPLOYMENT_TARGET)
	os.environ["LDFLAGS"] = "-arch %s -isysroot %s" % (arch, sysroot)
	if platform == "iPhoneSimulator":
		os.environ["CPPFLAGS"] = "-D__IPHONE_OS_VERSION_MIN_REQUIRED=%s0000" % IPHONEOS_DEPLOYMENT_TARGET

	os.chdir(CURL_DIR)

	print "CC:%s" % os.environ["CC"]
	print "CFLAGS:%s" % os.environ["CFLAGS"]
	print "LDFLAGS:%s" % os.environ["LDFLAGS"]
	# print "CPPFLAGS:%s" % os.environ["CPPFLAGS"]
	print "IPHONEOS_DEPLOYMENT_TARGET:%s" % os.environ["IPHONEOS_DEPLOYMENT_TARGET"]

	cmd = "./configure --host=\"%s-apple-darwin\" --with-darwinssl --enable-static --disable-shared --enable-thread-resolver --disable-verbose --enable-ipv6 --enable-http" % host
	cmd += " --disable-ftp --disable-file --disable-ldap --disable-ldaps --disable-rtsp --disable-dict --disable-telnet --disable-tftp --disable-pop3 --disable-imap"
	cmd += " --disable-smb --disable-smtp --disable-gopher"
	return_code = os.system(cmd)
	if return_code != 0:
		print ("Error running the cURL configure program")
		os.chdir(cwd)
		exit(1)

	cmd = "make -j4"
	return_code = os.system(cmd)
	if return_code != 0:
		print("Error running the make program")
		os.chdir(cwd)
		exit(1)

	cmd = "mkdir -p %s/%s" % (DST_DIR, arch)
	os.system(cmd)

	cmd = "cp %s/lib/.libs/libcurl.a  %s/%s/" % (CURL_DIR, DST_DIR, arch)
	os.system(cmd)
	cmd = "cp %s/lib/.libs/libcurl.a %s/libcurl-%s.a" % (CURL_DIR, DST_DIR, arch)
	os.system(cmd)

	cmd = "make clean"
	os.system(cmd)

	os.chdir(cwd)

def build_curl():
	length = len(ARCHS)
	for i in range(length):
		do_build_curl(ARCHS[i], HOSTS[i], PLATFORMS[i], SDKS[i])

# Build a single static lib with all the archs in it
def merge_static_library():
	cwd = os.getcwd()

	os.chdir(DST_DIR)
	cmd = "lipo -create -output libcurl.a libcurl-*.a"
	os.system(cmd)
	cmd = "rm libcurl-*.a"
	os.system(cmd)

	os.chdir(cwd)

# Copy cURL headers
def copy_curl_headers():
	src_dir = os.path.join(CURL_DIR, "include")
	cmd = "cp -R %s  %s" % (src_dir, DST_DIR)
	os.system(cmd)

# Patch headers for 64-bit archs
def patch_headers():
	pass
if __name__ == "__main__":
	print ("Building curl for ios ...")
	print ("Current dir:%s" % g_cur_dir)

	check_env()
	set_env()
	build_curl()
	merge_static_library()
	copy_curl_headers()
	patch_headers()