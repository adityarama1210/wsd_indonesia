# input files are:
'''
1. Output 200 original Giza
2. Dictionary from bi-directional
2. Dictionary from crawling
'''
import re

f_giza = '200_testing_giza.txt'
f_crawling_dict = '../Resources/enhanced_dictionary_final.txt'
f_bidirectional_dict = '../Resources/enhanced_dictionary_new.txt'

def get_dictionary_from_file(dictionary_file):
	dictionary = {}
	file = open(dictionary_file, 'r')
	for line in file:
		line = line.strip().split('\t')
		word_id, tokens = line[0], line[1].split(' ')
		if word_id not in dictionary:
			dictionary[word_id] = {}
		for token in tokens:
			tmp = token.split('||')
			word_en, occurence = tmp[0], tmp[1]
			if word_en not in dictionary[word_id]:
				dictionary[word_id][word_en] = 1
	file.close()
	return dictionary


class ObjWord:
	def __init__(self, word, index):
		self.word = word
		self.index = index

def clean_indexes(indexes):
	# 1 2 3 
	result = []
	indexes = indexes.split(' ')
	for index in indexes:
		if index != '' and re.search('[0-9]+', index):
			result.append(index)
	return result

dictionary_crawling = get_dictionary_from_file(f_crawling_dict)
dictionary_bidirectional = get_dictionary_from_file(f_bidirectional_dict)

indo_sentence = None
obj_words = []
file = open(f_giza, 'r')
for line in file:
	line = line.strip()
	'''
	Sentence pair #1
	Semua pemangku kepentingan harus berperan dalam upaya ini termasuk pemda
	NULL ({ 6 8 }) All ({ 1 }) stakeholders ({ 2 3 7 }) including ({ 9 }) the ({ }) regional ({ }) governments ({ 10 }) should ({ 4 }) play ({ }) their ({ }) role ({ 5 })
	'''
	if "Sentence pair #" in line:
		state = 1 
		# state == 1 is indonesian
		continue
	elif state == 1:
		indo_sentence = line.split(' ')
		state = 2
	elif state == 2:
		tmp = line.split('})')
		for token in tmp:
			#  All ({ 1 
			token = token.strip().split('({')
			if token != ['']:
				word = token[0].strip()
				indexes = token[1].strip()
				indexes = clean_indexes(indexes)
				_str = _str + word + ' ({' + str(indexes) + '})' +' '
				obj_words.append(ObjWord(word, indexes))
		# obj_words is now containing list of word and their corresponding indexes
		state = 0
file.close()