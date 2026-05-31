from flask import Flask, request, jsonify, Response
import logging
import json

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Store received callbacks
callbacks_received = []

def log_callback(endpoint, data):
    print(f"📥 {endpoint} RECEIVED: {data}")
    callbacks_received.append({"endpoint": endpoint, "data": data})

@app.route('/callback', methods=['GET', 'POST', 'OPTIONS'])
def callback():
    # Handle GET (browser testing)
    if request.method == 'GET':
        # Check query params first
        if request.args:
            data = dict(request.args)
            log_callback("CALLBACK", data)
            return Response(
                json.dumps({"status": "ok", "message": "GET callback received", "data": data}),
                mimetype='application/json'
            )
        # Plain GET - just return healthy
        return Response(
            json.dumps({"status": "ok", "message": "callback endpoint ready"}),
            mimetype='application/json'
        )
    
    # Handle POST (broker calls)
    try:
        data = request.json or {}
    except:
        data = {}
    log_callback("CALLBACK", data)
    return jsonify({"status": "ok", "message": "callback received"})

@app.route('/postback', methods=['GET', 'POST', 'OPTIONS'])
def postback():
    if request.method == 'GET':
        if request.args:
            data = dict(request.args)
            log_callback("POSTBACK", data)
            return Response(
                json.dumps({"status": "ok", "message": "GET postback received", "data": data}),
                mimetype='application/json'
            )
        return Response(
            json.dumps({"status": "ok", "message": "postback endpoint ready"}),
            mimetype='application/json'
        )
    
    try:
        data = request.json or {}
    except:
        data = {}
    log_callback("POSTBACK", data)
    return jsonify({"status": "ok", "message": "postback received"})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "callbacks_received": len(callbacks_received)
    })

@app.route('/callbacks', methods=['GET'])
def list_callbacks():
    return jsonify({"callbacks": callbacks_received})

if __name__ == '__main__':
    print("🚀 Starting callback server on port 8000")
    app.run(host='0.0.0.0', port=8000)