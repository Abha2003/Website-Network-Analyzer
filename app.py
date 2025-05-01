from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging

# 👇 Replace these with the actual files where your functions are defined
from network_tools import analyze_website, get_dns_info, get_ssl_info, is_valid_url
import re

def is_valid_url(url):
    pattern = re.compile(
        r'^(https?://)?'          # optional http or https
        r'(([a-zA-Z0-9_-]+\.)+[a-zA-Z]{2,})'  # domain
        r'(/.*)?$'                # optional path
    )
    return re.match(pattern, url) is not None

app = Flask(__name__)
app.secret_key = 'your-secret-key'

limiter = Limiter(get_remote_address, app=app, default_limits=[])

class WebsiteForm(FlaskForm):
    website = StringField('Website URL', validators=[DataRequired()])
    submit = SubmitField('Analyze')

@app.template_filter('format_dict')
def format_dict(value):
    if isinstance(value, dict):
        output = ""
        for k, v in value.items():
            if isinstance(v, (list, tuple)):
                output += f"<strong>{k}:</strong><ul>"
                for item in v:
                    output += f"<li>{item}</li>"
                output += "</ul>"
            elif isinstance(v, dict):
                output += f"<strong>{k}:</strong><br>" + format_dict(v)
            else:
                output += f"<strong>{k}:</strong> {v}<br>"
        return output
    elif isinstance(value, (list, tuple)):
        return "<br>".join(str(item) for item in value)
    return str(value)


@app.route('/', methods=['GET', 'POST'])
def homepage():
    form = WebsiteForm()
    result = None
    analyzed = False

    if request.method == 'POST' and form.validate_on_submit():
        website_url = form.website.data
        if is_valid_url(website_url):
            try:
                domain = website_url.split("//")[-1].split("/")[0]
                result = analyze_website(website_url)
                result['dns'] = get_dns_info(domain)
                result['ssl'] = get_ssl_info(domain)
                analyzed = True
            except Exception as e:
                result = {'error': str(e)}
        else:
            result = {'error': 'Invalid URL. Must start with http:// or https://'}

    return render_template('analyzer_home.html', form=form, result=result, analyzed=analyzed)

if __name__ == '__main__':
    import webbrowser
    from threading import Timer

    def open_browser():
        webbrowser.open_new('http://127.0.0.1:5000')

    # Open the browser after a 1-second delay
    Timer(1, open_browser).start()

    # Run app with reloader disabled to prevent double execution
    app.run(debug=True, use_reloader=False)