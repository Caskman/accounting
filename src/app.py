from flask import Flask, jsonify
import account

app = Flask(__name__)

@app.route("/ping", methods=["POST"])
def ping():
    return jsonify(True)

@app.route('/compile', methods=["POST"])
def index():
    account.compile_statements()
    return jsonify(True)

if __name__ == '__main__':
    app.run()
