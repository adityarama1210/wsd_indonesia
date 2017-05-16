# import needed library here
import re, sys, nltk, gensim
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from sklearn import svm, tree, dummy
from sklearn.model_selection import cross_val_score, ShuffleSplit
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
		return result_arr

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

	def total_sum(self, counter_arr):
		res = 0
		for key in counter_arr:
			res += counter_arr[key]
		return float(res)

	def print_sentence_and_class(self):
		print "===<BEGIN>==="+ self.target_word + "===<BEGIN>==="
		for x in range(len(sentences)):
			print (self.sentences[x] + '||' + self.classes[x])
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

def produce_indo_sense_tagged_corpus(indo_original_sentences, english_tagged_sentences, dictionary, a3_file):
	for key in indo_original_sentences:
		indo_sentence = indo_original_sentences[key]
		en_tag_sentence = english_tagged_sentences[key]
		a3 = a3_file[key]
		output = ''
		for indo_word in indo_sentence.split(' '):
			sense_key = None
			if indo_word in dictionary:
				en_words = dictionary[indo_word]
				english_word = get_en_from_a3_by_indo_word(indo_word, a3)
				if english_word and english_word in en_words:
					# the pair from A3 file exist in the dictionary
					sense_key = get_sense_key_from_en_tag_sentence(en_words, en_tag_sentence)
			if sense_key:
				output = output + indo_word + '||' + sense_key + ' '
			else:
				output = output + indo_word + ' '
		print output




## end of processing


## some methods

def word_in_sentence_corner(sentence, word):
	regex = ' ' + word + '$|^' +  word + ' | ' + word + ' |^' + word + '$'
	m = re.search(regex, sentence)
	return m != None

def get_indo_sentences_and_classes(sentences, target_word, english_tagged_sentences, dictionary, a3_file):
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
			result_sentences.append(sentence_indo)
			result_classes.append(sense_key)
			index_for_sentence.append(index-1)
			# INDEX IS ARRAY INDEX WHICH START FORM ZERO
	return (result_sentences, result_classes, index_for_sentence)

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
#f_dictionary = 'enhanced_dictionary_new.txt'
#f_dictionary = 'enhanced_dictionary.txt'
f_dictionary = 'enhanced_dictionary_final.txt'
# dictionary
f_stopwords = 'stopwords.txt'
# stopword file
f_word_embedding_model = 'model_ignore/wordembed-single-lowcase'
# word embedding model
f_a3_file = 'Post-Process-A3/output_a3.txt'
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
			if sys.argv[3] == 'f1':
				# just bag of words
				bag_of_words = wsd.get_bag_of_words()
				features = wsd.get_features(bag_of_words)
			elif sys.argv[3] == 'f2a':
				# word embedding
				features = wsd.get_word_embedding_features(model)
			elif sys.argv[3] == 'f2b':
				# word embedding
				features = wsd.get_word_embedding_features_full_token(model)
			elif sys.argv[3] == 'f3':
				# pos tagging only
				features = wsd.get_pos_tag_features(f_id_postag, index_for_sentence)
			elif sys.argv[3] == 'f4':
				# pos tagging and bag of words
				f1 = wsd.get_pos_tag_features(f_id_postag, index_for_sentence)
				bag_of_words = wsd.get_bag_of_words()
				f2 = wsd.get_features(bag_of_words)
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
		produce_indo_sense_tagged_corpus(indo_original_sentences, english_tagged_sentences, dictionary, a3_file)




## script end here