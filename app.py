from flask import Flask, request, Response, stream_with_context
import os
from endpoints.add_newsletter_user_graph import add_newsletter_user_graph
from endpoints.create_newsletter import create_newsletter_route

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World! This is a Flask app running on Cloud Run!'

@app.route('/addNewsletterUserGraph', methods=['POST'])
def add_newsletter_user_graph_route():
    """
    POST endpoint to add newsletter user graph data.
    
    Expected JSON payload:
    {
        "url": "string",
        "subdomain": "string", 
        "publication_id": "string"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return {"error": "No JSON data provided"}, 400
            
        url = data.get('url')
        subdomain = data.get('subdomain')
        publication_id = data.get('publication_id')
        
        if not all([url, subdomain, publication_id]):
            return {"error": "Missing required parameters: url, subdomain, publication_id"}, 400
        
        result = add_newsletter_user_graph(url, subdomain, publication_id)
        
        if result["status"] == "success":
            return result, 200
        else:
            return result, 500
            
    except Exception as e:
        return {"error": f"Internal server error: {str(e)}"}, 500

@app.route('/createNewsletter', methods=['POST'])
def create_newsletter_route_wrapper():
    return create_newsletter_route()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080))) 