from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import ssl
import socket
from urllib.parse import urlparse
import requests
import threading
from network_tools import get_dns_info, get_ssl_info, is_valid_url, get_http_security_headers, get_redirect_chain, get_trackers
from packet_sniffer import start_sniffing
import webbrowser
import time

app = Flask(__name__)
app.secret_key = 'your-secret-key'
limiter = Limiter(get_remote_address, app=app, default_limits=[])

class WebsiteForm(FlaskForm):
    website = StringField('Website URL', validators=[DataRequired()])
    submit = SubmitField('Analyze')

def analyze_website(url):
    try:
        response = requests.get(url, timeout=10)
        return {
            "status_code": response.status_code,
            "content_type": response.headers.get("Content-Type"),
            "response_time": response.elapsed.total_seconds()
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"Error analyzing website: {str(e)}"}

def get_tls_version(domain):
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                return ssock.version()
    except Exception as e:
        return f"Error fetching TLS version: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def homepage():
    form = WebsiteForm()
    result = {}
    analyzed = False
    sniffed_packets = []

    if request.method == 'POST' and form.validate_on_submit():
        website_url = form.website.data
        if is_valid_url(website_url):
            try:
                domain = website_url.split("//")[-1].split("/")[0]
                result = analyze_website(website_url)
                result['dns'] = get_dns_info(domain)
                result['ssl'] = get_ssl_info(domain)
                result['tls_version'] = get_tls_version(domain)
                result['redirect_chain'] = get_redirect_chain(website_url)
                result['trackers'] = get_trackers(website_url)
                result['security_headers'] = get_http_security_headers(website_url)

                sniffed_packets = start_sniffing(packet_count=10)

                analyzed = True
            except Exception as e:
                result = {'error': str(e)}
        else:
            result = {'error': 'Invalid URL. Must start with http:// or https://'}

    return render_template("analyzer_home.html", form=form, analyzed=analyzed, result=result, sniffed_packets=sniffed_packets)

@app.route('/info')
def info_page():
    return render_template('info.html')

if __name__ == '__main__':
    def open_browser():
        time.sleep(1)
        webbrowser.open("http://127.0.0.1:5000")

    threading.Thread(target=open_browser).start()
    app.run(debug=True, use_reloader=False)
