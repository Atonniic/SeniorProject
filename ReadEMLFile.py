from email import policy
from email.parser import BytesParser
import geoip2.database
import argparse
import re
from bs4 import BeautifulSoup

def extract_urls(text):
    '''Extract URLs from string.'''
    
    # Define the regular expression for URL extraction
    url_pattern = r'(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+'
    # Find all matches of the pattern in the text
    urls = re.findall(url_pattern, text)
    return urls

def extract_sender_ip(received_headers):
    '''Extract sender's IP address from Received headers.'''
    
    for received in received_headers:
        # Use regex to find IP addresses in the Received headers
        ip_match = re.search(r'\[([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\]', received)
        if ip_match:
            return ip_match.group(1)
    return None

def getSenderIP(msg):
    '''Extract the sender's IP address from the email.'''
        
    received_headers = msg.get_all('Received')
    if received_headers:
        sender_ip = extract_sender_ip(received_headers)
        return ( True, sender_ip )
    else:
        return ( False, None )
        
def getLocations(ip_addresses):
    '''Get the location of the IP addresses.'''
        
    reader = geoip2.database.Reader('GeoLite2-City_20241224/GeoLite2-City.mmdb')
    response = reader.city(ip_addresses)
    
    if response:
        location = response.country.name
    else:
        location = None
            
    return location
    
def getBody(msg):
    '''Extract the body of an email.'''
    
    body = ""
    if msg.is_multipart():
        for part in msg.iter_parts():
            content_type = part.get_content_type()
            try:
                if content_type == "text/plain":
                    # Return plain text directly
                    body = part.get_payload(decode=True).decode(part.get_content_charset())
                    break  # Stop after finding plain text
                elif content_type == "text/html":
                    # Convert HTML to plain text
                    html_content = part.get_payload(decode=True).decode(part.get_content_charset())
                    soup = BeautifulSoup(html_content, 'html.parser')
                    body = soup.get_text()
            except Exception as e:
                print(f"Error processing part with content type {content_type}: {e}")
    else:
        # Single part email
        content_type = msg.get_content_type()
        try:
            if content_type == "text/plain":
                body = msg.get_payload(decode=True).decode(msg.get_content_charset())
            elif content_type == "text/html":
                html_content = msg.get_payload(decode=True).decode(msg.get_content_charset())
                soup = BeautifulSoup(html_content, 'html.parser')
                body = soup.get_text()
        except Exception as e:
            print(f"Error processing email body: {e}")

    # Return the processed body
    return body.strip() if body else "No body content found."

def parse_eml(file_path):
    # Open and parse the .eml file
    with open(file_path, 'rb') as eml_file:
        msg = BytesParser(policy=policy.default).parse(eml_file)

    print(f"From        -> {msg['From']}")
    print(f"To          -> {msg['To']}")
    print(f"Subject     -> {msg['Subject']}")
    print(f"Date        -> {msg['Date']}")
    print(f"Sender's IP -> {getSenderIP(msg)[1] if getSenderIP(msg)[0] else 'No IP found'}")
    print(f"Locations   -> {getLocations(getSenderIP(msg)[1]) if getSenderIP(msg)[0] else 'No location found'}")
    print(f"URLs        -> {extract_urls(getBody(msg)) if getBody(msg) else 'No URLs found'}")
    print(f"Body        ->\n{getBody(msg) if getBody(msg) else 'No body found'}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract information from a .eml file.")
    parser.add_argument("file", help="Path to the .eml file")
    args = parser.parse_args()

    parse_eml(args.file)
