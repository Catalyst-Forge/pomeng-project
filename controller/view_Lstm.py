from flask import Blueprint, request, jsonify, redirect, url_for, render_template, flash
from models.lstm_model import db, Lstm, save_to_json
from flask_login import login_required

lstm = Blueprint("lstm", __name__)


# Read all dataset
@lstm.route("/dashboard/dataset")
@login_required
def read_lstm():
    lstm = Lstm.query.all()
    return render_template("pages/dataset.html", lstm=lstm)


# Create an dataset
@lstm.route("/dashboard/dataset/create", methods=["POST"])
@login_required
def create_lstm():
    tag = request.form["tag"]
    patterns = request.form.getlist("patterns[]")  # Ambil semua pola sebagai list
    responses = request.form["responses"]  # Input sebagai string
    patterns_str = ",".join(patterns)  # Gabungkan pola menjadi string

    new_lstm = Lstm(tag=tag, patterns=patterns_str, responses=responses)
    db.session.add(new_lstm)
    db.session.commit()
    save_to_json()
    return redirect(url_for("lstm.read_lstm"))


# Update an dataset
@lstm.route("/dashboard/dataset/<int:id>/update", methods=["POST"])
@login_required
def update_lstm(id):
    lstm = Lstm.query.get(id)
    if lstm:
        # Log untuk melihat apakah data dari form sudah diterima dengan benar
        print(f"Updating lstm Data with ID: {id}")
        print(f"Tag: {request.form['tag']}")
        print(f"Patterns: {request.form['patterns']}")
        print(f"Responses: {request.form['responses']}")

        lstm.tag = request.form["tag"]
        lstm.patterns = request.form["patterns"]  # Input sebagai string
        lstm.responses = request.form["responses"]  # Input sebagai string
        db.session.commit()
        save_to_json()  # Simpan perubahan ke JSON
        flash("Data berhasil diubah!", "success")
    return redirect(url_for("lstm.read_lstm"))


# Delete an dataset
@lstm.route("/dashboard/dataset/<int:id>/delete", methods=["POST"])
@login_required
def delete_lstm(id):
    lstm = Lstm.query.get(id)
    if lstm:
        db.session.delete(lstm)
        db.session.commit()
        save_to_json()
        flash("Data berhasil dihapus!", "success")
    return redirect(url_for("lstm.read_lstm"))
