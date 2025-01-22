from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

class EmailData(BaseModel):
    sender: str
    recipient: str
    subject: str
    body: str

# ตั้งค่า CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # อนุญาตทุก origin หรือเปลี่ยนเป็น ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],  # อนุญาตทุก Method
    allow_headers=["*"],  # อนุญาตทุก Header
)

@app.post("/analyze-email")
def analyze_email(data: EmailData):
    result = {
        "sender": data.sender,
        "subject": data.subject,
        "body_length": len(data.body),
        "is_phishing": False  # ตัวอย่าง output
    }
    return result
