from flask import Blueprint, request, jsonify
from speech_service import speak
from flask import Flask


routes = Blueprint('routes', __name__)

@routes.route('/data/speak/<text>', methods=['GET'])
def call_speak(text):
    try:
        print(f"Received Speak Request {text}")
        speak(f"{text}")
        return jsonify({"success": "completed"})
    except Exception as e:
        print(f"Error in Speak Request, {str(e)}")
        return jsonify({"error": "False"}), 500
    

if __name__ == "__main__":
    app = Flask(__name__)
    app.register_blueprint(routes)
    
    print("Starting audio server on port 5001...")
    app.run(host='0.0.0.0', port=5001, debug=True)