from flask import Blueprint, request, jsonify, redirect, url_for, render_template, flash
from models.lstm_model import db, Lstm, save_to_json
from flask_login import login_required

lstm = Blueprint("lstm", __name__, url_prefix="/dashboard/dataset/lstm")


# Read all dataset
@lstm.route("/list", methods=["GET"])
@login_required
def read_lstm():
    page = request.args.get("page", 1, type=int)
    per_page = 10
    lstm_query = Lstm.query.paginate(page=page, per_page=per_page, error_out=False)
    start_number = (page - 1) * per_page + 1

    return render_template(
        "pages/dataset-lstm.html",
        lstm=lstm_query.items,
        pagination=lstm_query,
        start_number=start_number,
    )


# Create an dataset
@lstm.route("/create", methods=["POST"])
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
    flash("Data berhasil ditambahkan!", "success")
    return redirect(url_for("lstm.read_lstm"))


# Update an dataset
@lstm.route("/<int:id>/update", methods=["POST"])
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
@lstm.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete_lstm(id):
    lstm = Lstm.query.get(id)
    if lstm:
        db.session.delete(lstm)
        db.session.commit()
        save_to_json()
        flash("Data berhasil dihapus!", "success")
    return redirect(url_for("lstm.read_lstm"))
