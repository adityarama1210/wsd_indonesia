f = open('enhanced_dictionary_crawl.txt', 'r')

_dict = {}

for line in f:
	line = line.strip().split('\t')
	word = line[0].lower()
	pairs = line[1].split(' ')
	if word not in _dict:
		_dict[word] = {}
	for pair in pairs:
		pair = pair.split('||')
		w = pair[0].lower()
		c = pair[1]
		if w not in _dict[word]:
			_dict[word][w] = c

f.close()


for key in _dict.keys():
	output = key + '\t'
	for w in _dict[key].keys():
		output = output + w +'||' + _dict[key][w]+' '
	print output.strip()