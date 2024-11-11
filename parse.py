import re

# Regular expression for URLs (supporting different protocols, IPs, localhost, and optional ports)
url_pattern = re.compile(
    r'\b(?:[a-zA-Z][a-zA-Z0-9+.-]*://|www\.)'    # Protocol (e.g., http://) or www
    r'(?:(?:\d{1,3}\.){3}\d{1,3}|'                # IP Address
    r'localhost|'                                 # Localhost
    r'(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,})'         # Domain
    r'(?::\d{1,5})?'                              # Optional Port
    r'(?:/[^\s]*)?'                               # Path
)

# Regular expression for emails
email_pattern = re.compile(
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
)

# Regular expression for phone numbers (basic formats)
phone_pattern = re.compile(
    r'\b(?:\+?\d{1,3}[-.\s]?)?'          # Country code (optional)
    r'(?:\(?\d{2,4}\)?[-.\s]?)?'         # Area code (optional)
    r'\d{3,4}[-.\s]?\d{3,4}\b'           # Main number
)



def extract_info(text):
    urls = url_pattern.findall(text)
    emails = email_pattern.findall(text)
    phones = phone_pattern.findall(text)

    return {
        "urls": urls,
        "emails": emails,
        "phones": phones
    }

# Example usage
if __name__ == "__main__":
    text = """
    Here are some test examples:
    Visit http://example.com or https://localhost:8080/path for info. 
    Contact us at test@example.com or call +1-800-555-1234, (123) 456-7890, or 555-6789.
    """
    
    result = extract_info(text)
    print("URLs:", result["urls"])
    print("Emails:", result["emails"])
    print("Phones:", result["phones"])
