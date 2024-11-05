import json
from extensions import db

class Lstm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(80), nullable=False)
    patterns = db.Column(db.Text, nullable=False)  
    responses = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Intent {self.tag}>'

def save_to_json():
    intents = Intent.query.all()
    data = {"intents": []}
    for intent in intents:
        data["intents"].append({
            "tag": intent.tag,
            "patterns": intent.patterns.split(","),
            "responses": intent.responses.split(",")
        })

    with open("dataset/intents.json", "w") as json_file:
        json.dump(data, json_file, indent=4)
