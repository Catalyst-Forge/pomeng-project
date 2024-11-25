import json
import random
import nltk
import string
import numpy as np
import pickle
import os
import jsonlines
from typing import Tuple, List, Dict, Optional
from dotenv import load_dotenv
from openai import OpenAI
# Import PySastrawi components
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from nltk.tokenize import word_tokenize
from tensorflow import keras
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ResponseGenerator:
    def __init__(self):
        self.load_dotenv()
        self.client = OpenAI(api_key=self.OPENAI_API_KEY)
        self.preparation()
    
    def load_dotenv(self):
        """Load environment variables"""
        load_dotenv()
        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        self.OPENAI_MODEL_SELECTED = os.getenv('OPENAI_MODEL_SELECTED')
        self.LSTM_MODEL_SELECTED = os.getenv('LSTM_MODEL_SELECTED')
        self.CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', '0.5'))
        
    def preparation(self):
        """Initialize all required components"""
        try:
            # Initialize Sastrawi components
            stemmer_factory = StemmerFactory()
            self.stemmer = stemmer_factory.create_stemmer()
            
            stopword_factory = StopWordRemoverFactory()
            self.stopword_remover = stopword_factory.create_stop_word_remover()
            self.stop_words = stopword_factory.get_stop_words()
            
            self.load_response()
            self.load_training_examples()
            self.load_models()
            self.initialize_nltk()
            print("Preparation completed successfully!")
        except Exception as e:
            print(f"Error during preparation: {e}")
            raise
    
    def initialize_nltk(self):
        """Initialize NLTK components"""
        nltk.download('punkt', quiet=True)
    
    def load_training_examples(self):
        """Load and prepare training examples"""
        try:
            self.training_examples = []
            user_queries = []
            
            with jsonlines.open('dataset/finetuning.jsonl') as reader:
                for item in reader:
                    if 'messages' in item:
                        self.training_examples.append(item['messages'])
                        for message in item['messages']:
                            if message['role'] == 'user':
                                user_queries.append(message['content'])
                                break
            
            # Using TfidfVectorizer with PySastrawi stop words
            self.vectorizer = TfidfVectorizer(
                ngram_range=(1, 2), 
                stop_words=self.stop_words
            )
            self.vectorizer.fit(user_queries)
            print(f"Loaded {len(self.training_examples)} training examples")
        except Exception as e:
            print(f"Error loading training examples: {e}")
            self.training_examples = []
    
    def preprocess_text(self, text: str) -> List[str]:
        """Preprocess input text using PySastrawi"""
        try:
            # Convert to lowercase
            text = text.lower()
            
            # Remove punctuation
            text = ''.join([char for char in text if char not in string.punctuation])
            
            # Remove stop words
            text = self.stopword_remover.remove(text)
            
            # Stem the text
            text = self.stemmer.stem(text)
            
            # Tokenize
            tokens = word_tokenize(text)
            
            return [' '.join(tokens)]
        except Exception as e:
            print(f"Error in text preprocessing: {e}")
            return [text]
    
    def load_response(self):
        """Load response dataset"""
        try:
            with open('dataset/arun.json') as content:
                data = json.load(content)
            self.responses = {intent['tag']: intent['responses'] for intent in data['lstm_data']}
        except Exception as e:
            print(f"Error loading responses: {e}")
            self.responses = {}
    
    def load_models(self):
        """Load all necessary models and preprocessing objects"""
        try:
            with open(f'logs/{self.LSTM_MODEL_SELECTED}/preprocessing/tokenizer.pkl', 'rb') as file:
                self.tokenizer = pickle.load(file)
            with open(f'logs/{self.LSTM_MODEL_SELECTED}/preprocessing/le.pkl', 'rb') as file:
                self.le = pickle.load(file)
            with open(f'logs/{self.LSTM_MODEL_SELECTED}/preprocessing/max_sequence_length.pkl', 'rb') as file:
                self.max_sequence_length = pickle.load(file)
            self.model = keras.models.load_model(f'logs/{self.LSTM_MODEL_SELECTED}/model.keras')
        except Exception as e:
            print(f"Error loading models: {e}")
            raise
    
    def vectorize_text(self, texts_p: List[str]) -> Optional[np.ndarray]:
        """Convert text to vector for prediction"""
        try:
            vector = self.tokenizer.texts_to_sequences(texts_p)
            return pad_sequences(vector, maxlen=self.max_sequence_length, padding='post', truncating='post')
        except Exception as e:
            print(f"Error during vectorization: {e}")
            return None
    
    def get_predictions(self, vector: np.ndarray) -> Tuple[str, float, List[Tuple[str, float]]]:
        """Get model predictions with probabilities"""
        try:
            probabilities = self.model.predict(vector)[0]
            sorted_indices = np.argsort(probabilities)[::-1]
            
            predictions = [(self.le.inverse_transform([idx])[0], probabilities[idx])
                         for idx in sorted_indices]
            
            return predictions[0][0], predictions[0][1], predictions
        except Exception as e:
            print(f"Error during prediction: {e}")
            return None, 0.0, []
    
    def format_probabilities(self, predictions: List[Tuple[str, float]]) -> str:
        """Format probability results"""
        if not predictions:
            return "Tidak dapat menghitung probabilitas."
        
        result = "\nProbabilitas untuk setiap kelas:\n"
        for tag, prob in predictions:
            result += f"{tag}: {prob*100:.2f}%\n"
        return result
    
    def get_openai_response(self, text: str) -> str:
        """Get response from OpenAI with context"""
        try:
            messages = [
                {"role": "system", "content": "Anda adalah asisten AI yang membantu dalam bahasa Indonesia. Berikan respons yang sopan dan membantu."}
            ]
            
            # Add relevant context from training examples
            for example in self.training_examples[:5]:
                messages.extend(example)
            
            messages.append({"role": "user", "content": text})
            
            response = self.client.chat.completions.create(
                model=self.OPENAI_MODEL_SELECTED,
                messages=messages,
                temperature=0.7,
                max_tokens=150
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error getting OpenAI response: {e}")
            return "Maaf, terjadi kesalahan saat mencoba mendapatkan respons."
    
    def get_response(self, text: str) -> str:
        """Generate response based on user input"""
        try:
            # Preprocess input
            processed_text = self.preprocess_text(text)
            vector = self.vectorize_text(processed_text)
            
            if vector is None:
                return "Maaf, saya tidak bisa memproses permintaan Anda."
            
            # Get predictions
            tag, probability, predictions = self.get_predictions(vector)
            prob_info = self.format_probabilities(predictions)
            
            # Use OpenAI if confidence is low
            if probability < self.CONFIDENCE_THRESHOLD:
                openai_response = self.get_openai_response(text)
                print(f"[OpenAI Response karena kepercayaan rendah ({probability*100:.2f}%)]\n{openai_response}\n{prob_info}")
                return openai_response
            
            # Use local model response
            if tag not in self.responses:
                return "Maaf, saya tidak memiliki jawaban untuk pertanyaan Anda."
            
            response = random.choice(self.responses[tag])
            print(f"[Kepercayaan: {probability*100:.2f}%]{prob_info}")
            return response
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return "Terjadi kesalahan saat menghasilkan jawaban."