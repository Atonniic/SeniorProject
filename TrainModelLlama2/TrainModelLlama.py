from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments, DataCollatorForLanguageModeling, AutoModelForSequenceClassification
from safetensors.torch import load_model, save_model
from torch import nn
from datasets import DatasetDict, Dataset
from sklearn.model_selection import train_test_split
import pandas as pd
import torch

#	Load tokenizer and model
model_name = "meta-llama/Llama-3.2-1B"
tokenizer = AutoTokenizer.from_pretrained( model_name )
base_model = AutoModelForCausalLM.from_pretrained( model_name )

if tokenizer.pad_token is None:
	tokenizer.pad_token = tokenizer.eos_token

#	ปรับขนาด embedding ของโมเดลให้สอดคล้องกับ tokenizer
base_model.resize_token_embeddings(len(tokenizer))

print( 'tokenizer:', len( tokenizer ) )
print( 'base_model:', base_model.config.vocab_size )
print( 'tokenizer:', tokenizer.vocab_size )

#	ตรวจสอบขนาดของ vocab
assert len( tokenizer ) == base_model.config.vocab_size, "Vocab size mismatch!"

class LlamaForSequenceClassification( nn.Module ):

	def __init__( self, base_model, num_labels ):

		super( LlamaForSequenceClassification, self ).__init__()
		self.base_model = base_model
		self.classification_head = nn.Linear( base_model.config.hidden_size, num_labels )

	def forward( self, input_ids, attention_mask = None, labels = None, label = None ):

		labels = labels if labels is not None else label

		#	Use hidden state at first position (CLS token) as input of classification head
		outputs = self.base_model( input_ids = input_ids, attention_mask = attention_mask, output_hidden_states = True )
		logits = self.classification_head( outputs.hidden_states[ -1 ][ :, 0 ] )
		
		#	Calculate Loss ( If has labels )
		loss = None
		if labels is not None:

			if labels.dim() > 1:
				labels = torch.argmax( labels, dim = 1 )

			loss_fn = nn.CrossEntropyLoss()
			loss = loss_fn( logits, labels )
		
		return {"loss": loss, "logits": logits}

#	Create model include classification head
num_labels = 2  # Number of class ( Eg. 2 for binary classification )
model = LlamaForSequenceClassification( base_model, num_labels )

def preprocess_function( examples ):

	tokenized_inputs = tokenizer(
		examples[ 'text' ], 
		truncation = True, 
		padding = 'max_length', 
		max_length = 512
	)

	# Add labels
	tokenized_inputs[ "labels" ] = examples[ "label" ]
	return tokenized_inputs

# 	Prepare data
def prepare_data( file_paths ):

	#	Load data from csv file
	dataframes = [ pd.read_csv( file_path ) for file_path in file_paths ]

	#	Combine data
	combined_data = pd.concat( dataframes, ignore_index = True )

	#	Create 'text' column by combine sender, receiver, subject, and body
	combined_data[ 'text' ] = (
		# combined_data[ 'sender' ].fillna( '' ) + ' ' +
		# combined_data[ 'receiver' ].fillna( '' ) + ' ' +
		combined_data[ 'subject' ].fillna( '' ) + ' ' +
		combined_data[ 'body' ].fillna( '' )
	)

	#	Choose only 'text' and 'label' column
	combined_data = combined_data[ [ 'text', 'label' ] ]

	#	Split data to train and test data
	train_texts, test_texts, train_labels, test_labels = train_test_split(
		combined_data[ 'text' ], combined_data[ 'label' ], test_size = 0.2, random_state = 42
	)

	#	Convert data to pandas DataFrame
	train_data = pd.DataFrame( {'text': train_texts, 'label': train_labels} )
	test_data = pd.DataFrame( {'text': test_texts, 'label': test_labels} )

	#	Convert pandas DataFrame to Hugging Face Dataset
	return DatasetDict({
		'train': Dataset.from_pandas( train_data ),
		'test': Dataset.from_pandas( test_data )
	})

file_paths = [
	# "../ceasDataset/orig/CEAS00.csv",	# For test script 
	"../ceasDataset/orig/CEAS01.csv", 
	"../ceasDataset/orig/CEAS02.csv", 
	"../ceasDataset/orig/CEAS03.csv",
	"../ceasDataset/orig/CEAS04.csv"
]

data = prepare_data( file_paths )

#	Use DatasetDict for train/test
encoded_data = data.map( preprocess_function, batched = True)

training_args = TrainingArguments(
	output_dir = "./llama-sequence-classification-new",
	evaluation_strategy = "epoch",
	learning_rate = 2e-5,
	per_device_train_batch_size = 4,
	per_device_eval_batch_size = 4,
	num_train_epochs = 3,
	weight_decay = 0.01,
	logging_dir = "./logs-new",
	save_strategy = "epoch",
	load_best_model_at_end = True,
	save_safetensors = False
)

data_collator = DataCollatorForLanguageModeling(
	tokenizer = tokenizer,
	mlm = True,  # ใช้ False สำหรับ causal language modeling
)

trainer = Trainer(
	model = model,
	args = training_args,
	train_dataset = encoded_data["train"],
	eval_dataset = encoded_data["test"],
	tokenizer = tokenizer,
	data_collator = data_collator
)

trainer.train()

trainer.save_model( "./llama-sequence-classification-new" )
tokenizer.save_pretrained( "./llama-sequence-classification-new" )
# save_model( model, "./llama-sequence-classification-finish" )
# model.save_pretrained( "./llama-pretrained-sequence-classification-finish" )
