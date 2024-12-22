import pandas as pd
import psycopg2
import ast  # ใช้สำหรับแปลง string เป็น list (ในกรณีที่ urlLinks เก็บในรูปแบบ string)

# เชื่อมต่อกับ PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="mydatabase",
    user="myuser",
    password="mypassword"
)

cursor = conn.cursor()
print(cursor)

exit(-1)

# อ่านข้อมูลจาก CSV
csv_file = "your_file.csv"  # ระบุชื่อไฟล์ CSV
df = pd.read_csv(csv_file)

# เลือกเฉพาะ 2 แถวแรก
df = df.head(2)

# เตรียมข้อมูลสำหรับการ INSERT
rows_to_insert = []
for index, row in df.iterrows():
    sender = row['sender']
    receiver = row['receiver']
    date = row['date']
    subject = row['subject']
    label = row['label']
    url_links = row['urlLinks']

    # ตรวจสอบและแปลง urlLinks (ถ้าเป็น list ให้แยกออก)
    urls = ast.literal_eval(url_links) if isinstance(url_links, str) and url_links.startswith("[") else [url_links]

    for url in urls:
        rows_to_insert.append((sender, receiver, date, subject, label, url))

# สร้างคำสั่ง INSERT
insert_query = """
    INSERT INTO email (sender, receiver, date, subject, label, urlLink)
    VALUES (%s, %s, %s, %s, %s, %s)
"""

# Execute และ Commit เฉพาะ 2 แถวแรก
cursor.executemany(insert_query, rows_to_insert)
conn.commit()

print(f"Inserted {len(rows_to_insert)} rows successfully.")

# ปิดการเชื่อมต่อ
cursor.close()
conn.close()
