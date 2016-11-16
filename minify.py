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
#
# Find file types:
# find . -type f -name "*.*" | awk -F. '!a[$NF]++{print $NF}'

# Changelog
# 2016/11/16
# Refactored to a proper module.
# Add a jpeg quality parameter.
# Compare dates of src and dst file. If src is newer, regenerate minified file.
# Fix files and folder permissions.

import sys
import os
import time
import subprocess
import shutil
from os.path import join, normpath

class Minifier:
	def __init__(self):
		self.base = 'photos_originals'
		self.newbase = 'photos_minified'
		self.quality = "85"

	def setParams(self, argv):
		if len(argv) >= 2:
			self.base = argv[1]

		if len(argv) >= 3:
		        self.newbase = argv[2]

		if len(argv) >= 4:
			self.quality = argv[3]

	def getRatio(self, src, dst):
		try:
			srcsize = os.stat(src).st_size
			dstsize = os.stat(dst).st_size
		except BaseException as err:
			dstsize = 0
			print('error: ', src, '->', dst, ' - ', err)
			#pass
		ratio = dstsize / srcsize
		return ratio

	def isNewer(self, src, dst):
		try:
			src_mtime = os.stat(src).st_mtime
			dst_mtime = os.stat(dst).st_mtime
			if src_mtime > dst_mtime:
				return True
			return False
		except BaseException as err:
			# dst may not exist, so return True
			return True
		return False

	def run(self):
		print("Working directory: ", os.getcwd())
		print("Source: ", self.base)
		print("Destination: ", self.newbase)
		print("Quality: ", self.quality)

		print('Proceed? ')
		res = input()
		if res != 'y':
		        sys.exit()

		os.chdir(self.base)

		if not os.path.isdir(self.newbase):
			os.mkdir(self.newbase)

		for root, dirs, files in os.walk('.'):
			for dir in dirs:
				srcdir = normpath(join(root, dir))
				dstdir = normpath(join(self.newbase, srcdir))
				print('mkdir: ', join(self.base, srcdir), '->', dstdir)
				try:
					os.chmod(srcdir, 0o775)
					os.mkdir(dstdir)
				except:
					pass

			for file in files:
				srcpath = normpath(join(root, file))
				try:
					os.chmod(srcpath, 0o664)
				except:
					pass
				basefile, extension = os.path.splitext(file)
				interdstpath = normpath(join(self.newbase, root, basefile))
				dstpath = interdstpath + extension
				extension = extension.lower()
				fullsrcpath = join(self.base, srcpath)
				if basefile.startswith('.'):
					print('dot file: ', fullsrcpath)
					continue
				if extension in ['.jpg', '.jpeg', '.bmp', '.png', '.cr2']:
					dstpath = normpath(interdstpath + '.jpg')
					if self.isNewer(srcpath, dstpath):
						subprocess.run(["gm", "convert", "-quality", self.quality, srcpath, dstpath])
						ratio = self.getRatio(srcpath, dstpath)
						print('convert: ', fullsrcpath, '->', dstpath, "{0:.2f}".format(ratio))
						if ratio >= 1.0:
							print('  keep original file')
							shutil.copy2(srcpath, dstpath)
					else:
						print('skip: ', fullsrcpath, '->', dstpath)
				elif extension in ['.mov', '.mp4', '.wmv', '.mod', '.mpg', '.avi', '.mts', '.mkv']:
					dstpath = normpath(interdstpath + '.mkv')
					if self.isNewer(srcpath, dstpath):
						subprocess.run(["ffmpeg", "-y", "-i", srcpath, "-c:v", "libx265", "-vf", "yadif=0:-1:0", dstpath])
						ratio = self.getRatio(srcpath, dstpath)
						print('ffmpeg: ', fullsrcpath, '->', dstpath, "{0:.2f}".format(ratio))
						if ratio >= 1.0:
							print('  keep original file')
							shutil.copy2(srcpath, dstpath)
						#time.sleep(1)
					else:
						print('skip: ', fullsrcpath, '->', dstpath)
				elif extension in ['.zip', '.pdf', '.txt', '.sh', '.thm']:
					print('copy: ', fullsrcpath, '->', dstpath)
					#subprocess.run(["cp", "-a", srcpath, dstpath])
					shutil.copy2(srcpath, dstpath)
				else:
					print('unknown: ', fullsrcpath)
				sys.stdout.flush()

if __name__ == '__main__':
	print('Picture and video minification script')
	minifier = Minifier()
	minifier.setParams(sys.argv)
	minifier.run()

