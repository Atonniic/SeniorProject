from email import policy
from email.parser import BytesParser
import argparse
import re
from bs4 import BeautifulSoup
from datetime import datetime

def ExtractURLs( text ):
    '''Extract URLs from string.'''
    urlPattern = r'(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+'
    urls = re.findall( urlPattern, text )
    return urls

def GetBody( msg ):
    '''Extract the body of an email.'''
    body = ""
    if msg.is_multipart():
        for part in msg.iter_parts():
            contentType = part.get_content_type()
            try:
                if contentType == "text/plain":
                    body = part.get_payload( decode=True ).decode( part.get_content_charset() )
                    break
                elif contentType == "text/html":
                    htmlContent = part.get_payload( decode=True ).decode( part.get_content_charset() )
                    soup = BeautifulSoup( htmlContent, 'html.parser' )
                    body = soup.get_text()
            except Exception as e:
                print( f"Error processing part with content type {contentType}: {e}" )
    else:
        contentType = msg.get_content_type()
        try:
            if contentType == "text/plain":
                body = msg.get_payload( decode=True ).decode( msg.get_content_charset() )
            elif contentType == "text/html":
                htmlContent = msg.get_payload( decode=True ).decode( msg.get_content_charset() )
                soup = BeautifulSoup( htmlContent, 'html.parser' )
                body = soup.get_text()
        except Exception as e:
            print( f"Error processing email body: {e}" )
    return body.strip() if body else "No body content found."

def ExtractEmail( headerValue ):
    '''Extract the email address from a header value.'''
    email_match = re.search( r'<([^>]+)>', headerValue )
    if email_match:
        return email_match.group( 1 )  # Return only the email inside <>
    else:
        return headerValue.strip()  # Return as-is if no <>
    
def ConvertDate( dateStr ):
	'''	Convert date string
	'''

	try:
		#	Parse the input date string with the given format
		parsedDate = datetime.strptime( dateStr, '%a, %d %b %Y %H:%M:%S %z' )

	except ValueError:
		return None

	#	Convert to desired format 'YYYY-MM-DD'
	return parsedDate.strftime( '%Y-%m-%d %H:%M:%S' )    
    
def ParseEML( filePath ):
    with open( filePath, 'rb' ) as emlFile:
        msg = BytesParser( policy=policy.default ).parse( emlFile )


    fromEmail = ExtractEmail( msg['From'] ) if msg['From'] else "No From found"

    print( f"From        -> { fromEmail }" )
    print( f"Subject     -> { msg[ 'Subject' ] }" )
    print( f"Date        -> { ConvertDate( msg[ 'Date' ] ) }" )
    print( f"URLs        -> { ExtractURLs( GetBody( msg ) ) if GetBody( msg ) else 'No URLs found' }" )
    print( f"Body        ->\n{ GetBody( msg ) if GetBody( msg ) else 'No body found' }" )

if __name__ == "__main__":
    parser = argparse.ArgumentParser( description="Extract information from a .eml file." )
    parser.add_argument( "file", help="Path to the .eml file" )
    args = parser.parse_args()

    ParseEML( args.file )
