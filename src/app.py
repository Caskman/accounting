from flask import Flask, jsonify, send_file
import account
import os

app = Flask(__name__)

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify(True)

@app.route('/compile', methods=["GET"])
def index():
    path = account.compile_statements()
    # return send_file(os.path.abspath(path), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    return path

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
