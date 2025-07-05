from flask import Flask, request, Response, stream_with_context
import os
from endpoints.add_newsletter_user_graph import add_newsletter_user_graph_route
from endpoints.create_newsletter import create_newsletter_route
from endpoints.build_newsletter import build_newsletter_route
from endpoints.newsletter_build_check import newsletter_build_check_route

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World! This is a Flask app running on Cloud Run!'

@app.route('/addNewsletterUserGraph', methods=['POST'])
def add_newsletter_user_graph_route_wrapper():
    return add_newsletter_user_graph_route()

@app.route('/createNewsletter', methods=['POST'])
def create_newsletter_route_wrapper():
    return create_newsletter_route()

@app.route('/buildNewsletter', methods=['POST'])
def build_newsletter_route_wrapper():
    return build_newsletter_route()

@app.route('/newsletterBuildCheck', methods=['POST'])
def newsletter_build_check_route_wrapper():
    return newsletter_build_check_route()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080))) 