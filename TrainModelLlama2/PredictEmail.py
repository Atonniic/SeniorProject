from transformers import AutoTokenizer, LlamaForSequenceClassification
import torch

# โหลด Tokenizer และโมเดล
MODEL_PATH = "./llama-sequence-classification"  # เปลี่ยนเป็น path ของโมเดลที่คุณต้องการใช้
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = LlamaForSequenceClassification.from_pretrained(MODEL_PATH)

# เพิ่มโทเคนพิเศษใน tokenizer (ถ้าจำเป็น)
tokenizer.add_special_tokens({'pad_token': '[PAD]'})

# อัปเดต embedding layer ของโมเดลให้รองรับ vocab_size ของ tokenizer
model.resize_token_embeddings(len(tokenizer))

# เตรียมข้อความที่ต้องการจำแนก
texts = [
    """
From: fakebank@example.com
To: user@example.com
Subject: Urgent: Verify Your Account

Dear User,

We noticed suspicious activity in your account. Please verify your details immediately by clicking the link below.

[Verify Now](http://phishingsite.com)

Thank you,
Support Team
"""
]

# Tokenize ข้อความ
inputs = tokenizer(
    texts,
    padding=True,              # เติม padding ให้มีขนาดเท่ากัน
    truncation=True,           # ตัดข้อความที่ยาวเกินไป
    return_tensors="pt"       # คืนค่าเป็น PyTorch tensor
)

print("Input IDs:", inputs["input_ids"])
# vocab_size = tokenizer.vocab_size
vocab_size = len( tokenizer )
print("Vocab Size:", vocab_size)

if (inputs["input_ids"] >= vocab_size).any():
    print("พบค่าที่เกิน vocab_size")
else:
    print("ไม่มีค่าที่เกินขอบเขต")

# ดูขนาด vocab_size ของโมเดล
print("Model vocab size:", model.config.vocab_size)

# print( 'tokenizer:', tokenizer.vocab_size )
# print( 'model:', model.config.vocab_size )
# print( 'tokenizer:', len( tokenizer ) )

# model.config.vocab_size = tokenizer.vocab_size

# ตรวจสอบว่า vocab_size ตรงกันหรือไม่
# assert tokenizer.vocab_size == model.config.vocab_size, "vocab_size ของ tokenizer และ model ไม่ตรงกัน"
assert len( tokenizer ) == model.config.vocab_size, "vocab_size ของ tokenizer และ model ไม่ตรงกัน"


# ส่งข้อมูลเข้าโมเดล
with torch.no_grad():
    outputs = model(**inputs)

# ดึงค่า logits และคำนวณ softmax
logits = outputs.logits
probs = torch.nn.functional.softmax(logits, dim=-1)

# แสดงผลลัพธ์
for i, text in enumerate(texts):
    print(f"ข้อความ: {text}")
    print(f"ความน่าจะเป็น (probabilities): {probs[i].tolist()}")
    print(f"ประเภทที่คาดการณ์: {torch.argmax(probs[i]).item()}\n")
