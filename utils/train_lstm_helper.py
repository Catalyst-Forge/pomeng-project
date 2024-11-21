import nltk
import json
from nltk.stem import WordNetLemmatizer
from pathlib import Path
import logging
import datetime
import shutil


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize nltk resources
nltk.download("punkt")
nltk.download("wordnet")

# Load dataset and asset_preprocessing configurations
with open("dataset/arun.json") as f:
    chatbot_dataset = json.load(f)

lemmatizer = WordNetLemmatizer()


def create_version_folder():
    """Create a new version folder based on timestamp"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    version_path = Path(f"logs/version_{timestamp}")
    version_path.mkdir(parents=True, exist_ok=True)
    return version_path

def backup_current_asset_preprocessing():
    """Backup current asset_preprocessing folder if it exists"""
    current_asset_preprocessing = Path("asset_preprocessing")
    if current_asset_preprocessing.exists():
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)

        # Get the version folder path
        version_path = create_version_folder()

        # Copy all files from asset_preprocessing to the version folder
        try:
            shutil.copytree(
                current_asset_preprocessing, version_path, dirs_exist_ok=True
            )
            logger.info(f"Backed up asset_preprocessing to {version_path}")

            # Create metadata file with extended training history if available
            metadata = {
                "version_timestamp": version_path.name,
                "backup_date": datetime.datetime.now().isoformat(),
                "files_backed_up": [
                    f.name for f in current_asset_preprocessing.glob("*")
                ],
            }

            # Check if training history exists in current asset_preprocessing
            history_file = current_asset_preprocessing / "training_history.json"
            if history_file.exists():
                with open(history_file) as f:
                    training_history = json.load(f)
                metadata["training_history"] = training_history

            with open(version_path / "metadata.json", "w") as f:
                json.dump(metadata, f, indent=4)

            return str(version_path)
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            raise
    return None

def preprocess_data():
    """Preprocess data with versioning support"""
    words, classes, documents = [], [], []
    ignore_words = ["?", "!"]

    # Backup existing asset_preprocessing folder
    backup_current_asset_preprocessing()

    for intent in chatbot_dataset["lstm_data"]:
        for pattern in intent["patterns"]:
            word_list = nltk.word_tokenize(pattern)
            words.extend(word_list)
            documents.append((word_list, intent["tag"]))
            if intent["tag"] not in classes:
                classes.append(intent["tag"])

    words = sorted(
        set(lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_words)
    )
    classes = sorted(set(classes))

    # Tokenize and encode labels
    tokenizer = Tokenizer(num_words=2000)
    patterns = [" ".join(pattern).lower() for pattern, _ in documents]
    tokenizer.fit_on_texts(patterns)
    train_sequences = tokenizer.texts_to_sequences(patterns)
    X_train = pad_sequences(train_sequences)

    le = LabelEncoder()
    Y_train = le.fit_transform([label for _, label in documents])

    # Ensure asset_preprocessing directory exists
    Path("asset_preprocessing").mkdir(exist_ok=True)

    # Save asset_preprocessing objects
    asset_preprocessing_files = {
        "words.pkl": words,
        "classes.pkl": classes,
        "le.pkl": le,
        "tokenizer.pkl": tokenizer,
    }

    for filename, obj in asset_preprocessing_files.items():
        with open(f"asset_preprocessing/{filename}", "wb") as f:
            pickle.dump(obj, f)

    # Create metadata for current version
    metadata = {
        "asset_preprocessing_date": datetime.datetime.now().isoformat(),
        "vocab_size": len(words),
        "num_classes": len(classes),
        "num_patterns": len(patterns),
    }

    with open("asset_preprocessing/metadata.json", "w") as f:
        json.dump(metadata, f, indent=4)

    return X_train, Y_train, len(tokenizer.word_index) + 1, le.classes_.shape[0]
