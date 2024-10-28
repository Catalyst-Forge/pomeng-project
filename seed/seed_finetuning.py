# import_jsonl_to_db.py

import json
from models.fine_tuning import Conversation  # pastikan path ini sesuai dengan struktur folder Anda
from extensions import db

def import_jsonl_to_db(jsonl_file_path):
    # Baca file JSONL
    with open(jsonl_file_path, 'r') as jsonl_file:
        for line in jsonl_file:
            # Parse setiap baris JSONL ke dalam dictionary
            data = json.loads(line)
            messages = data.get("messages", [])

            # Buat instance Conversation baru
            conversation = Conversation(messages=messages)
            
            # Tambahkan ke sesi database
            db.session.add(conversation)
    
    # Simpan semua perubahan ke database
    db.session.commit()
    print("Import data dari JSONL berhasil!")
