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
		self.target_word = target_word.lower()
		for x in range(len(sentences)):
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

	def get_pos_tag_features(self, file):
		file_tag = open(file.replace('.txt','_tag.txt'), 'r')
		temp_features = [[],[],[]]
		for line in file_tag:
			line = line.strip().split(' ')
			for x in range(len(line)):
				token = line[x].split('_')
				if token[0] == self.target_word:
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
		file_tag.close()
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


	def get_word_embedding_features(self):
		fname = '../word_embed_model_ignore/wordembed-single-lowcase'
		model = gensim.models.Word2Vec.load(fname)
		#temp_sentences = []
		#for sentence in self.sentences:
		#	temp_sentences.append(sentence.strip().split())
		#model = gensim.models.Word2Vec(temp_sentences, min_count=1)
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


	def get_word_embedding_features_full_token(self):
		fname = '../word_embed_model_ignore/wordembed-single-lowcase'
		model = gensim.models.Word2Vec.load(fname)
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


	def concat_features_and_word_embedding(self, f, w_f):
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


# Load and process some needed file #

## list of files

f_en_tag_min = 'en_tag_corpus_ignore_new.min.xml'
f_id_original = 'original_id_clean.txt'
f_id_postag = 'original_id_clean_postag.txt'
f_dictionary = 'enhanced_crawl.txt'

## the end list of files

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

## end of processing


## script begin here

english_tagged_sentences = get_list_en_tag('Resources/'+f_en_tag_min)
indo_original_sentences = get_list_id_original('Resources/'+f_id_original)
dictionary = get_dictionary('Resources/'+f_dictionary)

if len(sys.argv) > 1:
	# if we want to add some words to be tested (Testing environment)
	testing_file = sys.argv[1]
	testing_words = reading_testing_file(testing_file)
	print testing_words

## script end here