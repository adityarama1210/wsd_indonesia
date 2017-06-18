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
f_out_bidirectional = '200_testing_crawling.txt'
f_out_crawling = '200_testing_bidirectional.txt'

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

def modify_obj_word_based_on_dictionary(dictionary, objword, list_of_indo_words):
	new_obj_word = ObjWord(objword.word, objword.index)
	if new_obj_word.word == 'NULL':
		return new_obj_word
	if new_obj_word.word in dictionary:
		word_id_dict = dictionary[new_obj_word.word]
	else:
		# not available in dictionary, then return it
		return new_obj_word
	indexes = new_obj_word.index
	if indexes:
		new_indexes = []
		# the case should be
		# word is available in the dictionary, and the numbers inside of it are correct
		for index in indexes:
			if index < len(list_of_indo_words):
				index = int(index)
				word_id = list_of_indo_words[index]
				if word_id in word_id_dict:
					new_indexes.append(str(index))
		new_obj_word.index = new_indexes
	return new_obj_word

def get_printed_obj_words(obj_words):
	str_result = ''
	for obj_word in obj_words:
		word = obj_word.word
		indexes = obj_word.index
		str_result = str_result + word + ' ({ '
		for index in indexes:
			str_result = str_result + str(index) + ' '
		str_result = str_result + '}) '
	str_result = str_result.strip()
	return str_result

def print_out_sentence(file, sentence_number, indo_sentence, obj_words):
	file.write('Sentence pair #'+ str(sentence_number) +'\n')
	file.write(indo_sentences + '\n')
	file.write(get_printed_obj_words(obj_words) + '\n')


dictionary_crawling = get_dictionary_from_file(f_crawling_dict)
dictionary_bidirectional = get_dictionary_from_file(f_bidirectional_dict)

indo_sentence = None
indo_sentences = None
obj_words_bidirectional, obj_words_crawling = [], []
file = open(f_giza, 'r')
number = 0

out_crawling = open(f_out_crawling, 'w')
out_bidirectional = open(f_out_bidirectional, 'w')

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
		number += 1
		continue
	elif state == 1:
		indo_sentence = line.split(' ')
		indo_sentences = line
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
				objword = ObjWord(word, indexes)
				objword_bidirectional = modify_obj_word_based_on_dictionary(dictionary_bidirectional, objword, indo_sentence)
				obj_words_bidirectional.append(objword_bidirectional)
				objword_crawling = modify_obj_word_based_on_dictionary(dictionary_crawling, objword, indo_sentence)
				obj_words_crawling.append(objword_crawling)
		# obj_words is now containing list of word and their corresponding indexes
		# print the sentence pair and the indonesian file with the english aligned version
		print_out_sentence(out_crawling, number, indo_sentences, obj_words_crawling)
		print_out_sentence(out_bidirectional, number, indo_sentences, obj_words_bidirectional)
		obj_words_bidirectional, obj_words_crawling = [], []
		state = 0

file.close()
out_crawling.close()
out_bidirectional.close()