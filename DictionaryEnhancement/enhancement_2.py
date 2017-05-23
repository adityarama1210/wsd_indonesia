def contains_same_translation(_dict1, _dict2):
	for key in _dict1.keys():
		if key in _dict2:
			return True
	return False



f = open('dictionary_final_crawl.txt', 'r')

_dict = {}

for line in f:
	line = line.strip().split('\t')
	word_indo = line[0]
	if word_indo not in _dict:
		_dict[word_indo] = {}
		for token in line[1].split(' '):
			word_en = token.split('||')[0]
			count = token.split('||')[1]
			if word_en not in _dict[word_indo]:
				_dict[word_indo][word_en] = count
			else:
				_dict[word_indo][word_en] += count

f.close()


for indo_word in _dict.keys():
	if len(indo_word.split(' ')) > 1:
		# cek apakah untuk setiap kata di dalam indo_word mempunyai pasangan tsb
		en_words = _dict[indo_word]
		indo_words = indo_word.split(' ')
		false = False
		for word in indo_words:
			if word in en_words or (word in _dict and contains_same_translation(_dict[word], en_words)):
				false = True
		if false:
			# this multiword will be deleted
			_dict[indo_word] = None
			_dict.pop(indo_word, None)
	if len(indo_word.split(' ')) > 3:
		_dict[indo_word] = None
		_dict.pop(indo_word, None)


for indo_word in _dict.keys():
	output = indo_word + '\t'
	for en_word in _dict[indo_word].keys():
		output = output + en_word + '||' + _dict[indo_word][en_word] + ' '
	print output.strip()

