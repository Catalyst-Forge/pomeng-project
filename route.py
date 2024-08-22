from flask import Flask, render_template, request, jsonify, Blueprint
from process import preparation, botResponse
preparation()

route_bp = Blueprint('routes', __name__)

@route_bp.route('/')
def index():
  return render_template('index.html')


@route_bp.route("/predict", methods=["GET", "POST"])
def predict():
	text = request.get_json().get("message")
	response = botResponse(text)
	message = {"answer": response}
	return jsonify(message)