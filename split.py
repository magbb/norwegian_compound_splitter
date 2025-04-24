# Magnus Breder Birkenes 2023
# Inspired by Koehn and Knight 2023: https://aclanthology.org/E03-1076.pdf

import sys
import numpy as np
from operator import itemgetter
import requests
import json

def geo_mean(iterable):
    a = np.array(iterable)
    return a.prod()**(1.0/len(a))

def ngram_lookup(word):
	try:
		url = "https://api.nb.no/dhlab/nb_ngram/ngram/query?terms=%s&lang=nor&case_sens=1&freq=rel&corpus=bok" % (word)
		r = requests.get(url)
		content = r.content
		json_content = json.loads(content)

		total = 0

		for element in json_content[0]["values"]:
			total += element["f"]
	except:
		total = None

	return total

try:
	word = sys.argv[1]
except:
	print("Norwegian compound splitter: Enter a word")
	sys.exit(1)

min_length = 2

ignore_prefixes = ['be', 'for', "av", "på", "med"]
ignore_suffixes = ['else', 'ing', 'ning', 'en', 'et', 'ge', 'le', 'la']
compound_interfix = ["s", "e"]

def check_suffix(word):
	for suffix in ignore_suffixes:
		if word == suffix:
			return True
	return False

def check_prefix(word):
	for prefix in ignore_prefixes:
		if word == prefix:
			return True
	return False

def split_into_two(word):
	candidates = []
	word_length = len(word)
	max_length = word_length - min_length

	if word_length >= (min_length * 2):
		# add the fullform itself as a candiate
		word_freq = ngram_lookup(word)

		if word_freq:
			candidate = [word,None,word_freq,None,geo_mean([word_freq])]
			candidates.append(candidate)
			print(word, candidate)

		# if fullform ends with a potential compound interfix, include the variant without the interfix
		if word.endswith('e') or word.endswith('s'):
			# add the fullform itself as a candiate
			word_freq = ngram_lookup(word[:-1])

			if word_freq:
				candidate = [word,None,word_freq,None,geo_mean([word_freq])]
				candidates.append(candidate)
				print(word, candidate)

		for i in range(min_length, max_length+1):
			candidate = []

			p1 = word[:i]
			p2 = word[i:]

			# skip certain prefixes and suffixes
			if check_prefix(p1) == True:
				continue

			if check_suffix(p2) == True:
				continue

			# lookup each form
			p1_freq = ngram_lookup(p1)
			p2_freq = ngram_lookup(p2)

			if p1_freq and p2_freq:
				candidate = [p1, p2, p1_freq, p2_freq, geo_mean([p1_freq, p2_freq])]
				candidates.append(candidate)
			#else:
				#print(p1, p2, "not a candidate split")

			print(p1, p2, candidate)

		sorted_candidates = sorted(candidates, key=itemgetter(4), reverse=True)
		return (sorted_candidates[0][0], sorted_candidates[0][1])
	else:
		return None

# return first split
print("First iteration...")
splits = split_into_two(word)
print("Found:", splits)

# split each part again (if split is found)
if splits:
	if splits[1] != None:
		print("Second iteration")
		splits_1 = split_into_two(splits[0])
		splits_2 = split_into_two(splits[1])

		if splits_1 and splits_2:
			print(splits_1, splits_2)
		elif splits_1:
			print(splits_1, splits[1])
		elif splits_2:
			print(splits[0], splits_2)
		else:
			print(splits)
	else:
		print(word)
else:
	print(word)
