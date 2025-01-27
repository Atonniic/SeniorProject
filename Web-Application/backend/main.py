from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import re
import requests
import os
from dotenv import load_dotenv

app = FastAPI()

#	Setting CORS
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# 	Load Model & Tokenizer
base_model = AutoModelForCausalLM.from_pretrained( "meta-llama/Llama-3.2-1B" )
model = PeftModel.from_pretrained( base_model, "apkmew/LlamaPhishing" )
tokenizer = AutoTokenizer.from_pretrained( "apkmew/LlamaPhishing" )

#     Load .env
load_dotenv( '../../.env' )
hunterioApiKey = os.getenv( 'hunterio_apikey' )
xApiKeys = os.getenv( 'x_apikey' )

print( 'hunter.io API Key:', hunterioApiKey )
print( 'VirusTotal API Key:', xApiKeys )

##############################################################
#
#	Class OOP
#

class EmailData( BaseModel ):
	sender: str
	subject: str
	body: str

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

	return { 'result': result }
