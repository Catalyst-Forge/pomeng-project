# migrate_function.py

import json
from models.lstm_model import Intent  # pastikan path ini sesuai dengan letak file models Anda
from extensions import db

def migrate_json_to_db(json_file_path):
    # Membaca data dari file JSON
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    # Iterasi pada setiap intent dalam data JSON
    for intent_data in data['intents']:
        # Gabungkan patterns dan responses menjadi string untuk disimpan di database
        patterns_str = ",".join(intent_data['patterns'])
        responses_str = ",".join(intent_data['responses'])
        
        # Membuat instance baru dari Intent
        intent = Intent(
            tag=intent_data['tag'],
            patterns=patterns_str,
            responses=responses_str
        )
        
        # Menambahkan ke sesi database
        db.session.add(intent)
    
    # Menyimpan semua perubahan ke database
    db.session.commit()
    print("Migrasi data berhasil!")
