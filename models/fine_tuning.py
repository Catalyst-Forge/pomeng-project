from extensions import db

class Finetuning(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    messages = db.Column(db.JSON, nullable=False)  # Simpan pesan dalam format JSON

    def __repr__(self):
        return f'<Finetuning {self.id}>'
