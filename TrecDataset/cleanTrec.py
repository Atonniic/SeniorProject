import pandas as pd
import os
import re
import nltk
from nltk.corpus import stopwords
from bs4 import BeautifulSoup
import spacy

#   Download stopwords from NLTK
nltk.download( 'stopwords' )
nltk.download( 'punkt' )

#   Load english language model from SpaCy
nlp = spacy.load( "en_core_web_sm" )

def CleanEmailText( text: str ):
	''' Clean email data
	'''

	if type( text ) is not str:
		return ''

	#   1. Remove HTML tags
	text = BeautifulSoup( text, "html.parser" ).get_text()
	
	#   2. Convert alphabet to lower
	text = text.lower()
	
	#   3. Remove URL
	text = re.sub( r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE )
	
	#   4. Remove email address
	text = re.sub( r'\S*@\S*\s?', '', text )
	
	#   5. Remove special character and number
	text = re.sub( r'\d+', '', text )  # Remove number
	text = re.sub( r'[^\w\s]', '', text )  # Remove space
	
	#   6. Remove Stopwords
	stop_words = set( stopwords.words( 'english' ) )
	word_tokens = nltk.word_tokenize(text)
	text = ' '.join( [ word for word in word_tokens if word not in stop_words ] )
	
	#   7. Tokenization and Lemmatization by SpaCy
	doc = nlp( text )
	text = ' '.join( [ token.lemma_ for token in doc ] )  # ลดคำเป็นรากฐาน
	
	return text

def CleanDataset( fileNumber: int ):
	''' Clean email text
	'''

	#   Get input / output file name
	inputFileName = f'TREC{fileNumber:02d}.csv'
	outputFileName = f'cleanTrec{fileNumber:02d}.csv'

	#   Get input / output file path
	inputPath = f'/data/users/fengwwta/SeniorProject/TrecDataset/orig/{inputFileName}'
	outputPath = f'/data/users/fengwwta/SeniorProject/TrecDataset/clean/{outputFileName}'

	#   Check if path is exist
	if not os.path.exists( inputPath ):
		return

	#   Read CSV
	df = pd.read_csv( inputPath )

	#   Clean eamil message in dataset
	cleanMessages = pd.Series( index = df.message.index )
	for row, message in enumerate( df.message ): 
		if row % 1000 == 0:
			print( f'\tRow: {row}' )
		cleanMessages[ row ] = CleanEmailText( message )

	#   Create clean message serie and drop message serie
	df[ 'cleanMessage' ] = cleanMessages
	df = df.drop( [ 'message' ], axis = 1 )

	# 	Create new CSV
	df.to_csv( outputPath, sep = ',', index = False, encoding = 'utf-8' )

############################################################
#
#   Main
#

for num in range( 1, 5 ):
	print( f'File No.{num:02d}' )
	CleanDataset( num )