#!/bin/python3

import os
import sys

from contextlib import closing
import struct

IMAGE_MAGIC = 0x31524448 # 'HDR1'
PART_MAGIC = 0xFFFFFFFF

def XQImage_extract(image_path, output_dir):
	with closing(open(image_path, 'rb')) as image_file:
		magic, size, crc32, type, platform = struct.unpack(
			'<IIIHH',
			image_file.read(struct.calcsize('<IIIHH'))
		)

		if magic != IMAGE_MAGIC:
			raise Exception("magic incorrent: 0x%08X != 0x%08X" % (magic, IMAGE_MAGIC))

		if type != 0 and type != 2:
			raise Exception("Unsupport type: %d" % type)

		# TODO: Check crc32

		print("Image: %s" % image_path)
		print("Type: %d" % type)
		print("target platform: %d" % platform)

		offsets = struct.unpack(
			'<4I',
			image_file.read(struct.calcsize('<4I'))
		)

		os.mkdir(output_dir)
		print("Parts:")
		for off in offsets:
			if off != 0:
				image_file.seek(off, os.SEEK_SET)
				_, magic, size, _, name = struct.unpack(
					'<IIII24s',
					image_file.read(struct.calcsize('<IIII24s'))
				)
				name = name.decode('UTF-8').rstrip('\0')

				if magic != PART_MAGIC:
					raise Exception("magic incorrent: 0x%08X != 0x%08X" % (magic, PART_MAGIC))

				print("  - %s" % name)

				with closing(open(output_dir + '/' + name, 'wb')) as output:
					output.write(image_file.read(size))

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print("Usage:")
		print('  ' + sys.argv[0] + ' <image path> <output dir>')
		exit(1)

	XQImage_extract(sys.argv[1], sys.argv[2])
