# import needed library here
import re, sys, nltk, gensim, json
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from sklearn import svm, tree, dummy
from sklearn.model_selection import cross_val_score, ShuffleSplit
from nltk.corpus import wordnet as wn
from nltk.corpus.reader.wordnet import WordNetError
from collections import Counter

# the end of importing libraries

# All needed function

def remove_punctuation(line):
	return re.sub('[\'\"!\,\.\(\)\?\;\:]', '', line)

def is_punctuation(line):
	m = re.match('[\'\"!\,\.\(\)\?\;\:]', line)
	return m != None

# All needed function

# All needed class
class EnglishTagToken:

	def __init__(self, word_and_sense_key):
		temp = word_and_sense_key.split('||')
		self.word = temp[0]
		self.sense_key = temp[1]
	def get_word(self):
		return self.word
	def get_sense_key(self):
		return self.sense_key

class WSDIndonesia:
	def __init__(self, stopwords, sentences, classes, target_word):
		self.stopwords = stopwords
		# create stemmer
		factory = StemmerFactory()
		stemmer = factory.create_stemmer()
		#self.target_word = stemmer.stem(target_word.lower())
		self.target_word = target_word.lower()
		for x in range(len(sentences)):
			#sentences[x] = stemmer.stem(self.remove_punctuation(sentences[x].lower()))
			sentences[x] = self.remove_punctuation(sentences[x].lower())
		self.sentences = sentences
		self.classes = classes

	'''
	def __init__(self, stopwords, json_dict, classes, target_word):
		self.stopwords = stopwords
		self.json_dict = json_dict
		self.classes = classes
		self.target_word = target_word
	'''


	def zerolistmaker(self, n):
	    listofzeros = [0] * n
	    return listofzeros

	def get_top_words(self):
		temp_arr = []
		for sentence in self.sentences:
			arr = sentence.split(' ')
			for token in arr:
				if token != "." and target_word != token:
					temp_arr.append(token)
		temp_arr = Counter(temp_arr)
		result_arr = []
		# take top n
		for (word, count) in temp_arr.most_common(10):
			result_arr.append(word)
		return result_arr

	def get_bag_of_words(self):
		temp_arr = []
		for sentence in self.sentences:
			arr = sentence.split(' ')
			for index in range(len(arr)):
				word = arr[index]
				if word != ".":
					if word == self.target_word:
						# take the -2 -1 +1 +2 word
						if index-2 >= 0:
							temp_arr.append(arr[index-2])
						if index-1 >= 0:
							temp_arr.append(arr[index-1])
						if index+1 < len(arr):
							temp_arr.append(arr[index+1])
						if index+2 < len(arr):
							temp_arr.append(arr[index+2])
		temp_arr = Counter(temp_arr)
		result_arr = []
		for word in temp_arr.keys():
			result_arr.append(word)
		print sorted(result_arr)
		return result_arr

	def get_bag_of_words_feature_from_json(self):
		temp_arr = []
		for sentence_id in self.json_dict['sentences'].keys():
			sentence = self.json_dict['sentences'][sentence_id]
			for index in range(len(sentence['words'])):
				word_obj = sentence['words'][index]
				word = word_obj['word']
				if word == self.target_word:
					# take the -2 -1 +1 +2 word
					if index-2 >= 0:
						temp_arr.append(sentence['words'][index-2]['word'])
					if index-1 >= 0:
						temp_arr.append(sentence['words'][index-1]['word'])
					if index+1 < len(sentence['words']):
						temp_arr.append(sentence['words'][index+1]['word'])
					if index+2 < len(sentence['words']):
						temp_arr.append(sentence['words'][index+2]['word'])
		temp_arr = Counter(temp_arr)
		result_arr = []
		for word in temp_arr.keys():
			result_arr.append(word)
		
		# get the real features in one hot vector form

		print sorted(result_arr)

		x_features = []
		for sentence_id in self.json_dict['sentences'].keys():
			sentence = self.json_dict['sentences'][sentence_id]
			arr = self.zerolistmaker(len(result_arr))
			for x in range(len(result_arr)):
				# check if the sentence contain the words
				for index in range(len(sentence['words'])):
					word_obj = sentence['words'][index]
					word = word_obj['word']
					if word == result_arr[x]:
						arr[x] = 1
			x_features.append(arr)
		temp_arr, result_arr = None, None
		return x_features

	def get_pos_tag_features_from_json(self):
		temp_arr = [[],[],[]]
		# first for -1 pos tag, second for target word pos tag, and so on
		for sentence_id in self.json_dict['sentences'].keys():
			sentence = self.json_dict['sentences'][sentence_id]
			for index in range(len(sentence['words'])):
				word_obj = sentence['words'][index]
				word = word_obj['word']
				pos = word_obj['pos']
				if word == self.target_word:
					# take the -1 0 +1 pos tag
					if pos != '':
						temp_arr[1].append(pos)
					if index-1 >= 0 and sentence['words'][index-1]['pos'] != '':
						temp_arr[0].append(sentence['words'][index-1]['pos'])
					if index+1 < len(sentence['words']) and sentence['words'][index+1]['pos'] != '':
						temp_arr[2].append(sentence['words'][index+1]['pos'])
		
		temp_arr[0], temp_arr[1], temp_arr[2] = Counter(temp_arr[0]), Counter(temp_arr[1]), Counter(temp_arr[2])
		result_arr = [[],[],[]]
		for x in range(len(temp_arr)):
			for pos in temp_arr[x].keys():
				result_arr[x].append(pos)

		# get the real features in one hot vector form

		x_features = []
		for sentence_id in self.json_dict['sentences'].keys():
			sentence = self.json_dict['sentences'][sentence_id]
			arr_0 = self.zerolistmaker(len(result_arr[0]))
			arr_1 = self.zerolistmaker(len(result_arr[1]))
			arr_2 = self.zerolistmaker(len(result_arr[2]))
			for index in range(len(sentence['words'])):
				word_obj = sentence['words'][index]
				word = word_obj['word']
				pos = word_obj['pos']

				if word == self.target_word:
					if pos != '':
						# which position is this pos tag in the 2nd array of result?
						for x in range(len(result_arr[1])):
							if result_arr[1][x] == pos:
								arr_1[x] = 1
					if index-1 >= 0:
						if sentence['words'][index-1]['pos'] != '':
							for x in range(len(result_arr[0])):
								if result_arr[0][x] == sentence['words'][index-1]['pos']:
									arr_0[x] = 1
					if index+1 >= 0:
						if sentence['words'][index+1]['pos'] != '':
							for x in range(len(result_arr[2])):
								if result_arr[2][x] == sentence['words'][index+1]['pos']:
									arr_2[x] = 1
			x_features.append(arr_0 + arr_1 + arr_2)
		return x_features

	def get_max_length_json(self):
		tmp_max = 0
		for sentence_id in self.json_dict['sentences'].keys():
			sentence = self.json_dict['sentences'][sentence_id]
			if len(sentence['words']) > tmp_max:
				tmp_max = len(sentence['words'])
		return tmp_max

	def get_word_embedding_features_from_json(self, model):

		# get the maximum length first!
		max_length = self.get_max_length_json()
		x_features = []
		for sentence_id in self.json_dict['sentences'].keys():
			sentence = self.json_dict['sentences'][sentence_id]
			arr = []
			for x in range(max_length):
				if x >= 0 and x < len(sentence['words']):
					word_obj = sentence['words'][x]
					word = word_obj['word']
					if word in model:
						arr = arr + model[word].tolist()
					else:
						arr = arr + self.zerolistmaker(128)
				else:
					arr = arr + self.zerolistmaker(128)
			x_features.append(arr)

		return x_features

	def remove_punctuation(self, line):
		return re.sub('[\'\"!\,\.\(\)\?\;\:]', '', line)

	def get_features(self, top_words):
		x_features = []
		for sentence in sentences:
			arr = self.zerolistmaker(len(top_words))
			for x in range(len(top_words)):
				word = top_words[x]
				if ' '+word+' ' in sentence:
					# using boolean feature
					arr[x] = 1
			x_features.append(arr)
			print sentence
			print arr
			print '=================='
		return x_features

	def get_pos_tag_features(self, file, index_for_sentence):
		id_tag_sentences = []
		file_tag = open('Resources/'+file, 'r')
		temp_features = [[],[],[]]
		for line in file_tag:
			id_tag_sentences.append(line.strip())
		file_tag.close()

		for x in index_for_sentence:
			line = id_tag_sentences[x]
			line = line.strip().split(' ')
			for x in range(len(line)):
				token = line[x].split('_')
				if token[0].lower() == self.target_word:
					# take -1 word pos tag
					if x-1 >= 0:
						token_1 = line[x-1].split('_')
						temp_features[0].append(token_1[1])
					else:
						temp_features[0].append('')
					# take this word pos tag (target word)
					temp_features[1].append(token[1])
					# take the word + 1 pos tag
					if x+1 < len(line):
						token_2 = line[x+1].split('_')
						temp_features[2].append(token_2[1])
					else:
						temp_features[2].append('')
					break


		first = Counter(temp_features[0]).keys()
		second = Counter(temp_features[1]).keys()
		third = Counter(temp_features[2]).keys()
		final_features = []
		for x in range(len(temp_features[0])):
			(tag_1, tag_2, tag_3) = (temp_features[0][x], temp_features[1][x], temp_features[2][x])
			t_a = []
			for key in first:
				if tag_1 == key:
					t_a.append(1)
				else:
					t_a.append(0)
			for key in second:
				if tag_2 == key:
					t_a.append(1)
				else:
					t_a.append(0)
			for key in third:
				if tag_3 == key:
					t_a.append(1)
				else:
					t_a.append(0)
			final_features.append(t_a)

		return final_features


	def get_word_embedding_features(self, model):
		temp_sentences = []
		for sentence in self.sentences:
			#arr = self.zerolistmaker(len(model[self.target_word]) * 2)
			arr = []
			index_target_word = 0
			words = sentence.split()
			for index in range(len(words)):
				if words[index] == self.target_word:
					index_target_word = index
			if index_target_word-1 >= 0 and words[index_target_word-1] in model:
				# for -1 target word
				#arr[0:100] = model[words[index_target_word-1]].tolist()
				arr = arr + model[words[index_target_word-1]].tolist()
			else:
				arr = arr + self.zerolistmaker(128)
			if index_target_word-2 >= 0 and words[index_target_word-2] in model:
				# for -1 target word
				#arr[0:100] = model[words[index_target_word-1]].tolist()
				arr = arr + model[words[index_target_word-2]].tolist()
			else:
				arr = arr + self.zerolistmaker(128)
			if index_target_word-3 >= 0 and words[index_target_word-3] in model:
				# for -1 target word
				#arr[0:100] = model[words[index_target_word-1]].tolist()
				arr = arr + model[words[index_target_word-3]].tolist()
			else:
				arr = arr + self.zerolistmaker(128)
			if index_target_word+1 < len(words) and words[index_target_word+1] in model:
				#arr[100:] = model[words[index_target_word+1]].tolist()
				arr = arr + model[words[index_target_word+1]].tolist()
			else:
				arr = arr + self.zerolistmaker(128)
			if index_target_word+2 < len(words) and words[index_target_word+2] in model:
				# for -1 target word
				#arr[0:100] = model[words[index_target_word-1]].tolist()
				arr = arr + model[words[index_target_word+2]].tolist()
			else:
				arr = arr + self.zerolistmaker(128)
			if index_target_word+3 < len(words) and words[index_target_word+3] in model:
				# for -1 target word
				#arr[0:100] = model[words[index_target_word-1]].tolist()
				arr = arr + model[words[index_target_word+3]].tolist()
			else:
				arr = arr + self.zerolistmaker(128)
			temp_sentences.append(arr)
		return temp_sentences


	def get_word_embedding_features_full_token(self, model):
		max_length = 0
		for sentence in self.sentences:
			temp_length = len(sentence.split(' '))
			if temp_length >= max_length:
				max_length = temp_length
		features = []
		length_we_feature = len(model['apa'])
		for sentence in self.sentences:
			arr = []
			words = sentence.split(' ')
			for x in range(max_length):
				if x >= 0 and x < len(words):
					if words[x] in model:
						arr = arr + model[words[x]].tolist()
					else:
						arr = arr + self.zerolistmaker(length_we_feature)
				else:
					arr = arr + self.zerolistmaker(length_we_feature)
			features.append(arr)
		return features


	def concat_features(self, f, w_f):
		final_features = []
		for x in range(len(f)):
			final_features.append(f[x] + w_f[x])
		return final_features



	def remove_stopword(self):
		for index in range(len(self.sentences)):
			sentence = self.sentences[index]
			for stopword in self.stopwords:
				stopword = ' '+stopword+' '
				if stopword in sentence:
					# remove the stopword
					sentence = sentence.replace(stopword,' ')
			self.sentences[index] = sentence

	def remove_stopword_json(self):
		for sentence_id in self.json_dict['sentences'].keys():
			new_arr = []
			sentence = self.json_dict['sentences'][sentence_id]
			for word_obj in sentence['words']:
				if word_obj['word'] not in self.stopwords:
					# passed, this word could come through!
					new_arr.append({'word': word_obj['word'], 'pos': word_obj['pos'], 'sense_key': word_obj['sense_key']})
			self.json_dict['sentences'][sentence_id]['words'] = new_arr

	def total_sum(self, counter_arr):
		res = 0
		for key in counter_arr:
			res += counter_arr[key]
		return float(res)

	def print_sentence_and_class(self):
		print "===<BEGIN>==="+ self.target_word + "===<BEGIN>==="
		for x in range(len(sentences)):
			print (self.sentences[x] + '||' + self.classes[x])
		print "===<STATISTIC>===#Classes", len(Counter(self.classes))," With ", str(Counter(self.classes)), "===</STATISTIC>===" 
		print "===<END>===" + self.target_word +"===<END>==="

	def disambiguate(self, features):
		# initiate classifier
		clf = svm.SVC(kernel='linear')
		bf = dummy.DummyClassifier(strategy='most_frequent')
		# calculating the baseline
		arr = Counter(self.classes)
		baseline = float(arr.most_common(1)[0][1])/self.total_sum(arr)
		print "Disambiguation for:", self.target_word
		cv = ShuffleSplit(n_splits=3, test_size=0.3, random_state=0)
		scores = cross_val_score(clf, features, self.classes, cv=cv, scoring='f1_micro')
		print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))
		scores = cross_val_score(bf, features, self.classes, cv=cv, scoring='f1_micro')
		print("Baseline Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))
		print "With number of classes", len(list(set(self.classes)))
		print dict(Counter(self.classes))


# All needed class

## process the needed files

def get_list_en_tag(file):
	result = {}
	sentence_counter = 1
	file = open(file, 'r')
	for line in file:
		result[sentence_counter] = []
		line = line.strip()
		m = re.search('<sentence>(.*)</sentence>', line)
		tokens = m.group(1).split(' ')
		for token in tokens:
			if token:
				result[sentence_counter].append(EnglishTagToken(token))
		sentence_counter += 1
	file.close()
	return result

def get_list_id_original(file):
	result = {}
	sentence_counter = 1
	file = open(file, 'r')
	for line in file:
		result[sentence_counter] = None
		line = line.strip()
		result[sentence_counter] = line
		sentence_counter += 1
	file.close()
	return result

def get_from_a3_post_process(file):
	result = {}
	sentence_counter = 1
	file = open(file, 'r')
	for line in file:
		result[sentence_counter] = []
		line = line.strip().split('##')
		for token in line:
			m = re.search('<pair>(.*)\|\|(.*)</pair>', token)
			if m:
				result[sentence_counter].append((m.group(1), m.group(2)))
				# (english,indo) -> (eat,makan) atau (long,panjang), dll
		sentence_counter += 1

	file.close()
	return result

def get_en_from_a3_by_indo_word(indo, a3):
	# a3 in form of [(eat,makan),(long,panjang),(distance,jarak),...]
	for (en_w, id_w) in a3:
		if indo == id_w:
			return en_w
	return None

def get_indo_from_a3_by_en_word(en_word, a3):
	for (en_w, id_w) in a3:
		if en_w == id_w:
			return en_w
	return None



def get_stopwords(file):
	result = []
	file = open(file, 'r')
	for line in file:
		line = line.strip()
		result.append(line)
	file.close()
	return result

def get_dictionary(file):
	dictionary = {}
	file = open(file, 'r')
	for line in file:
		line = line.strip().split('\t')
		word_indo = line[0]
		if word_indo not in dictionary:
			# add to the dictionary
			dictionary[word_indo] = []
		tokens = line[1].split(' ')
		for word_en in tokens:
			word_en = word_en.split('||')[0]
			if word_en not in dictionary[word_indo]:
				dictionary[word_indo].append(word_en)
	return dictionary

def reading_testing_file(filename):
	result = []
	file = open(filename, 'r')
	for line in file:
		line = line.strip()
		result.append(line)
	file.close()
	return result

def get_sense_key_from_en_tag_sentence(en_words_from_dict, en_tag_sentence):
	sense_key = None
	for english_tag_token in en_tag_sentence:
		if english_tag_token.word in en_words_from_dict:
			# return the sense
			sense_key = english_tag_token.sense_key
	return sense_key

def get_similar_sense_key(dict_of_sense_key, sense_key, word):
	if sense_key not in dict_of_sense_key[word]:
		dict_of_sense_key[word][sense_key] = 1
		# add new sense key to the dictionary
	try:
		synset_sense_key = wn.lemma_from_key(sense_key).synset()
	except WordNetError:
		synset_sense_key = None
	if synset_sense_key:
		for key in dict_of_sense_key[word].keys():
			try:
				synset = wn.lemma_from_key(key).synset()
			except WordNetError:
				synset = None
			if synset and synset_sense_key:
				if synset_sense_key.path_similarity(synset) > 0.5:
					sense_key = key
					# considered as the same meaning
	return (dict_of_sense_key, sense_key)


def get_json_of_postag(f_postag):
	f = open(f_postag, 'r')
	json_s = {
		'sentences': {}
	}
	sentence_number = 1
	for line in f:
		json_s['sentences'][sentence_number] = { 'words' : [] }
		line = line.strip().rstrip(' ._Z').split(' ')
		for token in line:
			token = token.split('_')
			word = remove_punctuation(token[0].lower())
			if word and '-rrb-' not in word and '-lrb-' not in word and word != "``" and word != "''" and word != '\'' and word != '`' and '`' not in word:
				if len(token) > 1:
					postag = token[1]
				else:
					postag = ''
				json_s['sentences'][sentence_number]['words'].append({ 'word': word, 'pos': postag, 'sense_key': '' })
		sentence_number += 1
	f.close()
	return json_s

#def produce_indo_sense_tagged_corpus(indo_original_sentences, english_tagged_sentences, dictionary, a3_file):

'''
	for key in indo_original_sentences:
		indo_sentence = indo_original_sentences[key]
		en_tag_sentence = english_tagged_sentences[key]
		a3 = a3_file[key]
		output = ''
		for indo_word in indo_sentence.split(' '):
			if indo_word not in dict_of_sense_key:
				dict_of_sense_key[indo_word] = {}
			sense_key = None
			if indo_word in dictionary:
				en_words = dictionary[indo_word]
				english_word = get_en_from_a3_by_indo_word(indo_word, a3)
				if english_word and english_word in en_words:
					# the pair from A3 file exist in the dictionary
					sense_key = get_sense_key_from_en_tag_sentence(en_words, en_tag_sentence)
			if sense_key:
				dict_of_sense_key, sense_key = get_similar_sense_key(dict_of_sense_key, sense_key, indo_word)
				output = output + indo_word + '||' + sense_key + ' '
			else:
				output = output + indo_word + ' '
		print output
	'''

def allowed_word(word):
	m = re.search('^\'+|^"+|^`+|^:+|^;+', word)
	return m == None

def produce_indo_sense_tagged_corpus(json_s, english_tagged_sentences, dictionary, a3_file):
	dict_of_sense_key = {}
	for sentence_number in json_s['sentences'].keys():
		sentence = json_s['sentences'][sentence_number]
		en_tag_sentence = english_tagged_sentences[sentence_number]
		a3 = a3_file[sentence_number]
		for index in range(len(sentence['words'])):
			token = sentence['words'][index]
			indo_word = token['word']
			pos = token['pos']
			sense_key = token['sense_key']
			if allowed_word(indo_word):
				if indo_word not in dict_of_sense_key:
					dict_of_sense_key[indo_word] = {}
				sense_key = None
				if indo_word in dictionary:
					en_words = dictionary[indo_word]
					english_word = get_en_from_a3_by_indo_word(indo_word, a3)
					if english_word and english_word in en_words:
						# the pair from A3 file exist in the dictionary
						sense_key = get_sense_key_from_en_tag_sentence(en_words, en_tag_sentence)
				if sense_key:
					dict_of_sense_key, sense_key = get_similar_sense_key(dict_of_sense_key, sense_key, indo_word)
					json_s['sentences'][sentence_number]['words'][index]['sense_key'] = sense_key
	return json_s


## end of processing


## some methods

def word_in_sentence_corner(sentence, word):
	regex = ' ' + word + '$|^' +  word + ' | ' + word + ' |^' + word + '$'
	m = re.search(regex, sentence)
	return m != None

def get_indo_sentences_and_classes(sentences, target_word, english_tagged_sentences, dictionary, a3_file):
	dict_of_sense_key = {target_word: {}}
	# for sense optimization
	index_for_sentence = []
	en_words = dictionary[target_word]
	result_sentences, result_classes = [], []
	for index in range(len(sentences)):
		index = index+1
		sentence_indo = sentences[index]
		en_tag_sentence = english_tagged_sentences[index]
		# check on the A3 file, what is the pair word in english?
		a3 = a3_file[index]
		english_word = get_en_from_a3_by_indo_word(target_word, a3)
		sense_key = None
		if english_word and english_word in en_words:
			sense_key = get_sense_key_from_en_tag_sentence(en_words, en_tag_sentence)
			#for english_tag_token in en_tag_sentence:
				#if english_tag_token.word in en_words:
				#	# correct translation found in the english tagged sentence (with tag)
				#	sense_key = english_tag_token.sense_key
		if (word_in_sentence_corner(sentence_indo, target_word)) and sense_key:
			dict_of_sense_key, sense_key = get_similar_sense_key(dict_of_sense_key, sense_key, target_word)
			result_sentences.append(sentence_indo)
			result_classes.append(sense_key)
			index_for_sentence.append(index-1)
			# INDEX IS ARRAY INDEX WHICH START FORM ZERO
	return (result_sentences, result_classes, index_for_sentence)

def get_sentence_and_classes_from_json(json_dict, target_word):
	new_json_dict = {'sentences': {}}
	classes = []
	for sentence_id in json_dict['sentences'].keys():
		sentence = json_dict['sentences'][sentence_id]
		for word_obj in sentence['words']:
			word = word_obj['word']
			sense_key = word_obj['sense_key']
			if word == target_word and sense_key != '':
				# get the current word sense key and sentence
				classes.append(sense_key)
				new_json_dict['sentences'][sentence_id] = sentence
				break
	return (new_json_dict, classes)


def get_indo_sentences_f_postag(file):
	f = open('Resources/'+file, 'r')
	sentences = []
	for line in f:
		line = line.strip().split(' ')
		sentence = ''
		for token in line:
			token = token.split('_')
			word = token[0].lower()
			if (not is_punctuation(word)):
				sentence = sentence + word + ' '
		sentences.append(sentence.strip())
	f.close()
	return sentences

def get_json_corpus(json_file):
	with open(json_file) as data_file:    
    		data = json.load(data_file)
	return data

## some methods

## script begin here

# for resource file

## list of files

f_en_tag_min = 'en_tag_corpus_ignore_new.min.xml'
# en tag xml file
f_id_original = 'original_id_clean.txt'
# sentence id original
f_id_postag = 'original_id_clean_postag.txt'
# sentence id pos tag
#f_dictionary = 'enhanced_dictionary_new.txt' # this is the bi-direectional dictionary
#f_dictionary = 'enhanced_dictionary.txt'
f_dictionary = 'enhanced_dictionary_final.txt' # this is the crawling dictionary
# dictionary
f_stopwords = 'stopwords.txt'
# stopword file
f_word_embedding_model = 'model_ignore/wordembed-single-lowcase'
# word embedding model
f_a3_file = 'Post-Process-A3/output_a3.txt'
f_json_corpus = 'Resources/indonesia_sense_tagged_corpus.json'
#json_file
## the end list of files



english_tagged_sentences = get_list_en_tag('Resources/'+f_en_tag_min)
indo_original_sentences = get_list_id_original('Resources/'+f_id_original)
dictionary = get_dictionary('Resources/'+f_dictionary)
stopwords = get_stopwords('Resources/'+f_stopwords)
a3_file = get_from_a3_post_process(f_a3_file)

if len(sys.argv) > 1:
	# if we want to add some words to be tested (Testing environment)
	_type = sys.argv[1]
	# python wsd.py <_type>
	if _type == "testing":
		# python wsd.py testing <testing_file> <feature>
		if len(sys.argv) != 4:
			print "python wsd.py testing <testing_file> <f1|f2a|f2b|f3|f4>"
			exit()
		if len(sys.argv) == 4 and (sys.argv[3] == 'f2a' or sys.argv[3] == 'f2b'):
			# load word embedding model for efficiency
			model = gensim.models.Word2Vec.load(f_word_embedding_model)

		testing_file = sys.argv[2]
		testing_words = reading_testing_file(testing_file)
		for word in testing_words:
			(sentences, classes, index_for_sentence) = get_indo_sentences_and_classes(indo_original_sentences, word, english_tagged_sentences, dictionary, a3_file)
			wsd = WSDIndonesia(stopwords, sentences, classes, word)
			wsd.remove_stopword()
			'''
			json_dict = get_json_corpus(f_json_corpus)
			(json_dict, classes) = get_sentence_and_classes_from_json(json_dict, word)
			wsd = WSDIndonesia(stopwords, json_dict, classes, word)
			wsd.remove_stopword_json()
			'''
			if sys.argv[3] == 'f1':
				# just bag of words
				bag_of_words = wsd.get_bag_of_words()
				features = wsd.get_features(bag_of_words)
				#features = wsd.get_bag_of_words_feature_from_json()
			elif sys.argv[3] == 'f2a':
				# word embedding
				features = wsd.get_word_embedding_features(model)
				#features = wsd.get_word_embedding_features_from_json(model)
			elif sys.argv[3] == 'f2b':
				# word embedding
				features = wsd.get_word_embedding_features_full_token(model)
				#features = wsd.get_word_embedding_features_from_json(model)
			elif sys.argv[3] == 'f3':
				# pos tagging only
				features = wsd.get_pos_tag_features(f_id_postag, index_for_sentence)
				#features = wsd.get_pos_tag_features_from_json()
			elif sys.argv[3] == 'f4':
				# pos tagging and bag of words
				f1 = wsd.get_pos_tag_features(f_id_postag, index_for_sentence)
				#f1 = wsd.get_pos_tag_features_from_json()
				bag_of_words = wsd.get_bag_of_words()
				f2 = wsd.get_features(bag_of_words)
				#f2 = wsd.get_bag_of_words_feature_from_json()
				features = wsd.concat_features(f1, f2)
			else:
				print 'Feature doesn\'t exist!'
				exit()
			wsd.disambiguate(features)
	elif _type == "sense_transfering":
		# python wsd.py sense_transfering <testing_file>
		testing_file = sys.argv[2]
		testing_words = reading_testing_file(testing_file)
		for word in testing_words:
			(sentences, classes, index_for_sentence) = get_indo_sentences_and_classes(indo_original_sentences, word, english_tagged_sentences, dictionary, a3_file)
			wsd = WSDIndonesia(stopwords, sentences, classes, word)
			wsd.print_sentence_and_class()

	elif _type == "produce_tagged_corpus":
		# python wsd.py produce_tagged_corpus
		json_s = get_json_of_postag('Resources/'+f_id_postag)
		json_s = produce_indo_sense_tagged_corpus(json_s, english_tagged_sentences, dictionary, a3_file)
		print json.dumps(json_s, indent=4, separators=(',',': '))

## script end here