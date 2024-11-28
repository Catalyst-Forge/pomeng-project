import json
import pickle
import nltk
from nltk.stem import WordNetLemmatizer
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import to_categorical
from pathlib import Path
import datetime
from utils.lstm.config import Config, logger

# Initialize nltk resources
nltk.download('punkt')
nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()

def create_version_folder(model_name):
    """Create a version folder based on model name"""
    version_path = Path(f"{Config.LOGS_DIRECTORY}/{model_name}")
    version_path.mkdir(parents=True, exist_ok=True)
    return version_path

def preprocess_data(version_path, model_name, dataset_path=Config.DATASET_PATH):
    """Preprocess data with versioning support"""
    with open(dataset_path) as f:
        arun_dataset = json.load(f)

    words, classes, documents = [], [], []
    ignore_words = ['?', '!']

    for intent in arun_dataset['lstm_data']:
        for pattern in intent['patterns']:
            word_list = nltk.word_tokenize(pattern)
            words.extend(word_list)
            documents.append((word_list, intent['tag']))
            if intent['tag'] not in classes:
                classes.append(intent['tag'])

    words = sorted(set(lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_words))
    classes = sorted(set(classes))

    # Tokenize and encode labels
    tokenizer = Tokenizer(num_words=2000)
    patterns = [' '.join(pattern).lower() for pattern, _ in documents]
    tokenizer.fit_on_texts(patterns)
    train_sequences = tokenizer.texts_to_sequences(patterns)
    
    # Get maximum sequence length
    max_sequence_length = max(len(seq) for seq in train_sequences)
    X_train = pad_sequences(train_sequences, maxlen=max_sequence_length)

    le = LabelEncoder()
    Y_train_encoded = le.fit_transform([label for _, label in documents])
    # Convert to one-hot encoded format
    Y_train = to_categorical(Y_train_encoded)

    # Save preprocessing objects in the version folder
    preprocessing_path = version_path / "preprocessing"
    preprocessing_path.mkdir(parents=True, exist_ok=True)

    preprocessing_files = {
        'words.pkl': words,
        'classes.pkl': classes,
        'le.pkl': le,
        'tokenizer.pkl': tokenizer,
        'max_sequence_length.pkl': max_sequence_length
    }

    for filename, obj in preprocessing_files.items():
        with open(preprocessing_path / filename, 'wb') as f:
            pickle.dump(obj, f)

    # Create metadata for current version
    metadata = {
        "preprocessing_date": datetime.datetime.now().isoformat(),
        "vocab_size": len(words),
        "num_classes": len(classes),
        "num_patterns": len(patterns),
        "max_sequence_length": max_sequence_length,
        "model_name": model_name
    }

    with open(preprocessing_path / 'metadata.json', 'w') as f:
        json.dump(metadata, f, indent=4)

    logger.info(f"Data preprocessing completed. Shape of X_train: {X_train.shape}, Y_train: {Y_train.shape}")
    
    return (X_train, Y_train, 
            len(tokenizer.word_index) + 1,  # vocab_size 
            len(classes),                    # num_classes
            max_sequence_length)             # sequence_length