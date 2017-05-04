import re

f = open('original_id_ignore.txt','r')

def remove_punctuation(line):
	return re.sub('[\'\"!\,\.\(\)\?\;\:]', '', line)

for line in f:
	line = remove_punctuation(line.strip()).strip().lower()
	print line

f.close()