from flask import Blueprint, request, jsonify, redirect, url_for, render_template
from models.lstm_model import db, Intent, save_to_json
from flask_login import login_required

crud_bp = Blueprint('crud_bp', __name__)

@crud_bp.route('/create', methods=['POST'])
@login_required
def create_intent():
    tag = request.form['tag']
    patterns = request.form.getlist('patterns[]')  # Ambil semua pola sebagai list
    responses = request.form['responses']  # Input sebagai string
    patterns_str = ','.join(patterns)  # Gabungkan pola menjadi string

    new_intent = Intent(tag=tag, patterns=patterns_str, responses=responses)
    db.session.add(new_intent)
    db.session.commit()
    save_to_json() 
    return redirect(url_for('crud_bp.read_intents'))


# Read all intents
@crud_bp.route('/crud')
@login_required
def read_intents():
    intents = Intent.query.all()
    return render_template('crud.html', intents=intents)

# Update an intent
@crud_bp.route('/update/<int:id>', methods=['POST'])
@login_required
def update_intent(id):
    intent = Intent.query.get(id)
    if intent:
        # Log untuk melihat apakah data dari form sudah diterima dengan benar
        print(f"Updating intent with ID: {id}")
        print(f"Tag: {request.form['tag']}")
        print(f"Patterns: {request.form['patterns']}")
        print(f"Responses: {request.form['responses']}")

        intent.tag = request.form['tag']
        intent.patterns = request.form['patterns']  # Input sebagai string
        intent.responses = request.form['responses']  # Input sebagai string
        db.session.commit()
        save_to_json()  # Simpan perubahan ke JSON
    return redirect(url_for('crud_bp.read_intents'))


# Delete an intent
@crud_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_intent(id):
    intent = Intent.query.get(id)
    if intent:
        db.session.delete(intent)
        db.session.commit()
        save_to_json()  # Simpan perubahan ke JSON
    return redirect(url_for('crud_bp.read_intents'))
