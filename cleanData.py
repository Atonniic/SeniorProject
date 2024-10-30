import re
import pandas as pd
import nltk
from nltk.corpus import stopwords
from bs4 import BeautifulSoup
import spacy

#   Download stopwords from NLTK
nltk.download( 'stopwords' )
nltk.download( 'punkt' )

#   Load english language model from SpaCy
nlp = spacy.load( "en_core_web_sm" )

def clean_email_text( text ):
	''' Clean email data
	'''

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
