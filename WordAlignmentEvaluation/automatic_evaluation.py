import re

class Sentence:
	def __init__(self, number, indo, en_anotator_1, en_anotator_2, en_giza, en_bidirectional, en_crawling):
		self.number = number
		self.indo = indo
		self.en_giza = en_giza
		self.en_anotator_1 = en_anotator_1
		self.en_anotator_2 = en_anotator_2
		self.en_bidirectional = en_bidirectional
		self.en_crawling = en_crawling
	def evaluate(self):
		# compare the en_giza and en_anotator
		temp_giza = self.en_giza.split('({')
		temp_anotator_1 = self.en_anotator_1.split('({')
		temp_anotator_2 = self.en_anotator_2.split('({')
		temp_crawling = self.en_crawling.split('({')
		temp_bidirectional = self.en_bidirectional.split('({')
		(p1, r1, a, a) = self.calculate_precision_and_recall(temp_giza, temp_anotator_1, 1)
		(p1_crawling, r1_crawling, a, a) = self.calculate_precision_and_recall(temp_crawling, temp_anotator_1, 1)
		(p1_bidirectional, r1_bidirectional, a, a) = self.calculate_precision_and_recall(temp_bidirectional, temp_anotator_1, 1)
		'''
		if len(temp_giza) == len(temp_anotator_1):
			# process
			is_null_bracket = False
			matches, total_anotator, total_giza = 0, 0, 0
			for x in range(len(temp_giza)):
				# processing every token and the brackets
				if "NULL" in temp_giza[x].strip() and "NULL" in temp_anotator_1[x].strip():
					is_null_bracket = True
					continue
				if ('})' in temp_giza[x].strip() and '})' in temp_anotator_1[x].strip()):
					giza = temp_giza[x].strip().split('})')[0].strip().split(' ')
					anotator = temp_anotator_1[x].strip().split('})')[0].strip().split(' ')
					giza, anotator = self.clean_list_from_empty_string(giza), self.clean_list_from_empty_string(anotator)
					# need additional filter if either giza is empty (kosong) or anotator is empty
					# and counter to evaluate precision and recall
					if is_null_bracket:
						(numbers_anotator, numbers_giza, match) = self.evaluate_bracket(giza, anotator)
						is_null_bracket = False
					else:
						(numbers_anotator, numbers_giza, match) = self.evaluate_bracket(giza, anotator)
					matches += match
					total_giza += numbers_giza
					total_anotator += numbers_anotator
		else:
			print str(self.number), 'have different length in giza and anotator number 1'

		'''

		(p2, r2, a, a) = self.calculate_precision_and_recall(temp_giza, temp_anotator_2, 2)
		(p2_crawling, r2_crawling, a, a) = self.calculate_precision_and_recall(temp_crawling, temp_anotator_2, 2)
		(p2_bidirectional, r2_bidirectional, a, a) = self.calculate_precision_and_recall(temp_bidirectional, temp_anotator_2, 2)
		'''
		if len(temp_giza) == len(temp_anotator_2):
			# process
			is_null_bracket = False
			matches, total_anotator, total_giza = 0, 0, 0
			for x in range(len(temp_giza)):
				# processing every token and the brackets
				if "NULL" in temp_giza[x].strip() and "NULL" in temp_anotator_2[x].strip():
					is_null_bracket = True
					continue
				if ('})' in temp_giza[x].strip() and '})' in temp_anotator_2[x].strip()):
					giza = temp_giza[x].strip().split('})')[0].strip().split(' ')
					anotator = temp_anotator_2[x].strip().split('})')[0].strip().split(' ')
					giza, anotator = self.clean_list_from_empty_string(giza), self.clean_list_from_empty_string(anotator)
					# need additional filter if either giza is empty (kosong) or anotator is empty
					# and counter to evaluate precision and recall
					if is_null_bracket:
						(numbers_anotator, numbers_giza, match) = self.evaluate_bracket(giza, anotator)
						is_null_bracket = False
					else:
						(numbers_anotator, numbers_giza, match) = self.evaluate_bracket(giza, anotator)
					matches += match
					total_giza += numbers_giza
					total_anotator += numbers_anotator
			# return precision and agreement between two annotator
			# in the form of (p1,r1,p2,r2,agreement)
			return float(matches)/float(total_giza), float(matches)/float(total_anotator)			
		else:
			print str(self.number), 'have different length in giza and anotator number 2'
		'''
		agreement = self.calculate_agreement(temp_anotator_1, temp_anotator_2)
		(em, total) = self.evaluate_exact_match(temp_anotator_1, temp_anotator_2)
		#return (p1, p2, r1, r2, agreement)
		return round(p1,3), round(p2,3), round(r1,3), round(r2,3), round(agreement,3), em, total, round(p1_crawling, 3), round(p2_crawling, 3), round(r1_crawling, 3), round(r2_crawling, 3), round(p1_bidirectional, 3), round(p2_bidirectional, 3), round(r1_bidirectional, 3), round(r2_bidirectional, 3)

	def is_the_same(self, list_giza, list_anotator):
		# bracket is in form of array of number / arr of number (in string form)
		return (set(list_anotator) == set(list_giza))

	def evaluate_null_bracket(self, list_giza, list_anotator):
		exact_match = list(set(list_giza).intersection(list_anotator))
		diff = []
		for x in list_giza:
			if x not in exact_match:
				diff.append(x)
		for x in list_anotator:
			if x not in exact_match:
				diff.append(x)
		exact_match = len(exact_match)
		total = exact_match + len(diff)
		return (exact_match, total)


	def evaluate_bracket(self, list_giza, list_anotator):
		# evaluate per character
		numbers_anotator = len(list_anotator)
		numbers_giza = len(list_giza)
		match = 0
		if numbers_giza < numbers_anotator:
			# iterate through the numbers giza
			for n in list_giza:
				if n in list_anotator:
					match += 1
		else:
			# iterate through the numbers anotator
			for n in list_anotator:
				if n in list_giza:
					match += 1
		return (numbers_anotator, numbers_giza, match)

	def clean_list_from_empty_string(self, _list):
		new_list = []
		for x in range(len(_list)):
			if _list[x] != '':
				new_list.append(_list[x])
		return new_list

	def evaluate_exact_match(self, temp_giza, temp_anotator):
		is_null_bracket = False
		exact_match, total, miss = 0, 0, 0
		for x in range(len(temp_giza)):
			# processing every token and the brackets
			if "NULL" in temp_giza[x].strip() and "NULL" in temp_anotator[x].strip():
				is_null_bracket = True
				continue
			if ('})' in temp_giza[x].strip() and '})' in temp_anotator[x].strip()):
				giza = temp_giza[x].strip().split('})')[0].strip().split(' ')
				anotator = temp_anotator[x].strip().split('})')[0].strip().split(' ')
				giza, anotator = self.clean_list_from_empty_string(giza), self.clean_list_from_empty_string(anotator)
				# need additional filter if either giza is empty (kosong) or anotator is empty
				# and counter to evaluate precision and recall
				if is_null_bracket:
					temp_exact_match, temp_total = self.evaluate_null_bracket(giza, anotator)
					exact_match += temp_exact_match
					total += temp_total
					is_null_bracket = False
				else:
					total += 1
					if(self.is_the_same(giza, anotator)):
						# calculate as exact match
						exact_match += 1
		# return exact match, total
		return (exact_match, total)

	def calculate_precision_and_recall(self, temp_giza, temp_anotator, number):
		if len(temp_giza) == len(temp_anotator):
			# process
			is_null_bracket = False
			matches, total_anotator, total_giza = 0, 0, 0
			exact_match, total = 0, 0
			for x in range(len(temp_giza)):
				# processing every token and the brackets
				if "NULL" in temp_giza[x].strip() and "NULL" in temp_anotator[x].strip():
					is_null_bracket = True
					continue
				if ('})' in temp_giza[x].strip() and '})' in temp_anotator[x].strip()):
					giza = temp_giza[x].strip().split('})')[0].strip().split(' ')
					anotator = temp_anotator[x].strip().split('})')[0].strip().split(' ')
					giza, anotator = self.clean_list_from_empty_string(giza), self.clean_list_from_empty_string(anotator)
					# need additional filter if either giza is empty (kosong) or anotator is empty
					# and counter to evaluate precision and recall
					if is_null_bracket:
						(numbers_anotator, numbers_giza, match) = self.evaluate_bracket(giza, anotator)
						#temp_exact_match, temp_total = self.evaluate_null_bracket(giza, anotator)
						#exact_match += temp_exact_match
						#total += temp_total
						is_null_bracket = False
					else:
						(numbers_anotator, numbers_giza, match) = self.evaluate_bracket(giza, anotator)
						total += 1
						if(self.is_the_same(giza, anotator)):
							# calculate as exact match
							exact_match += 1
						'''
						this section is for tuple comparation rather than single number comparation
						if len(giza) > 0:
							numbers_giza += 1
						if len(anotator) > 0:
							numbers_anotator += 1
						if self.is_the_same(giza, anotator):
							match += 1
						'''
					matches += match
					total_giza += numbers_giza
					total_anotator += numbers_anotator
			# return precision, recall
			prec = float(matches)/float(total_giza)
			rec = float(matches)/float(total_anotator)
			return (prec, rec, exact_match, total) 
		else:
			print str(self.number), 'have different length in giza and anotator number', str(number)

	def calculate_agreement(self, temp_anotator_1, temp_anotator_2):
		if len(temp_anotator_1) == len(temp_anotator_2):
			is_null_bracket = False
			matches, total_anotator_1, total_anotator_2 = 0, 0, 0
			for x in range(len(temp_anotator_1)):
				# processing every token and the brackets
				if "NULL" in temp_anotator_1[x].strip() and "NULL" in temp_anotator_2[x].strip():
					is_null_bracket = True
					continue
				if ('})' in temp_anotator_1[x].strip() and '})' in temp_anotator_2[x].strip()):
					anotator_1 = temp_anotator_1[x].strip().split('})')[0].strip().split(' ')
					anotator_2 = temp_anotator_2[x].strip().split('})')[0].strip().split(' ')
					anotator_1, anotator_2 = self.clean_list_from_empty_string(anotator_1), self.clean_list_from_empty_string(anotator_2)
					# need additional filter if either giza is empty (kosong) or anotator is empty
					# and counter to evaluate precision and recall
					if is_null_bracket:
						(numbers_anotator_1, numbers_anotator_2, match) = self.evaluate_bracket(anotator_1, anotator_2)
						is_null_bracket = False
					else:
						(numbers_anotator_1, numbers_anotator_2, match) = self.evaluate_bracket(anotator_1, anotator_2)
					matches += match
					total_anotator_1 += numbers_anotator_1
					total_anotator_2 += numbers_anotator_2
			# return agreement as a total match / total length
			return float(matches)/float(total_anotator_2)
		else:
			print str(self.number), " having different length in anotator 1 and 2"



def get_sentence_number(line):
	m = re.search('Sentence pair #(.*)', line)
	return m.group(1)


# input the name of giza file and anotator file here
a3_giza_file = '200_testing_giza.txt'
a3_anotator_file_1 = '200_testing_nadiarani.txt'
a3_anotator_file_2 = '200_testing_jodi.txt'
a3_bidirectional_file = '200_testing_bidirectional.txt'
a3_crawling_file = '200_testing_crawling.txt'
# this is the filename section

f_a3 = open(a3_giza_file,'r')
f_a3_anotator_1 = open(a3_anotator_file_1, 'r')
f_a3_anotator_2 = open(a3_anotator_file_2, 'r')
f_a3_bidirectional = open(a3_bidirectional_file, 'r')
f_a3_crawling = open(a3_crawling_file, 'r')

arr_of_sentence = {}

sentence = None
state = 0

for line in f_a3:
	# giza first
	line = line.strip()
	if "Sentence pair #" in line:
		number = get_sentence_number(line)
		sentence = Sentence(number, '', '', '', '', '', '')
		arr_of_sentence[number] = sentence
		state = 1
	else:
		if state == 1:
			line = re.sub(' \.$|\.$', '', line)
			sentence.indo = line
			state = 2
		elif state == 2:
			line = re.sub('(\.| \.) \(\{ \}\)$|(\.| \.) \(\{ ([\d]+) \}\)$', '', line)
			sentence.en_giza = line
			state = 0

f_a3.close()

sentence = None

for line in f_a3_anotator_1:
	# from anotator 1
	line = line.strip()
	if "Sentence pair #" in line:
		state = 1
		number = get_sentence_number(line)
		sentence = arr_of_sentence[number]
	else:
		if state == 1:
			state = 2
		elif state == 2:
			sentence.en_anotator_1 = line
			state = 0

f_a3_anotator_1.close()

for line in f_a3_anotator_2:
	# from anotator 2
	line = line.strip()
	if "Sentence pair #" in line:
		state = 1
		number = get_sentence_number(line)
		sentence = arr_of_sentence[number]
	else:
		if state == 1:
			state = 2
		elif state == 2:
			line = re.sub('(\.| \.) \(\{ \}\)$|(\.| \.) \(\{ ([\d]+) \}\)$', '', line)
			sentence.en_anotator_2 = line
			state = 0

f_a3_anotator_2.close()


for line in f_a3_bidirectional:
	# from anotator 2
	line = line.strip()
	if "Sentence pair #" in line:
		state = 1
		number = get_sentence_number(line)
		sentence = arr_of_sentence[number]
	else:
		if state == 1:
			state = 2
		elif state == 2:
			sentence.en_bidirectional = line
			state = 0

f_a3_bidirectional.close()

for line in f_a3_crawling:
	# from anotator 2
	line = line.strip()
	if "Sentence pair #" in line:
		state = 1
		number = get_sentence_number(line)
		sentence = arr_of_sentence[number]
	else:
		if state == 1:
			state = 2
		elif state == 2:
			sentence.en_crawling = line
			state = 0

f_a3_crawling.close()


calculation = {
	'precision_1' : 0,
	'precision_2' : 0,
	'recall_1' : 0,
	'recall_2' : 0,
	'f1_1' : 0,
	'f1_2' : 0,
	'agreement' : 0,
	'precision_1_crawling' : 0,
	'precision_2_crawling' : 0,
	'precision_1_bidirectional' : 0,
	'precision_2_bidirectional' : 0,
	'recall_1_crawling' : 0,
	'recall_2_crawling' : 0,
	'recall_1_bidirectional' : 0,
	'recall_2_bidirectional' : 0
}

exact_match = 0
total_match = 0

for key in arr_of_sentence:
	(p1, p2, r1, r2, agreement, em, total, p1_crawling, p2_crawling, r1_crawling, r2_crawling, p1_bidirectional, p2_bidirectional, r1_bidirectional, r2_bidirectional) = arr_of_sentence[key].evaluate()
	exact_match += em
	total_match += total
	calculation['precision_1'] = float(calculation['precision_1'] + p1) / 2.0
	calculation['precision_1_crawling'] = float(calculation['precision_1_crawling'] + p1_crawling) / 2.0
	calculation['precision_1_bidirectional'] = float(calculation['precision_1_bidirectional'] + p1_bidirectional) / 2.0
	calculation['precision_2'] = float(calculation['precision_2'] + p2) / 2.0
	calculation['precision_2_crawling'] = float(calculation['precision_2_crawling'] + p2_crawling) / 2.0
	calculation['precision_2_bidirectional'] = float(calculation['precision_2_bidirectional'] + p2_bidirectional) / 2.0
	calculation['recall_1'] = float(calculation['recall_1'] + r1) / 2.0 
	calculation['recall_1_crawling'] = float(calculation['recall_1_crawling'] + r1_crawling) / 2.0
	calculation['recall_1_bidirectional'] = float(calculation['recall_1_bidirectional'] + r1_bidirectional) / 2.0
	calculation['recall_2'] = float(calculation['recall_2'] + r2) / 2.0
	calculation['recall_2_crawling'] = float(calculation['recall_2_crawling'] + r2_crawling) / 2.0
	calculation['recall_2_bidirectional'] = float(calculation['recall_2_bidirectional'] + r2_bidirectional) / 2.0
	calculation['agreement'] = float(calculation['agreement'] + agreement) / 2.0 

print ' With Original Giza '
print 'Precision 1:', round(calculation['precision_1'],3),'Precision 2:', round(calculation['precision_2'],3), 'Recall 1:', round(calculation['recall_1'],3),'Recall 2:', round(calculation['recall_2'],3), 'Agreement:', round(calculation['agreement'],3)
print 'F-Score 1:', round(2*calculation['precision_1']*calculation['recall_1']/(calculation['precision_1'] + calculation['recall_1']),3)
print 'F-Score 2:', round(2*calculation['precision_2']*calculation['recall_2']/(calculation['precision_2'] + calculation['recall_2']),3)
print exact_match, total_match

print ' With Crawling '
print 'Precision 1:', round(calculation['precision_1_crawling'],3),'Precision 2:', round(calculation['precision_2_crawling'],3), 'Recall 1:', round(calculation['recall_1_crawling'],3),'Recall 2:', round(calculation['recall_2_crawling'],3), 'Agreement:', round(calculation['agreement'],3)
print 'F-Score 1:', round(2*calculation['precision_1_crawling']*calculation['recall_1_crawling']/(calculation['precision_1_crawling'] + calculation['recall_1_crawling']),3)
print 'F-Score 2:', round(2*calculation['precision_2_crawling']*calculation['recall_2_crawling']/(calculation['precision_2_crawling'] + calculation['recall_2_crawling']),3)

print ' With Bidirectional '
print 'Precision 1:', round(calculation['precision_1_bidirectional'],3),'Precision 2:', round(calculation['precision_2_bidirectional'],3), 'Recall 1:', round(calculation['recall_1_bidirectional'],3),'Recall 2:', round(calculation['recall_2_bidirectional'],3), 'Agreement:', round(calculation['agreement'],3)
print 'F-Score 1:', round(2*calculation['precision_1_bidirectional']*calculation['recall_1_bidirectional']/(calculation['precision_1_bidirectional'] + calculation['recall_1_bidirectional']),3)
print 'F-Score 2:', round(2*calculation['precision_2_bidirectional']*calculation['recall_2_bidirectional']/(calculation['precision_2_bidirectional'] + calculation['recall_2_bidirectional']),3)
