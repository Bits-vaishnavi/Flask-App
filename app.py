from flask import Flask,jsonify
app = Flask(__name__)
@app.route("/")
def home():
    return jsonify({
        "message": "ACEest Fitness API is running"
    })
if __name__ == "__main__":    
    app.run(debug=True)
