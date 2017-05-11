import re

a3_file = '../Resources/A3_file'

def remove_punctuation(line):
	return re.sub('[\'\"!\,\.\(\)\?\;\:]', '', line)

def to_i(s):
	return int(s)

f = open(a3_file, 'r')

state = 0
indo_words = None

for line in f:
	line = line.strip()
	if "# Sentence pair " in line:
		state = 1
	else:
		if state == 1:
			# take indo
			indo_words = line.lower().split(' ')
			state = 2 
		elif state == 2:
			# take english
			english_tokens = line.split('})')
			output = ''
			for token in english_tokens:
				# in format of ' I ({ 1 '
				token = token.strip().split('({')
				en_word = remove_punctuation(token[0].strip()).lower()
				numbers = None
				if len(token) > 1:
					if token[1].strip() != '':
						numbers = map(to_i, token[1].strip().split(' '))
				if numbers and len(numbers) > 0:
					corresponding_indo_words = ''
					for number in numbers:
						if number-1 < len(indo_words):
							corresponding_indo_words = corresponding_indo_words + indo_words[number-1] + ' '
					corresponding_indo_words = remove_punctuation(corresponding_indo_words.strip())
					if corresponding_indo_words:
						# this is the word
						output = output + '<pair>'+en_word+'||'+corresponding_indo_words+'</pair>##'
			output = output.rstrip('##')
			print output
			# print the sentence
			state = 0

f.close()