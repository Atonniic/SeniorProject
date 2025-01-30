from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import re
import requests
import os
from dotenv import load_dotenv
from huggingface_hub import login
from email.parser import BytesParser
from email import policy
from bs4 import BeautifulSoup
import psycopg2
from datetime import datetime
import hashlib

app = FastAPI()

#	Setting CORS
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

#	Load .env
load_dotenv( '../../.env' )
hunterioApiKey = os.getenv( 'hunterio_apikey' )
xApiKeys = os.getenv( 'x_apikey' )
huggingfaceToken = os.getenv( 'huggingface_token' )
postgresUrl = os.getenv( 'postgres_url' )

# 	Login to Hugging Face
login( token = huggingfaceToken )
print(  "Login to Hugging Face" )

# 	Load Model & Tokenizer
base_model = AutoModelForCausalLM.from_pretrained( "meta-llama/Llama-3.2-1B" )
model = PeftModel.from_pretrained( base_model, "apkmew/LlamaPhishing" )
tokenizer = AutoTokenizer.from_pretrained( "apkmew/LlamaPhishing" )

print(  "Model & Tokenizer Loaded" )

##############################################################
#
#	Class OOP
#

class EmailData( BaseModel ):
	sender: str
	date: datetime
	subject: str
	body: str
 
class EmailFile( BaseModel ):
	fileName: str
	content: str  # String content of the EML file

##############################################################
#
#	Helper Function
#

def generate_test_prompt( text ):
	'''	Generate the prompt for the model to classify the text into Phishing Email or Normal Email.

		Parameters:
			text (str): The text to be classified.

		Returns:
			str: The prompt for the model
	'''

	return f'''
			Classify the text into Phishing Email or Normal Email, and return the answer.
			text: { text }
			label: '''.strip()

def predict( text, model, tokenizer ):
	'''	Predict the text is Phishing Email or Normal Email.

		Parameters:
			text (str): The text to be classified.
			model (transformers.PreTrainedModel): The model to classify the text.
			tokenizer (transformers.PreTrainedTokenizer): The tokenizer to tokenize the text.

		Returns:
			bool: True if the text is Phishing Email, False if the text is Normal Email.
	'''

	# 	Generate the prompt for the model
	prompt = generate_test_prompt( text )

	# 	Generate the answer
	pipe = pipeline( 	task = "text-generation",
						model = model,
						tokenizer = tokenizer,
						max_new_tokens = 2,
						temperature = 0.1 )

	# 	Generate the answer
	result = pipe( prompt )
	answer = result[ 0 ][ 'generated_text' ].split( "label:" )[ -1 ].strip()
	
	return True if answer == "1" else False

def extract_urls( text ):
	'''	Extract urls from string

		Parameters:
			text (str): The text to extract the urls.

		Returns:
			list: The list of urls extracted from the text.
	'''

	#	Define the regular expression for URL extraction
	url_pattern = r'(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+'

	#	Find all matches of the pattern in the text
	urls = re.findall(url_pattern, text)

	return urls

def check_url( urls ):
	'''	Check the urls are malicious or not.

		Parameters:
			urls (list): The list of urls to be checked.

		Returns:
			bool: True if the urls are malicious, False if the urls are not malicious.
	'''

	#	Check each url
	for url in urls:

		#	Scan the url
		scanUrl = "https://www.virustotal.com/api/v3/urls"

		payload = { "url": url }
		headers = {
			"accept": "application/json",
			"content-type": "application/x-www-form-urlencoded",
			"X-Apikey": xApiKeys
		}

		response = requests.post( scanUrl, data = payload, headers = headers )

		#	Check the url is valid or not
		if 'error' in response.json():
			continue

		#	Get the id of the analysis
		id = response.json()[ 'data' ][ 'id' ]

		#	Get the analysis result
		analysisUrl = f"https://www.virustotal.com/api/v3/analyses/{ id }"

		headers = { "accept": "application/json",
					"X-Apikey": xApiKeys
		}

		response = requests.get( analysisUrl, headers = headers )

		#	Check the url is malicious or not
		if response.json()[ 'data' ][ 'attributes' ][ 'stats' ][ 'malicious' ] > 0:
			return True
		
	#	Return False if all urls are not malicious
	return False

def check_sender( sender ):
	'''	Check the sender email is valid or not.

		Parameters:
			sender (str): The sender email to be checked.

		Returns:
			bool: True if the sender email is valid, False if the sender email is invalid.
	'''

	response = requests.get( f'https://api.hunter.io/v2/email-verifier?email={ sender }&api_key={ hunterioApiKey }' )

	score = response.json()[ 'data' ][ 'score' ]

	return True if score >= 70 else False

def extract_email( header_value ):
	'''	Extract the email address from a header value.
	
		Parameters:
			header_value (str): The header value containing the email address.

		Returns:
			str: The email address extracted from the header value.
	'''

	email_match = re.search( r'<([^>]+)>', header_value )
	return email_match.group( 1 ) if email_match else header_value.strip()

def extract_body( msg ):
	'''	Extract the body of an email.

		Parameters:
			msg (email.message.Message): The email message object.

		Returns:
			str: The body of the email.
	'''

	body = ''

	#	Check if the email is multipart
	if msg.is_multipart():

		# 	Iterate through the parts of the email
		for part in msg.iter_parts():

			# 	Get the content type of the part
			content_type = part.get_content_type()

			try:

				# 	Extract the body based on the content type
				if content_type == "text/plain":
					body = part.get_payload( decode = True ).decode( part.get_content_charset() )
					break

				# 	Extract the body based on the content type
				elif content_type == "text/html":
					html_content = part.get_payload( decode = True ).decode( part.get_content_charset() )
					soup = BeautifulSoup( html_content, 'html.parser' )
					body = soup.get_text()

			except Exception as e:
				print(f"Error processing part with content type {content_type}: {e}")

	else:

		# 	Get the content type of the email
		content_type = msg.get_content_type()

		try:

			# 	Extract the body based on the content type
			if content_type == "text/plain":
				body = msg.get_payload( decode = True ).decode( msg.get_content_charset() )

			# 	Extract the body based on the content type
			elif content_type == "text/html":
				html_content = msg.get_payload( decode = True ).decode( msg.get_content_charset() )
				soup = BeautifulSoup(html_content, 'html.parser')
				body = soup.get_text()

		except Exception as e:
			print( f"Error processing email body: {e}" )

	# 	Return the body content
	return body.strip() if body else "No body content found."

def parse_eml_content(content: str):
	'''	Parse the EML content and extract sender, subject, and body.

		Parameters:
			content (str): The EML content to parse.

		Returns:
			tuple: A tuple containing the sender, subject, and body of the email.
	'''

	try:

		# 	Parse the EML content
		msg = BytesParser( policy = policy.default ).parsebytes( content.encode() )

		# 	Extract the sender, subject, and body
		sender = extract_email( msg[ "From" ] ) if msg[ "From" ] else "No From found"
		subject = msg[ "Subject" ] if msg[ "Subject" ] else "No Subject found"
		body = extract_body( msg )

		return sender, subject, body

	except Exception as e:
		return "Error", "Error", f"Parsing failed: {str( e )}"

def extendedCategorizeSubject(subject):
	categories = {
		"Computers and Internet": [
			"internet", "software", "computer", "website", "it", "technology", "hardware", "programming", 
			"developer", "app", "coding", "online", "digital", "networking", "cloud", "data", "cyber", "security"
		],
		"Business and Industry": [
			"business", "industry", "commerce", "corporate", "marketing", "sales", "management", "workforce",
			"startup", "strategy", "logistics", "supply chain", "operation", "HR", "revenue", "profit", "growth",
			"market share", "economy", "trade", "productivity"
		],
		"Infrastructure and Content Delivery Networks": [
			"infrastructure", "network", "cloud", "data center", "content delivery", "cdn", "server", "hosting",
			"backend", "architecture", "system", "platform", "connectivity", "iot", "edge", "bandwidth", "latency"
		],
		"Science and Technology": [
			"science", "technology", "engineering", "research", "AI", "machine learning", "robotics", "space",
			"innovation", "physics", "biology", "chemistry", "experiment", "data analysis", "quantum", "nanotech"
		],
		"Search Engines and Portals": [
			"search", "portal", "engine", "directory", "navigation", "lookup", "results", "search tool", "browser"
		],
		"Social Networking": [
			"social", "network", "chat", "connect", "community", "platform", "followers", "friends", "share",
			"engagement", "interaction", "messaging", "posting", "profile", "group"
		],
		"Finance": [
			"finance", "money", "investment", "bank", "account", "tax", "loan", "credit", "mortgage", "insurance",
			"economy", "trading", "stock", "budget", "wealth", "financial", "fund", "capital", "revenue", "payment"
		],
		"Shopping": [
			"shopping", "buy", "sell", "price", "offer", "discount", "deal", "product", "ecommerce", "store",
			"mall", "shop", "cart", "purchase", "order", "checkout", "bargain", "sale", "promo", "coupon", "retail", "save"
		],
		"Education": [
			"education", "school", "university", "training", "learning", "course", "student", "teacher",
			"workshop", "class", "lesson", "study", "academic", "homework", "test", "exam", "tutorial", "knowledge" 
		],
		"Entertainment": [
			"movie", "music", "game", "show", "concert", "event", "festival", "video", "streaming", "entertainment",
			"celebrity", "fun", "leisure", "hobby", "recreation", "theater", "tv", "series", "episode", "art", "culture"
		],
		"Health and Wellness": [
			"health", "wellness", "fitness", "exercise", "diet", "nutrition", "medicine", "doctor", "hospital",
			"clinic", "therapy", "mental health", "well-being", "workout", "yoga", "recovery", "care", "treatment"
		],
		"News and Media": [
			"news", "media", "report", "headline", "journal", "magazine", "article", "breaking", "coverage",
			"story", "blog", "broadcast", "newsletter", "publication", "press", "cnn", "bbc", "update", "alert"
		]
	}
	
	if not isinstance(subject, str) or subject.strip() == "":
		return None
	
	subject_lower = subject.lower()
	for category, keywords in categories.items():
		if any(keyword in subject_lower for keyword in keywords):
			return category
	return "Other"

def generate_email_id( sender, date, subject, body ):
	'''	Generate an email_id from the email data.

		Parameters:
			sender (str): The sender of the email.
			date (str): The date of the email.
			subject (str): The subject of the email.
			body (str): The body of the email.

		Returns:
			str: The generated email_id.
	'''

	#	Concatenate the email data
	email_data = f"{ sender }_{ date }_{ subject }_{ body }"

	#	Generate the email_id
	email_id = hashlib.md5( email_data.encode() ).hexdigest()

	return email_id

def insert_email_to_db( data ):
	'''	Insert email data into the PostgreSQL database.

		Parameters:
			data (dict): The email data to be inserted into the database.

		Returns:
			None
	'''
	
	try:
		# Connect to PostgreSQL database
		conn = psycopg2.connect( postgresUrl )
		cursor = conn.cursor()
		print("Connected to the database successfully.")

		# Start transaction
		conn.autocommit = False

		# Prepare data for insertion
		sender = data.get( "sender" )
		date = data.get( "date" )
		subject = data.get( "subject" )
		body = data.get( "body" )
		label = data.get( "label" )

		# Extract URLs from the body
		urls = extract_urls( body )

		# Determine category based on subject
		category = extendedCategorizeSubject( subject )

		try:
			# Convert date string to datetime object
			date = datetime.strptime( date, "%Y-%m-%d" ).date() if date else None

			# Generate email_id
			email_id = generate_email_id( sender, date, subject, body )

			# Check if the email_id already exists in the database
			email_id_query = "SELECT email_id FROM email WHERE email_id = %s;"
			cursor.execute( email_id_query, ( email_id, ) )
			result = cursor.fetchone()
			if result:
				print( f"Email with email_id { email_id } already exists in the database. Skipping insertion..." )
				return

			# Insert email data into the `email` table
			email_insert_query = """
				INSERT INTO email (email_id, sender, date, subject, label, category)
				VALUES (%s, %s, %s, %s, %s, %s);
			"""
			cursor.execute( email_insert_query, ( email_id, sender, date, subject, label, category ) )

			# Insert URLs into the `email_urllinks` table
			urllinks_insert_query = """
				INSERT INTO email_urllinks (email_id, urllink)
				VALUES (%s, %s);
			"""
			for url in urls:
				cursor.execute( urllinks_insert_query, ( email_id, url ) )

			# Commit the transaction if everything is successful
			conn.commit()
			print( f"Data inserted successfully with email_id { email_id }." )

		except Exception as e:
			# Rollback the transaction in case of errors
			conn.rollback()
			print( "Transaction failed. Rolling back..." )
			print( "Error:", e )

	except Exception as e:
		print( "Database connection error:", e )

	finally:
		# Close database connection
		if cursor:
			cursor.close()
		if conn:
			conn.close()
		print( "Database connection closed." )

##############################################################
#
#	API
#

@app.get( "/" )
def read_root():
	return { "Hello": "World" }

@app.post( "/analyze-email" )
def analyze_email( data: EmailData ):

	sender = data.sender
	predText = data.subject + " " + data.body
	datetime = data.datetime

	# 	Check the sender email
	isSenderInvalid = not check_sender( sender )

	# 	Extract urls from the text
	urls = extract_urls( predText )

	# 	Check the urls are malicious or not
	isMalicious = check_url( urls )

	# 	Check the text is Phishing Email or Normal Email
	isPhishing = predict( predText, model, tokenizer )

	print( 'isSenderInvalid:', isSenderInvalid )
	print( 'isMalicious:', isMalicious )
	print( 'isPhishing:', isPhishing )

	# 	Return the result
	result = isSenderInvalid or isMalicious or isPhishing

	# 	Insert email data into the database
	data = {
		"sender": sender,
		"date": datetime,
		"subject": data.subject,
		"body": data.body,
		"label": int( result )
	}
	insert_email_to_db( data )

	return { 'result': result }

@app.post("/upload-email/")
def upload_email( email_file: EmailFile ):
	sender, subject, body, datetime = parse_eml_content( email_file.content )

	print( "\n📨 Received Email File 📩" )
	print( f"📂 File Name: {email_file.fileName}" )
	print( f"📧 Sender: {sender}" )
	print( f"📅 Date: {datetime}" )
	print( f"📜 Subject: {subject}" )
	print( f"📜 Body: {body[:1000]}..." )	# Display only first 1,000 characters of the body
	print( "\n-------------------------------\n")

	return {
		"message": "File processed successfully!",
		"sender": sender,
		"datetime": datetime,
		"subject": subject,
		"body": body
	}
