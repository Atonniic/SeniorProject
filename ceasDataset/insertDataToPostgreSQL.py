import pandas as pd
import psycopg2
import ast  # ใช้สำหรับแปลง string เป็น list (ในกรณีที่ urlLinks เก็บในรูปแบบ string)
from datetime import datetime

try:
    # เชื่อมต่อกับ PostgreSQL
    conn = psycopg2.connect(
        "postgres://neondb_owner:PpIEst8Ql5VY@ep-restless-cloud-a1my0a20-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
    )
    cursor = conn.cursor()
    print("Connected to the database successfully.")

    # เริ่ม Transaction
    conn.autocommit = False

    # อ่านข้อมูลจาก CSV
    csv_file_path = r"D:\SeniorProject\ceasDataset\newClean\cleanCEAS04.csv"
    df = pd.read_csv(csv_file_path)

    # เลือกเฉพาะ 100 แถวแรก
    # df = df.head(100)

    # เตรียมข้อมูล
    rows_to_insert = []
    for index, row in df.iterrows():
        # ตรวจสอบและแปลง sender
        if isinstance(row['sender'], str) and row['sender'].startswith("["):
            sender_list = ast.literal_eval(row['sender'])  # แปลง string เป็น list
            sender = sender_list[0] if sender_list else None  # ดึงค่าหรือ None ถ้า list ว่างเปล่า
        else:
            sender = row['sender']

        # ตรวจสอบและแปลง receiver
        if isinstance(row['receiver'], str) and row['receiver'].startswith("["):
            receiver_list = ast.literal_eval(row['receiver'])  # แปลง string เป็น list
            receiver = receiver_list[0] if receiver_list else None  # ดึงค่าหรือ None ถ้า list ว่างเปล่า
        else:
            receiver = row['receiver']

        # ตรวจสอบและแปลง date
        date = row['date']
        try:
            # แปลง date เป็น datetime หากเป็นรูปแบบ YYYY-MM-DD
            date = datetime.strptime(date, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            # กรณีที่ date ไม่มีค่าหรือไม่ถูกต้อง
            date = None
            
        subject = row['subject']
        label = row['label']
        url_links = row['url_link']

        # ตรวจสอบและแปลง urlLinks
        urls = ast.literal_eval(url_links) if isinstance(url_links, str) and url_links.startswith("[") else [url_links]
        
        rows_to_insert.append((sender, receiver, date, subject, label, urls))

    # Insert ข้อมูลลงตาราง email
    email_insert_query = """
        INSERT INTO email (sender, receiver, date, subject, label)
        VALUES (%s, %s, %s, %s, %s) RETURNING email_id;
    """
    urllinks_insert_query = """
        INSERT INTO email_urllinks (email_id, urllink)
        VALUES (%s, %s);
    """

    try:
        for i, row in enumerate(rows_to_insert, start=1):
            sender, receiver, date, subject, label, urls = row

            # Insert ข้อมูลในตาราง email
            cursor.execute(email_insert_query, (sender, receiver, date, subject, label))
            email_id = cursor.fetchone()[0]  # ดึง email_id ที่เพิ่งสร้าง

            # Insert URL ลงในตาราง email_urllinks
            for url in urls:
                cursor.execute(urllinks_insert_query, (email_id, url))

            # Log การ Insert
            print(f"Inserted email ({i}/{len(rows_to_insert)}) with email_id {email_id} successfully.")

        # Commit ข้อมูลทั้งหมดหากไม่มีข้อผิดพลาด
        conn.commit()
        print("All data committed successfully.")

    except Exception as e:
        # Rollback หากเกิดข้อผิดพลาด
        conn.rollback()
        print("Transaction failed. Rolling back...")
        print("Error:", e)

except Exception as e:
    print("Error:", e)

finally:
    # ปิดการเชื่อมต่อ
    if cursor:
        cursor.close()
    if conn:
        conn.close()
    print("Database connection closed.")
