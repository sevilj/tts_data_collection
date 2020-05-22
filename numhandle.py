#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import re

#Regex
numRegex = re.compile("\d+")
dateRegex = re.compile("\d{1,2}\s*\.*\d{1,2}\s*\.*\d{4}")
timeRegex = re.compile("\d+:\d+")
telRegex = re.compile("(\d+\-\d+(\-\d+)*)")
wordNumRegex = re.compile("\s+|\s*\,+\s*|\s*\.+\s*|\s*\-+\s*|\s*\)+\s*|\s*\(+\s*|\s*:+\s*")
numsRegex = re.compile("(\d+\s+(\d+\s*)+)")
areaRegex = re.compile("m(\s*)2|metr(\s*)2")


dateWordRegex = re.compile("[0-3][0-9] [0-1][0-9] \d{4}")
timeWordRegex = re.compile("[0-2]{1}[0-9]{1} [0-6]{1}[0-9]{1}\D")
telWordRegex = re.compile("((\d{3}|012)\s\d{2,3}(\s\d{2})*)")
square = 'KVADRAT'
areaWordRegex = re.compile("m\s*"+square+"|metr\s*"+square)



# Container for lines
transcripts = []
transcripts_with_textified_numbers = []
transcripts_with_numberfied_numbers = []

# Mappings
number_map = {
	0: 'SIFIR', 1: 'BİR', 2: 'İKİ', 3: 'ÜÇ', 4: 'DÖRD', 5: 'BEŞ', 6: 'ALTI', 7: 'YEDDİ', 8: 'SƏKKİZ', 9: 'DOQQUZ', # Təklik
	10: 'ON', 20: 'İYİRMİ', 30: 'OTUZ', 40: 'QIRX', 50: 'ƏLLİ', 60: 'ALTMIŞ', 70: 'YETMİŞ', 80: 'SƏKSƏN', 90: 'DOXSAN', # Onluq
	100: 'YÜZ',
	1000: 'MİN',

}

month_map = {
	1: 'YANVAR', 2: 'FEVRAL', 3: 'MART', 4: 'APREL', 5: 'MAY', 6: 'İYUN', 7: 'İYUL', 8: 'AVQUST', 9: 'SENTYABR',
	10: 'OKTYABR', 11: 'NOYABR', 12: 'DEKABR'
}

vals = list(number_map.values())
keys = list(number_map.keys())

def textifyNum(sentences):
	# Find Numbers and Replace with words
	for line in sentences:
		transcripts_with_textified_numbers.append(replaceNumberstoWords(line))


	return transcripts_with_textified_numbers


def numberfyWords(sentences):
	# Find Words indicating numbers and Replace with numbers
	for line in sentences:
		# remove all double spaces
		line = line.replace("  ", " ")
		transcripts_with_numberfied_numbers.append(replaceWordstoNumbers(line, 0))

	return transcripts_with_numberfied_numbers


#@ line - line to be changed
def replaceNumberstoWords(line):
	# Regexes to find numbers
	found = numRegex.search(line)
	foundDate = dateRegex.search(line)
	foundTime = timeRegex.search(line)
	foundTel = telRegex.search(line)

	# If there is a date in the text remove dots
	if foundDate:
		date = foundDate.group()
		spacedDate = date.replace('.',' ')
		line = line.replace(date, spacedDate, 1)
		
	# If there is time in the text remove colons
	if foundTime:
		time = foundTime.group()
		spacedTime = time.replace(':',' ')
		line = line.replace(time, spacedTime, 1)

	# If there is a telephone number in the text remove dashes
	if foundTel:
		tel = foundTel.group()
		spacedTel = tel.replace('-',' ')
		line = line.replace(tel, spacedTel, 1)

	# If there is a number indicating the area
	if re.search("\Wm(\s*)2|\Wmetr(\s*)2", line):
		areaNum = 0
		if len(re.search("(\Wm(\s*)2)|(\Wmetr(\s*)2)", line).group().split()) > 1:
			areaNum = re.search("(\Wm(\s*)2)|(\Wmetr(\s*)2)", line).group().split()[1]
		elif len(re.search("(\Wm(\s*)2)|(\Wmetr(\s*)2)", line).group().split()) == 1:
			areaNum = re.search("(\Wm(\s*)2)|(\Wmetr(\s*)2)", line).group().split()[0][-1]
		
		wordForm = "KVADRAT"
		# if number is adjacent to a word
		if re.search("\w"+str(areaNum), line):
			wordForm = " "+wordForm
		line = line.replace(areaNum, wordForm, 1)
		
	# If there is any number in the text
	if found:
		number = found.group()
		wordForm = ''
		
		# Adding first zeros to the word
		if re.search("^0", number):
			wordForm += number_map[0]+" "
			if re.search("^00", number):
				wordForm += number_map[0]+" "

		changable_number = float(number)		
		wordForm += mappingNumberstoWords(float(number),1000)

		# if number is adjacent to a word
		if re.search("\w"+str(number), line):
			wordForm = " "+wordForm

		line = line.replace(number, wordForm.rstrip(), 1)

		# recursion
		return replaceNumberstoWords(line)

	# remove all double spaces
	line = line.replace("  ", " ")
	return line

#@ line - line to be changed
#@ index - used to start from definite position
def replaceWordstoNumbers(line, index):
	found = False

	for i,l in enumerate(wordNumRegex.split(line[index:])):

		# If there is a word indicating a number in the text
		try:
			changable_word = str(keys[vals.index(l)])
			found = True
			index = i			
			line = line.replace(l, changable_word, 1)
			break
		except:
			pass

	# If line still has unchanged words
	if found:
		# recursion
		return replaceWordstoNumbers(line, index)

	line = formattingNumbers(line)
	line = formattingSpecialNumbers(line)
	return line

#@ number - number to be changed
#@ num_zeros - used to find yuzluk, onluq, teklik etc. default:1000
def mappingNumberstoWords(number, num_zeros):
	wordForm = ''
	if(num_zeros != 0):
		division = int(number/num_zeros)

		if (division != 0):
			# Taking into account different words for onluq
			if num_zeros == 10:
				wordForm += number_map[division*num_zeros] + " "
			# Straight number for teklik
			elif num_zeros == 1:
				wordForm += number_map[division] + " "
			else:
				# Not adding number 1 to the word before yuz, min etc.
				if(division != 1):
					try:
						wordForm += number_map[division] + " "
					except KeyError as e:
						# Handling numbers bigger than thousand
						# recursion
						wordForm += mappingNumberstoWords(division, 1000)

				wordForm += number_map[num_zeros] + " "

		# recursion
		wordForm += mappingNumberstoWords(number%num_zeros, int(num_zeros/10))
		
	return wordForm

#@ line - line to be changed
def formattingNumbers(line):
	summingNum = 0
	lastNum = ""

	for word in wordNumRegex.split(line):
		if word.isdigit():
			# if number is found to merge

			numWord = int(word)
			# multiplying numbers before 1000
			if numWord == 1000 and summingNum != 0:
				numWord = (summingNum%1000000)*numWord
				summingNum -= (summingNum%1000000)
			# multiplying numbers before 100
			elif numWord == 100 and summingNum != 0 and int(summingNum%10) > 0:
				numWord = (summingNum%1000)*numWord
				summingNum -= (summingNum%1000)			

			# if number is a decimal, check if there is already a decimal
			if 10 <= numWord < 100 and int(summingNum%100) > 0:						
				lastNum = lastNum.rstrip() #remove additional whitespaces
				if summingNum != 0:
					line = line.replace(lastNum, str(summingNum), 1) # replace words with numbers

				# refresh values
				summingNum = 0
				lastNum = ""

			# if number is a singular, check if there is already a singular
			if numWord < 10 and int(summingNum%10) > 0:
				lastNum = lastNum.rstrip() #remove additional whitespaces
				if summingNum != 0:
					line = line.replace(lastNum, str(summingNum), 1) # replace words with numbers
				
				# refresh values
				summingNum = 0
				lastNum = ""

			# if encountered with zero, print the last number and seperately zero
			if numWord == 0:
				if lastNum:
					lastNum = lastNum.rstrip() #remove additional whitespaces
					line = line.replace(lastNum, str(summingNum), 1) # replace words with numbers				
				
				# if zero is not part of the number
				if re.search("[^\d+]0 |^0 ", line):
					line = line.replace("0 ", "0", 1) # replace words with numbers		
				
				# refresh values
				summingNum = 0
				lastNum = ""
				continue

			# Save values
			summingNum += numWord
			lastNum += word+" "
			
			# Divide numbers by dot
			if re.search(lastNum.rstrip()+"\.", line):
				lastNumDotted = lastNum.rstrip()+"." #remove additional whitespaces and add a dot
				if summingNum != 0:
					
					line = line.replace(lastNumDotted, str(summingNum)+".", 1) # replace words with numbers
					summingNum = 0
					lastNum = ""
			
		else:
			# when the number ended

			lastNum = lastNum.rstrip() #remove additional whitespaces
			if summingNum != 0:
				line = line.replace(lastNum, str(summingNum), 1) # replace words with numbers
				
			# refresh values
			summingNum = 0
			lastNum = ""

	# if number is at the end
	if lastNum != "" and summingNum != 0:
		lastNum = lastNum.rstrip() #remove additional whitespaces
		if summingNum != 0:
			line = line.replace(lastNum, str(summingNum), 1) # replace words with numbers

		# refresh values
		summingNum = 0
		lastNum = ""

	return line

def formattingSpecialNumbers(line):
	# If there is a date in the text add dots
	dates = re.findall(dateWordRegex, line)
	if dates:
		for date in dates:
			dottedDate = date.replace(" ", ".",2)
			line = line.replace(date, dottedDate, 1)
	
	# If there is time in the text add colons
	times = re.findall(timeWordRegex, line)
	
	if times:
		for time in times:
			colonedTime = time.replace(" ", ":",1)
			line = line.replace(time, colonedTime, 1)

	# If there is a telephone number in the text add dashes
	tels = re.findall(telWordRegex, line)
	if tels:
		for tel in tels:
			tel = str(tel)
			count = int(len(tel)/3-1)
			
			dashedTel = tel.replace(" ", "-",count)
			line = line.replace(tel, dashedTel, 1)
	
	# If there is a number indicating the area
	areas = re.findall(areaWordRegex, line)
	if areas:
		for area in areas:
			line = line.replace(square, "2", 1)


	return line