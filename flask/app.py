from flask import Flask, request, Response, stream_with_context
import os
from endpoints.add_newsletter_user_graph import add_newsletter_user_graph_route
from endpoints.create_newsletter import create_newsletter_route
from endpoints.build_newsletter import build_newsletter_route
from endpoints.newsletter_build_check import newsletter_build_check_route
from endpoints.create_dormant_newsletter import create_dormant_newsletter_route
from endpoints.follow_users import follow_users_route
from endpoints.add_older_posts import add_older_posts_route

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

@app.route('/createDormantNewsletter', methods=['POST'])
def create_dormant_newsletter_route_wrapper():
    return create_dormant_newsletter_route()

@app.route('/followUsers', methods=['POST'])
def follow_users_route_wrapper():
    return follow_users_route()

@app.route('/addOlderPosts', methods=['POST'])
def add_older_posts_route_wrapper():
    return add_older_posts_route()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# To run a local breakpoint debugger, uncomment this first.
# Add breakpoints
# Then do Run > Start Debugger
# if __name__ == '__main__':
#     app.run(debug=True, use_reloader=False)