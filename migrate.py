# migrate_combined.py

import sys
import json
from extensions import db
from models.fine_tuning import Conversation  # pastikan path ini sesuai dengan struktur folder Anda
from app import create_app  # Pastikan ini sesuai dengan aplikasi utama Anda


def migrate_to_db(file_path, file_type="json"):
    if file_type == "json":
        with open(file_path, 'r') as file:
            data = json.load(file)
        
        # Iterasi pada setiap intent dalam data JSON
        for intent_data in data['intents']:
            # Ambil messages dari JSON
            messages = [
                {"role": "system", "content": intent_data.get("tag")},
                {"role": "user", "content": ", ".join(intent_data.get("patterns", []))},
                {"role": "assistant", "content": ", ".join(intent_data.get("responses", []))}
            ]
            
            # Membuat instance baru dari Conversation
            conversation = Conversation(messages=messages)
            db.session.add(conversation)

    elif file_type == "jsonl":
        with open(file_path, 'r') as jsonl_file:
            for line in jsonl_file:
                data = json.loads(line)
                messages = data.get("messages", [])
                conversation = Conversation(messages=messages)
                db.session.add(conversation)

    # Simpan semua perubahan ke database
    db.session.commit()
    print(f"Migrasi data dari {file_type.upper()} berhasil!")


def main(file_path, file_type):
    app = create_app()  # Buat instance aplikasi Flask
    with app.app_context():  # Buat konteks aplikasi
        db.create_all()  # Membuat tabel jika belum ada
        migrate_to_db(file_path, file_type)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python migrate_combined.py <path_to_file> <file_type>")
        print("file_type can be 'json' or 'jsonl'")
    else:
        file_path = sys.argv[1]
        file_type = sys.argv[2].lower()
        if file_type not in ["json", "jsonl"]:
            print("file_type must be 'json' or 'jsonl'")
        else:
            main(file_path, file_type)
