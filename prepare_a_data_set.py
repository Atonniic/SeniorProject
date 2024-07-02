import pandas as pd
from sklearn.model_selection import train_test_split

# อ่านไฟล์ข้อมูล
non_phishing_df = pd.read_csv('Non-Phishing.csv')
phishing_df = pd.read_csv('Phishing.csv')

# จัดการคอลัมน์ให้สอดคล้องกัน
# เรียงคอลัมน์ให้เหมือนกัน: sender, receiver, date, subject, body, urls, label
non_phishing_df = non_phishing_df[['sender', 'receiver', 'date', 'subject', 'body', 'urls', 'label']]
phishing_df = phishing_df[['sender', 'receiver', 'date', 'subject', 'body', 'urls', 'label']]

# ผสมข้อมูลจากสองไฟล์
all_emails = pd.concat([non_phishing_df, phishing_df], ignore_index=True)

# แบ่งข้อมูลเป็นชุดฝึกและชุดทดสอบ
X = all_emails.drop('label', axis=1)
y = all_emails['label']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, shuffle=True)

# แสดงผลลัพธ์
print("Training set size:", X_train.shape[0])
print("Test set size:", X_test.shape[0])

# บันทึกชุดข้อมูลฝึกและทดสอบลงไฟล์
X_train.to_csv('Training_Set.csv', index=False)
y_train.to_csv('Training_Labels.csv', index=False)
X_test.to_csv('Test_Set.csv', index=False)
y_test.to_csv('Test_Labels.csv', index=False)
