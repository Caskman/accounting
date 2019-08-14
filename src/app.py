from flask import Flask, jsonify, send_file, render_template, request
import account
import os

app = Flask(__name__)

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify(True)

@app.route('/compile', methods=["GET"])
def compile():
    print("Compiling document")
    path = account.compile_statements()
    return send_file(os.path.abspath(path), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@app.route('/', methods=["GET"])
def index():
    return render_template("index.html")

@app.route('/upload', methods=["POST"])
def upload():
    success = account.verify_and_upload(request.get_json())
    return jsonify({ success: success })
    # print(request.get_json()["year"])
    # print(type(request.data))
    # print(request.data)
    # return "hello"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
