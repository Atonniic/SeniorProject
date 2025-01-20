import psycopg2
from datetime import datetime
import re

def extractURLs(text):
    '''Extract URLs from string.'''
    urlPattern = r'(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+'
    urls = re.findall(urlPattern, text)
    return urls

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

# Sample data for insertion
data = {
    "sender": "example.sender@example.com",
    "receiver": "example.receiver@example.com",
    "date": "2025-01-20",
    "subject": "Test Email about technology and security",
    "label": "phishing",
    "body": "This is a sample email body with a URL: https://example.com and another http://test.com"
}

try:
    # Connect to PostgreSQL database
    conn = psycopg2.connect(
        "postgres://neondb_owner:PpIEst8Ql5VY@ep-restless-cloud-a1my0a20-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
    )
    cursor = conn.cursor()
    print("Connected to the database successfully.")

    # Start transaction
    conn.autocommit = False

    # Prepare data for insertion
    sender = data.get("sender")
    receiver = data.get("receiver")
    date = data.get("date")
    subject = data.get("subject")
    body = data.get("body")
    label = data.get("label")

    # Extract URLs from the body
    urls = extractURLs(body)

    # Determine category based on subject
    category = extendedCategorizeSubject(subject)

    try:
        # Convert date string to datetime object
        date = datetime.strptime(date, "%Y-%m-%d").date() if date else None

        # Insert email data into the `email` table
        email_insert_query = """
            INSERT INTO email (sender, receiver, date, subject, label, category)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING email_id;
        """
        cursor.execute(email_insert_query, (sender, receiver, date, subject, label, category))
        email_id = cursor.fetchone()[0]  # Get the generated email_id

        # Insert URLs into the `email_urllinks` table
        urllinks_insert_query = """
            INSERT INTO email_urllinks (email_id, urllink)
            VALUES (%s, %s);
        """
        for url in urls:
            cursor.execute(urllinks_insert_query, (email_id, url))

        # Commit the transaction if everything is successful
        conn.commit()
        print(f"Data inserted successfully with email_id {email_id}.")

    except Exception as e:
        # Rollback the transaction in case of errors
        conn.rollback()
        print("Transaction failed. Rolling back...")
        print("Error:", e)

except Exception as e:
    print("Database connection error:", e)

finally:
    # Close database connection
    if cursor:
        cursor.close()
    if conn:
        conn.close()
    print("Database connection closed.")
