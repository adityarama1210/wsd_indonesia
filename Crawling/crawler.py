import requests
import re

url = "http://vvv.sederet.com/translate.php"
data = {
	'q': '',
	'lang': 'id_en'
}

chosen_words_file = 'clean_dict.txt'

def is_containing_number(line):
	m = re.search('[0-9]', line)
	return m != None

def is_ascii(s):
    return all(ord(c) < 128 for c in s)

def get_arr_of_translation(indo):
	data['q'] = indo
	text = requests.post(url, data)
	arr = re.findall('<div class="result_text">(.*)</div>', text.text)
	final_arr = []
	for x in range(len(arr)):
		if '<a href="http://vvv.sederet.com/translate.php?' in arr[x]:
			break
		else:
			if is_ascii(arr[x]):
				final_arr.append(arr[x])
	final_arr = map(str, final_arr)
	res_arr = []
	for token in final_arr:
		if "; " in token:
			temp = token.split('; ')
			for word in temp:
				word = word.strip()
				if word not in res_arr:
					res_arr.append(word)
		else:
			if token not in res_arr:
				res_arr.append(token)
	return res_arr

files = ['enhanced_dictionary_crawl.txt']


last_word = None
for file in files:
	file_open = open(file, 'r')
	for line in file_open:
		line = line.strip()
		last_word = line.split('\t')[0]
		
	file_open.close()

f = open(chosen_words_file, 'r')


f_out = open('enhanced_dictionary_crawl_2.txt', 'w')

state = 0

counter = 1

for line in f:
	line = line.strip().split('\t')
	word_indo = line[0]
	if word_indo == last_word:
		state = 1
		continue
	if state == 1:
		if not(is_containing_number(word_indo)) and is_ascii(word_indo):
			arr_translate = get_arr_of_translation(word_indo)
			if len(line) > 1:
				giza_res = line[1].split(' ')
				arr = []
				res = word_indo +'\t'
				match = 0
				for token in giza_res:
					t_result = token.split('||')[0]
					t_number = token.split('||')[1]
					if t_result.lower() in arr_translate:
						# the correct translation
						match += 1
						res = res + t_result + '||' + t_number + ' '
				if match > 0:
					res = res.strip()
					f_out.write(res+'\n')
				print 'Kata ke:', counter,'match', match, ' sisa:', str(159699 - counter)
	print 'Kata ke:', counter,'sisa:', str(159699 - counter)
	counter += 1
		

f_out.close()

f.close()