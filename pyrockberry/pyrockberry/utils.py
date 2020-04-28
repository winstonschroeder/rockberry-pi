#!/usr/bin/env python3

import json

def print_dict_as_json(dict):
	print (json.dumps(dict, sort_keys=True, indent=4))
