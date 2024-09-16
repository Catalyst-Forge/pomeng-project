import json
import os

# Path ke file JSON
JSON_FILE = os.path.join(os.getcwd(), 'dataset', 'arun.json')

# Fungsi untuk membaca semua intents dari file JSON
def get_all_intents():
    with open(JSON_FILE, 'r') as f:
        data = json.load(f)
    return data['intents']

# Fungsi untuk menambahkan intent baru
def add_intent(tag, patterns, responses):
    with open(JSON_FILE, 'r+') as f:
        data = json.load(f)
        new_intent = {
            "tag": tag,
            "patterns": patterns,
            "responses": responses
        }
        data['intents'].append(new_intent)
        f.seek(0)
        json.dump(data, f, indent=4)
    return new_intent

# Fungsi untuk memperbarui intent berdasarkan tag
def update_intent(tag, new_patterns, new_responses):
    with open(JSON_FILE, 'r+') as f:
        data = json.load(f)
        for intent in data['intents']:
            if intent['tag'] == tag:
                intent['patterns'] = new_patterns
                intent['responses'] = new_responses
                f.seek(0)
                json.dump(data, f, indent=4)
                return intent
        return None  # Jika intent dengan tag tidak ditemukan

# Fungsi untuk menghapus intent berdasarkan tag
def delete_intent(tag):
    with open(JSON_FILE, 'r+') as f:
        # Membaca data dari file JSON
        data = json.load(f)
        intents = data.get('intents', [])
        
        # Menyaring intent yang akan dihapus
        updated_intents = [intent for intent in intents if intent['tag'] != tag]
        
        # Mengecek apakah ada perubahan
        if len(updated_intents) < len(intents):
            # Mengatur posisi file pointer ke awal file
            f.seek(0)
            # Menghapus isi file yang lama
            f.truncate()
            # Menulis data yang telah diperbarui ke file
            json.dump({'intents': updated_intents}, f, indent=4)
            return {'tag': tag, 'status': 'deleted'}
        else:
            return {'status': 'not found'}
