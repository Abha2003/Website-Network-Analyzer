import socket
import ssl
import requests
import re
from urllib.parse import urlparse
import dns.resolver

# Website Analysis Functions

def is_valid_url(url):
    pattern = re.compile(r'^(https?://)?([a-zA-Z0-9_-]+\.)+[a-zA-Z]{2,}')
    return re.match(pattern, url) is not None

def get_dns_info(domain):
    try:
        result = dns.resolver.resolve(domain, 'A')
        return [ip.address for ip in result]
    except Exception as e:
        return f"Error fetching DNS info: {e}"

def get_ssl_info(domain):
    try:
        context = ssl.create_default_context()
        conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=domain)
        conn.connect((domain, 443))
        cert = conn.getpeercert()
        conn.close()
        return cert
    except Exception as e:
        return f"Error fetching SSL info: {e}"

def get_http_security_headers(url):
    try:
        response = requests.head(url, timeout=10)
        headers = response.headers
        security_headers = {
            "Strict-Transport-Security": headers.get('Strict-Transport-Security'),
            "Content-Security-Policy": headers.get('Content-Security-Policy'),
            "X-Content-Type-Options": headers.get('X-Content-Type-Options'),
            "X-Frame-Options": headers.get('X-Frame-Options'),
            "X-XSS-Protection": headers.get('X-XSS-Protection'),
            "Referrer-Policy": headers.get('Referrer-Policy'),
            "Feature-Policy": headers.get('Feature-Policy')
        }
        return {key: value for key, value in security_headers.items() if value is not None}
    except Exception as e:
        return {"error": f"Error fetching headers: {str(e)}"}

def get_redirect_chain(url):
    try:
        response = requests.get(url, allow_redirects=True, timeout=10)
        chain = [resp.url for resp in response.history]
        if response.url not in chain:
            chain.append(response.url)
        return chain
    except Exception as e:
        return [f"Redirect error: {str(e)}"]

def get_trackers(url):
    # For now, just a placeholder
    return ["Tracker 1", "Tracker 2"]
