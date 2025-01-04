from email import policy
from email.parser import BytesParser
import geoip2.database
import argparse
import re
from bs4 import BeautifulSoup
from datetime import datetime

def ExtractURLs( text ):
    '''Extract URLs from string.'''
    urlPattern = r'(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+'
    urls = re.findall( urlPattern, text )
    return urls

def ExtractSenderIP( receivedHeaders ):
    '''Extract sender's IP address from Received headers.'''
    for received in receivedHeaders:
        ipMatch = re.search( r'\[([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\]', received )
        if ipMatch:
            return ipMatch.group( 1 )
    return None

def GetSenderIP( msg ):
    '''Extract the sender's IP address from the email.'''
    receivedHeaders = msg.get_all('Received')
    if receivedHeaders:
        senderIP = ExtractSenderIP( receivedHeaders )
        return ( True, senderIP )
    else:
        return ( False, None )

def GetLocations( ipAddresses ):
    '''Get the location of the IP addresses.'''
    reader = geoip2.database.Reader( 'GeoLite2-City_20241224/GeoLite2-City.mmdb' )
    response = reader.city( ipAddresses )
    if response:
        location = response.country.name
    else:
        location = None
    return location

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

def ParseAuthenticationResults( msg ):
    '''Extract SPF, DKIM, and DMARC results.'''
    spf = dkim = dmarc = None
    authResults = msg.get( 'Authentication-Results' )
    if authResults:
        authResultsLower = authResults.lower()
        if 'spf=pass' in authResultsLower:
            spf = 1
        elif 'spf=fail' in authResultsLower:
            spf = 0

        if 'dkim=pass' in authResultsLower:
            dkim = 1
        elif 'dkim=fail' in authResultsLower:
            dkim = 0

        if 'dmarc=pass' in authResultsLower:
            dmarc = 1
        elif 'dmarc=fail' in authResultsLower:
            dmarc = 0

    return spf, dkim, dmarc

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
	return parsedDate.strftime( '%Y-%m-%d' )

def ParseEML( filePath ):
    with open( filePath, 'rb' ) as emlFile:
        msg = BytesParser( policy=policy.default ).parse( emlFile )

    spf, dkim, dmarc = ParseAuthenticationResults( msg )

    fromEmail = ExtractEmail( msg['From'] ) if msg['From'] else "No From found"
    toEmail = ExtractEmail( msg['To'] ) if msg['To'] else "No To found"

    print( f"From        -> { fromEmail }" )
    print( f"To          -> { toEmail }" )
    print( f"Subject     -> { msg[ 'Subject' ] }" )
    print( f"Date        -> { ConvertDate( msg[ 'Date' ] ) }" )
    print( f"Sender's IP -> { GetSenderIP( msg )[ 1 ] if GetSenderIP( msg )[ 0 ] else 'No IP found' }" )
    print( f"Locations   -> { GetLocations( GetSenderIP( msg )[ 1 ] ) if GetSenderIP( msg )[ 0 ] else 'No location found' }" )
    print( f"SPF         -> { spf if spf is not None else 'NULL' }" )
    print( f"DKIM        -> { dkim if dkim is not None else 'NULL' }" )
    print( f"DMARC       -> { dmarc if dmarc is not None else 'NULL' }" )
    print( f"URLs        -> { ExtractURLs( GetBody( msg ) ) if GetBody( msg ) else 'No URLs found' }" )
    print( f"Body        ->\n{ GetBody( msg ) if GetBody( msg ) else 'No body found' }" )

if __name__ == "__main__":
    parser = argparse.ArgumentParser( description="Extract information from a .eml file." )
    parser.add_argument( "file", help="Path to the .eml file" )
    args = parser.parse_args()

    ParseEML( args.file )
