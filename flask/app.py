import os
from flask import Flask
from flask_cors import CORS

from endpoints.add_newsletter_user_graph import add_newsletter_user_graph_route
from endpoints.create_newsletter import create_newsletter_route
from endpoints.build_newsletter import build_newsletter_route
from endpoints.newsletter_build_check import newsletter_build_check_route
from endpoints.create_dormant_newsletter import create_dormant_newsletter_route
from endpoints.follow_user import follow_user_route
from endpoints.add_older_posts import add_older_posts_route
from endpoints.activate_dormant_newsletter import activate_dormant_newsletter_route
from endpoints.update_list import update_list_route
from endpoints.update_all_lists import update_all_lists_route
from endpoints.announce_newsletter import announce_newsletter_route
from endpoints.check_new_newsletters import check_new_newsletters_route

app = Flask(__name__)
CORS(app)

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

@app.route('/followUser', methods=['POST'])
def follow_users_route_wrapper():
    return follow_user_route()

@app.route('/addOlderPosts', methods=['POST'])
def add_older_posts_route_wrapper():
    return add_older_posts_route()

@app.route('/activateDormantNewsletter', methods=['POST'])
def activate_dormant_newsletter_route_wrapper():
    return activate_dormant_newsletter_route()

@app.route('/updateList', methods=['POST'])
def update_list_route_wrapper():
    return update_list_route()

@app.route('/updateAllLists', methods=['POST'])
def update_all_lists_route_wrapper():
    return update_all_lists_route()

@app.route('/announceNewsletter', methods=['POST'])
def announce_newsletter_route_wrapper():
    return announce_newsletter_route()

@app.route('/checkNewNewsletters', methods=['POST'])
def check_new_newsletters_route_wrapper():
    return check_new_newsletters_route()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# To run a local breakpoint debugger, uncomment this first.
# Add breakpoints
# Then do Run > Start Debugger
# if __name__ == '__main__':
#     app.run(debug=True, use_reloader=False)