#!/usr/bin/env python

# Minimize picture and video script
# Maxime Morel - maxime@mmorel.eu
# 2015/12/17
#
# This script will reduce size and homogenize media library.
# Convert to jpg, quality 85
# Convert to mkv
#
# Requirements:
# python
# gm convert (graphicsmagick)
# ffmeg
# ufraw-batch (gimp-ufraw), for CR2 convertion (with imagemagick)
# dcraw, for CR2 convertion (with graphicsmagic)

# Usage:
# ./minify.py | tee logs/minify-$(date +%F-%T).log

import sys
import os
import time
import subprocess
import shutil

def getRatio(src, dst):
	srcsize = os.stat(src).st_size
	try:
		dstsize = os.stat(dst).st_size
	except BaseException as err:
		dstsize = 0
		print('error: ', src, '->', dst, ' - ', err)
		#pass
	ratio = dstsize / srcsize
	return ratio

print('Picture and video minification script')

base = 'photos_originals'
if len(sys.argv) >= 2:
        base = sys.argv[1]

newbase = '../photos_minified'
if len(sys.argv) >= 3:
        newbase = sys.argv[2]

print(os.path.join(os.getcwd(), base))
print(os.path.join(os.getcwd(), base, newbase))

print('Proceed? ')
res = input()
if res != 'y':
        sys.exit()

os.chdir(base)

if not os.path.isdir(newbase):
	os.mkdir(newbase)

for root, dirs, files in os.walk('.'):
	for dir in dirs:
		fullsrcdir = os.path.join(root, dir)
		fulldstdir = os.path.join(newbase, fullsrcdir)
		print('mkdir: ', fullsrcdir, '->', fulldstdir)
		if not os.path.isdir(fulldstdir):
			os.mkdir(fulldstdir)

	for file in files:
		fullsrcpath = os.path.join(root, file)
		basefile, extension = os.path.splitext(file)
		interdstpath = os.path.join(newbase, root, basefile)
		fulldstpath = interdstpath + extension
		extension = extension.lower()
		if basefile.startswith('.'):
			print('dot file: ', fullsrcpath)
			continue
		if extension in ['.jpg', '.jpeg', '.bmp', '.png', '.cr2']:
			fulldstpath = interdstpath + '.jpg'
			if not os.path.exists(fulldstpath):
				subprocess.run(["gm", "convert", "-quality", "85", fullsrcpath, fulldstpath])
				ratio = getRatio(fullsrcpath, fulldstpath)
				print('convert: ', os.path.join(fullsrcpath), '->', fulldstpath, "{0:.2f}".format(ratio))
				if ratio >= 1.0:
					print('  keep original file')
					shutil.copy2(fullsrcpath, fulldstpath)
			else:
				print('skip: ', os.path.join(fullsrcpath), '->', fulldstpath)
		elif extension in ['.mov', '.mp4', '.wmv', '.mod', '.mpg', '.avi', '.mts', '.mkv']:
			fulldstpath = interdstpath + '.mkv'
			if not os.path.exists(fulldstpath):
				subprocess.run(["ffmpeg", "-y", "-i", fullsrcpath, "-c:v", "libx265", "-vf", "yadif=0:-1:0",  fulldstpath])
				ratio = getRatio(fullsrcpath, fulldstpath)
				print('ffmpeg: ', os.path.join(fullsrcpath), '->', fulldstpath, "{0:.2f}".format(ratio))
				#time.sleep(1)
			else:
				print('skip: ', os.path.join(fullsrcpath), '->', fulldstpath)
		elif extension in ['.zip', '.pdf', '.txt', '.sh', '.thm']:
			print('copy: ', os.path.join(fullsrcpath), '->', fulldstpath)
			subprocess.run(["cp", "-a", fullsrcpath, fulldstpath])
		else:
			print('unknown ', fullsrcpath)
		sys.stdout.flush()

