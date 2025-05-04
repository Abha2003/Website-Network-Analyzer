import socket
import ssl
import requests
import whois
import json

def analyze_website(url):
    if not url.startswith("http"):
        url = "http://" + url

    response = requests.get(url, timeout=5)
    ip = socket.gethostbyname(url.split('//')[-1].split('/')[0])

    return {
        'ip': ip,
        'protocol': response.raw.version,
        'status_code': response.status_code,
        'response_time': response.elapsed.total_seconds(),
    }

def get_dns_info(url):
    try:
        ip = socket.gethostbyname(url.split('//')[-1])
        return {'A': ip}
    except Exception as e:
        return {'error': f'DNS lookup failed: {str(e)}'}

def get_ssl_info(url):
    try:
        hostname = url.split('//')[-1]
        context = ssl.create_default_context()
        with context.wrap_socket(socket.socket(), server_hostname=hostname) as sock:
            sock.settimeout(3)
            sock.connect((hostname, 443))
            cert = sock.getpeercert()
        return cert
    except Exception as e:
        return {'error': f'SSL info retrieval failed: {str(e)}'}

def get_whois_info(url):
    try:
        domain = url.split('//')[-1].split('/')[0]
        w = whois.whois(domain)
        return {'domain_name': w.domain_name, 'creation_date': str(w.creation_date), 'expiry': str(w.expiration_date)}
    except Exception as e:
        return {'error': f'WHOIS lookup failed: {str(e)}'}

def get_ip_geolocation(url):
    try:
        ip = socket.gethostbyname(url.split('//')[-1])
        response = requests.get(f"http://ip-api.com/json/{ip}").json()
        return {
            'country': response.get('country'),
            'region': response.get('regionName'),
            'city': response.get('city'),
            'isp': response.get('isp')
        }
    except Exception as e:
        return {'error': f'IP Geolocation failed: {str(e)}'}
