import pandas as pd
import os
import re
from datetime import datetime

def extract_emails( text ):
	'''	Extract emails from string
	'''

	if type( text ) is not str:
		return []

	#	Define the regular expression for email extraction
	email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

	#	Find all matches of the pattern in the text
	emails = re.findall( email_pattern, text )

	return emails

def convert_date( date_str ):
	'''	Convert date string
	'''

	try:

		#	Parse the input date string with the given format
		parsed_date = datetime.strptime( date_str, '%a, %d %b %Y %H:%M:%S %z' )

	except ValueError:
		return None

	#	Convert to desired format 'YYYY-MM-DD'
	return parsed_date.strftime('%Y-%m-%d')

def extract_urls( text ):
	'''	Extract urls from string
	'''

	#	Define the regular expression for URL extraction
	url_pattern = r'(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+'

	#	Find all matches of the pattern in the text
	urls = re.findall(url_pattern, text)

	return urls

def CleanDataset( fileNumber: int ):
	''' Clean email text
	'''

	#   Get input / output file name
	inputFileName = f'CEAS{fileNumber:02d}.csv'
	outputFileName = f'cleanCEAS{fileNumber:02d}.csv'

	#   Get input / output file path
	inputPath = f'/data/users/fengwwta/SeniorProject/ceasDataset/orig/{inputFileName}'
	outputPath = f'/data/users/fengwwta/SeniorProject/ceasDataset/newClean/{outputFileName}'

	#   Check if path is exist
	if not os.path.exists( inputPath ):
		return

	#   Read CSV
	df = pd.read_csv( inputPath )

	# #   Clean email text in dataset
	# cleanTexts = pd.Series( index = df.body.index )

	senderAddr = pd.Series( index = df.sender.index )
	receiverAddr = pd.Series( index = df.receiver.index )
	convDate = pd.Series( index = df.date.index )
	urllinks = pd.Series( index = df.body.index )

	for row, _ in enumerate( df.body ): 
		# if row % 1000 == 0:
		print( f'\tRow: {row}' )
		
		senderAddr[ row ] = extract_emails( df.sender[ row ] )
		receiverAddr[ row ] = extract_emails( df.receiver[ row ] )
		convDate[ row ] = convert_date( df.date[ row ] )
		urllinks[ row ] = extract_urls( df.body[ row ] )

	#   Create clean text serie and drop text serie
	df[ 'sender' ] = senderAddr
	df[ 'receiver' ] = receiverAddr
	df[ 'date' ] = convDate
	df[ 'url_link' ] = urllinks

	# 	Create new CSV
	df.to_csv( outputPath, sep = ',', index = False, encoding = 'utf-8' )

############################################################
#
#   Main
#

for num in range( 1, 5 ):
	print( f'File No.{num:02d}' )
	CleanDataset( num )