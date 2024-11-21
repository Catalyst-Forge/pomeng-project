import json
import random
import nltk
import string
import numpy as np
import pickle
import tensorflow as tf
from nltk.stem import WordNetLemmatizer
from tensorflow import keras
from tensorflow.keras.preprocessing.sequence import pad_sequences

global responses, lemmatizer, tokenizer, le, model, input_shape
input_shape = 15

# import dataset answer
def load_response():
    global responses
    responses = {}
    with open('dataset/arun.json') as content:
        data = json.load(content)
    for intent in data['lstm_data']:
        responses[intent['tag']]=intent['responses']

# import model dan download nltk file
def preparation():
    try:
        global lemmatizer, tokenizer, le, model
        load_response()
        with open('asset_preprocessing/tokenizer.pkl', 'rb') as file:
            tokenizer = pickle.load(file)
        with open('asset_preprocessing/le.pkl', 'rb') as file:
            le = pickle.load(file)
        model = keras.models.load_model('asset_preprocessing/arunv_latest.keras')
        lemmatizer = WordNetLemmatizer()
        nltk.download('punkt', quiet=True)
        nltk.download('wordnet', quiet=True)
        nltk.download('omw-1.4', quiet=True)
    except Exception as e:
        print(f"ada error: {e}")

# hapus tanda baca
def remove_punctuation(text):
    texts_p = []
    text = [letters.lower() for letters in text if letters not in string.punctuation]
    text = ''.join(text)
    texts_p.append(text)
    return texts_p

# mengubah text menjadi vector
def vectorization(texts_p):
    vector = tokenizer.texts_to_sequences(texts_p)
    vector = np.array(vector).reshape(-1)
    vector = pad_sequences([vector], input_shape)
    return vector

# klasifikasi pertanyaan user
def predict(vector):
    output = model.predict(vector)
    output = output.argmax()
    response_tag = le.inverse_transform([output])[0]
    return response_tag

# menghasilkan jawaban berdasarkan pertanyaan user
def botResponse(text):
    texts_p = remove_punctuation(text)
    vector = vectorization(texts_p)
    response_tag = predict(vector)
    answer = random.choice(responses[response_tag])
    return answer
    