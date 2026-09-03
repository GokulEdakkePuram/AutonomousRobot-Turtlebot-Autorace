#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ast
import sys
from pathlib import Path

#set constants
angle_min= -1.57079637051
angle_max= 1.53938043118
angle_incr = 0.0314159281552

'''
TODO: this is simple just return the length of a given list.
'''
def get_length(scan_data):
	length = len(scan_data)
	return length

'''
TODO: find the index of the closest point in the scan_data
'''
def get_index_of_closest_point(scan_data):
	sort_scan = sorted(scan_data)
	for val in sort_scan:
		if val == 0.0:
			continue
		else:
			break
	ind = scan_data.index(val)
	return ind

'''
TODO: calculate the angle in rad for the closest point in scan_data
'''
def get_angle_of_closest_point(scan_data):
	index = get_index_of_closest_point(scan_data)
	loc_ang = index * 0.03
	tot_ang = 1.57 - loc_ang
	return tot_ang


def get_laserdata(path):
	file = open(path, "r")
	laserdata_raw = file.read()
	laserdata = ast.literal_eval(laserdata_raw)

	return laserdata


if __name__ == "__main__":

	#what is wrong with the print statement below? The print should look like this in your console:
	'''
	####################
	Python exercise
	####################
	'''

	#import ipdb; ipdb.set_trace()

	#read raw laser data
	#default to the recorded scan shipped with the repo, or take a path on the command line
	default_path = Path(__file__).resolve().parents[2] / "stage_0" / "laser-testdata_1"
	scan_data = get_laserdata(sys.argv[1] if len(sys.argv) > 1 else default_path)
	
	#import ipdb; ipdb.set_trace()

	#print length of scan_data
	print("Length of scan data: {0}".format(get_length(scan_data)))

	#print index of closest point
	print("Index of closest point: {0}".format(get_index_of_closest_point(scan_data)))

	#print angle of closest point
	print("Angle of closest point: {0}".format(get_angle_of_closest_point(scan_data)))
