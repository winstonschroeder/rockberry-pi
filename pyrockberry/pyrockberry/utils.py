#!/usr/bin/env python3

import json

def print_dict_as_json(dict):
	print (json.dumps(dict, sort_keys=True, indent=4))

def update_list(keep_list, new_list, update_keeplist = True):
	""" compare two lists and delete, add or replaced changes items. """
	exist_list = []
	add_list = new_list
	remove_list = keep_list
	for i in keep_list:
		for j in new_list:
			if (i==j):
				exist_list.append((i,j))
	## colltect items that keep_list contains, but new_list doesn't contain.
	# Those shall be removed.
	for i in new_list:
		for j in remove_list:
			if (i==j):
				remove_list.remove(j)
	## collect items that new_list contains, but keep_list is missing:
	for i in keep_list:
		for j in add_list:
			if (i==j):
				add_list.remove(j)
				
	if (update_keeplist):
		for j in remove_list:
			for i in keep_list:
				if (i==j):
					keep_list.remove(i)
		for i in add_list:
			keep_list.append(i)
	return (exist_list, add_list, remove_list)
				