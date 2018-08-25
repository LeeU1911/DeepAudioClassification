# -*- coding: utf-8 -*-
import eyed3
import csv

#Remove logs
eyed3.log.setLevel("ERROR")
with open('Data/Raw/subset_train.csv', mode='r') as csv_file:
    genreData = csv.DictReader(csv_file)
    line_count = 0
    for row in genreData:
        line_count += 1
    print('Processed {0} lines.'.format(line_count))

def isMono(filename):
	audiofile = eyed3.load(filename)
	return audiofile.info.mode == 'Mono'

def getGenre(filename):
	return None


	