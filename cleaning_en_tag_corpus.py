
file = 'en_tag_corpus_ignore.txt'

f = open(file, 'r')

for line in f:
	line = line.strip().split('<x length="1 ')
	output = '<sentence>'
	for token in line:
		if token != '':
			token = token.strip().split('</x>')
			token = token[0]
			if token and '">' in token and '|' in token:
				#delhi%1:15:00::|1.0">Delhi split based on >
				token2 = token.split('">')
				token3 = token2[0]
				word = token2[1]
				best_sense = None
				if token3.split('|')[0] != '':
					best_sense = token3.split('|')[0]
				if word and best_sense:
					output = output + word + '||' + best_sense + ' '
	output = output.strip().lower() + '</sentence>'
	print output

f.close()
