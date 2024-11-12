import json
from extensions import db


class Lstm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(80), nullable=False)
    patterns = db.Column(db.Text, nullable=False)
    responses = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<Lstm {self.tag}>"


def save_to_json():
    lstm_data = Lstm.query.all()
    data = {"lstm_data": []}
    for lstm in lstm_data:
        data["lstm_data"].append(
            {
                "tag": lstm.tag,
                "patterns": lstm.patterns.split(","),
                "responses": lstm.responses.split(","),
            }
        )

    with open("dataset/arun.json", "w") as json_file:
        json.dump(data, json_file, indent=4)
