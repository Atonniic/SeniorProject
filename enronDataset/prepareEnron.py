import pandas as pd
import os

############################################################
#
#	Function
#

def GetMessage( series: pd.Series ):
	'''	Get message from text
	'''

	result = pd.Series( index = series.index )

	for row, message in enumerate( series ):
		messageWords = message.split( '\n' )
		del messageWords[ :15 ]
		result.iloc[ row ] = ''.join( messageWords ).strip()

	return result

def GetDate( series: pd.Series ):
	'''	Get date from text
	'''

	result = pd.Series( index = series.index )

	for row, message in enumerate( series ):
		messageWords = message.split( '\n' )
		del messageWords[ 0 ]
		del messageWords[ 1: ]
		result.iloc[ row ] = ''.join( messageWords ).strip() 
		result.iloc[ row ] = result.iloc[ row ].replace( 'Date: ', '' )

	print( 'Done parsing, converting to datetime format...' )
	return pd.to_datetime( result )

def GetSenderAndReceiver( series: pd.Series ):
	'''	Get sender and reciever from text
	'''
	
	sender = pd.Series( index = series.index )
	recipient1 = pd.Series( index = series.index )
	recipient2 = pd.Series( index = series.index )
	recipient3 = pd.Series( index = series.index )

	for row, message in enumerate( series ):
		messageWords = message.split( '\n' )
		sender[ row ] = messageWords[ 2 ].replace( 'From: ', '' )
		recipient1[ row ] = messageWords[ 3 ].replace( 'To: ', '' )
		recipient2[ row ] = messageWords[ 10 ].replace( 'X-cc: ', '' )
		recipient3[ row ] = messageWords[ 11 ].replace( 'X-bcc: ', '' )

	return sender, recipient1, recipient2, recipient3

def GetSubject( series: pd.Series ):
	'''	Get subject from text
	'''

	result = pd.Series( index = series.index )

	for row, message in enumerate( series ):
		messageWords = message.split( '\n' )
		messageWords = messageWords[ 4 ]
		result[ row ] = messageWords.replace( 'Subject: ', '' )

	return result

def GetFolder( series: pd.Series ):
	'''	Get folder from text
	'''

	result = pd.Series( index = series.index )

	for row, message in enumerate( series ):
		messageWords = message.split( '\n' )
		messageWords = messageWords[ 12 ]
		result[ row ] = messageWords.replace( 'X-Folder: ', '' )
	
	return result

def PrepareData( fileNumber: int ):
	'''	Prepare data
	'''

	inputFileName = f'enron{fileNumber:02d}.csv'
	outputFileName = f'prepareEnron{fileNumber:02d}.csv'

	inputFilePath = f'/data/users/fengwwta/SeniorProject/enronDataset/{inputFileName}'

	# 	Check if have file or not
	if not os.path.exists( inputFilePath ):
		return

	# 	Read CSV
	df = pd.read_csv( inputFilePath )

	# 	Separate message and add to data frame
	df[ 'text' ] = GetMessage( df.message )
	df[ 'sender' ], df[ 'recipient1' ], df[ 'recipient2' ], df[ 'recipient3' ] = GetSenderAndReceiver( df.message )
	df[ 'subject' ] = GetSubject( df.message )
	df[ 'folder' ] = GetFolder( df.message )
	df[ 'date' ] = GetDate( df.message )

	# 	Drop old part
	df = df.drop( [ 'message', 'file' ], axis = 1 )

	# 	Create new CSV
	df.to_csv( outputFileName, sep = ',', index = False, encoding = 'utf-8' )

for num in range( 1, 27 ):
	PrepareData( num )