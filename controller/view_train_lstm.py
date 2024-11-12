from flask import Flask, render_template, request, jsonify, Response, stream_with_context, Blueprint
import json
import pickle
import numpy as np
from queue import Queue, Empty
from threading import Thread
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from nltk.stem import WordNetLemmatizer
import os
import nltk
import shutil
from pathlib import Path
import datetime
import logging
from tensorflow.python.client import device_lib

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
lstm_train = Blueprint('lstm_train', __name__)

# Initialize nltk resources
nltk.download('punkt')
nltk.download('wordnet')

# Load dataset and asset_preprocessing configurations
with open('dataset/arun.json') as f:
    msbot_dataset = json.load(f)

lemmatizer = WordNetLemmatizer()

print(device_lib.list_local_devices())

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
            shutil.copytree(current_asset_preprocessing, version_path, dirs_exist_ok=True)
            logger.info(f"Backed up asset_preprocessing to {version_path}")
            
            # Create metadata file with extended training history if available
            metadata = {
                "version_timestamp": version_path.name,
                "backup_date": datetime.datetime.now().isoformat(),
                "files_backed_up": [f.name for f in current_asset_preprocessing.glob("*")]
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
    ignore_words = ['?', '!']

    # Backup existing asset_preprocessing folder
    backup_current_asset_preprocessing()

    for intent in msbot_dataset['intents']:
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
    X_train = pad_sequences(train_sequences)

    le = LabelEncoder()
    Y_train = le.fit_transform([label for _, label in documents])

    # Ensure asset_preprocessing directory exists
    Path("asset_preprocessing").mkdir(exist_ok=True)

    # Save asset_preprocessing objects
    asset_preprocessing_files = {
        'words.pkl': words,
        'classes.pkl': classes,
        'le.pkl': le,
        'tokenizer.pkl': tokenizer
    }

    for filename, obj in asset_preprocessing_files.items():
        with open(f'asset_preprocessing/{filename}', 'wb') as f:
            pickle.dump(obj, f)

    # Create metadata for current version
    metadata = {
        "asset_preprocessing_date": datetime.datetime.now().isoformat(),
        "vocab_size": len(words),
        "num_classes": len(classes),
        "num_patterns": len(patterns)
    }

    with open('asset_preprocessing/metadata.json', 'w') as f:
        json.dump(metadata, f, indent=4)

    return X_train, Y_train, len(tokenizer.word_index) + 1, le.classes_.shape[0]

# Route for the main page with form inputs
@lstm_train.route('/training-lstm')
def home():
    return render_template('pages/training-lstm.html')

@lstm_train.route('/versions', methods=['GET'])
def get_versions():
    """Endpoint to retrieve all available versions"""
    versions_path = Path("logs")
    if not versions_path.exists():
        return jsonify({"versions": []})
    
    versions = []
    for version_dir in versions_path.glob("version_*"):
        metadata_file = version_dir / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file) as f:
                metadata = json.load(f)
                versions.append(metadata)
    
    return jsonify({"versions": sorted(versions, key=lambda x: x['backup_date'], reverse=True)})
# Add new endpoint to get training history for specific version

@lstm_train.route('/version-history/<version>', methods=['GET'])
def get_version_history(version):
    """Get detailed training history for a specific version including per-epoch metrics"""
    try:
        version_path = Path(f"logs/{version}")
        if not version_path.exists():
            return jsonify({"error": "Version not found"}), 404

        metadata_file = version_path / "training_metadata.json"
        if not metadata_file.exists():
            return jsonify({"error": "Version metadata not found"}), 404
        
        with open(metadata_file) as f:
            metadata = json.load(f)
        
        return jsonify(metadata)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@lstm_train.route('/restore/<version>', methods=['POST'])
def restore_version(version):
    """Endpoint to restore a specific version"""
    try:
        version_path = Path(f"logs/{version}")
        if not version_path.exists():
            return jsonify({"error": "Version not found"}), 404

        # Backup current before restore
        backup_current_asset_preprocessing()

        # Clear current asset_preprocessing folder
        shutil.rmtree("asset_preprocessing", ignore_errors=True)
        
        # Restore the selected version
        shutil.copytree(version_path, "asset_preprocessing", dirs_exist_ok=True)
        
        return jsonify({"message": f"Successfully restored version {version}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@lstm_train.route('/train', methods=['POST'])
def train_model():
    try:
        # Preprocess data for training with versioning
        X_train, Y_train, vocab_size, output_length = preprocess_data()

        # Get configuration data from the request
        data = request.get_json()
        embedding_dim = data.get("embedding_dim", 16)
        learning_rate = data.get("learning_rate", 0.001)
        batch_size = data.get("batch_size", 64)
        epochs = data.get("epochs", 10)
        layers = data.get("layers", [])

        def generate_training_progress():
            model = Sequential()
            model.add(Embedding(input_dim=vocab_size, output_dim=embedding_dim, input_length=X_train.shape[1]))

            for layer in layers:
                if layer['type'] == 'LSTM':
                    model.add(LSTM(units=layer['neurons'], return_sequences=False))
                elif layer['type'] == 'Dense':
                    model.add(Dense(units=layer['neurons'], activation='relu'))
                elif layer['type'] == 'Dropout':
                    model.add(Dropout(rate=layer.get("rate", 0.5)))

            model.add(Dense(output_length, activation='softmax'))
            model.compile(loss='sparse_categorical_crossentropy', 
                        optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate), 
                        metrics=['accuracy'])

            # Calculate total steps
            steps_per_epoch = len(X_train) // batch_size
            total_steps = steps_per_epoch * epochs

            # Initialize training history
            training_history = {
                "epochs": [],
                "start_time": datetime.datetime.now().isoformat(),
                "total_steps": total_steps,
                "steps_per_epoch": steps_per_epoch
            }

            class DetailedTrainingCallback(tf.keras.callbacks.Callback):
                def __init__(self):
                    super(DetailedTrainingCallback, self).__init__()
                    self.current_epoch_data = None
                    self.current_epoch_steps = []
                    self.sse_queue = Queue()
                
                def on_epoch_begin(self, epoch, logs=None):
                    self.current_epoch_data = {
                        "epoch_number": epoch + 1,
                        "start_time": datetime.datetime.now().isoformat(),
                        "steps": [],
                        "metrics": {}
                    }
                    self.current_epoch_steps = []

                def on_batch_end(self, batch, logs=None):
                    if logs:
                        step_data = {
                            "step": batch + 1,
                            "time": datetime.datetime.now().isoformat(),
                            "accuracy": float(logs.get('accuracy', 0)),
                            "loss": float(logs.get('loss', 0))
                        }
                        self.current_epoch_steps.append(step_data)
                        
                        # Put SSE data in queue
                        current_step = (self.current_epoch_data["epoch_number"] - 1) * steps_per_epoch + batch + 1
                        progress = int((current_step / total_steps) * 100)
                        self.sse_queue.put({
                            'progress': progress,
                            'step_data': step_data
                        })

                def on_epoch_end(self, epoch, logs=None):
                    end_time = datetime.datetime.now()
                    start_time = datetime.datetime.fromisoformat(self.current_epoch_data["start_time"])
                    
                    # Update epoch data
                    self.current_epoch_data.update({
                        "end_time": end_time.isoformat(),
                        "duration": str(end_time - start_time),
                        "steps": self.current_epoch_steps.copy(),  # Store all steps for this epoch
                        "metrics": {
                            "accuracy": float(logs.get('accuracy', 0)),
                            "loss": float(logs.get('loss', 0)),
                            "val_accuracy": float(logs.get('val_accuracy', 0)) if 'val_accuracy' in logs else None,
                            "val_loss": float(logs.get('val_loss', 0)) if 'val_loss' in logs else None
                        }
                    })
                    
                    # Add completed epoch to training history
                    training_history["epochs"].append(self.current_epoch_data)
                    
                    # Calculate time elapsed since training started
                    training_start = datetime.datetime.fromisoformat(training_history["start_time"])
                    total_time_elapsed = str(end_time - training_start)
                    
                    # Put epoch completion data in queue
                    self.sse_queue.put({
                        'progress': int(((epoch + 1) / epochs) * 100),
                        'epoch_data': {
                            "epoch": epoch + 1,
                            "accuracy": float(logs.get('accuracy', 0)),
                            "loss": float(logs.get('loss', 0)),
                            "time_elapsed": total_time_elapsed,
                            "step_count": len(self.current_epoch_steps)
                        }
                    })

            callback = DetailedTrainingCallback()
            
            @stream_with_context
            def stream_response():
                # Start training in a separate thread
                def train_model_thread():
                    try:
                        return model.fit(
                            X_train, Y_train,
                            batch_size=batch_size,
                            epochs=epochs,
                            verbose=1,
                            callbacks=[callback]
                        )
                    except Exception as e:
                        callback.sse_queue.put({'error': str(e)})
                        return None

                training_thread = Thread(target=train_model_thread)
                training_thread.start()

                # Stream SSE messages from queue
                while training_thread.is_alive() or not callback.sse_queue.empty():
                    try:
                        data = callback.sse_queue.get(timeout=1.0)
                        if 'error' in data:
                            yield f"data:{json.dumps({'error': data['error']})}\n\n"
                            break
                        yield f"data:{json.dumps(data)}\n\n"
                    except Empty:
                        continue

                training_thread.join()

                # Save the model
                model_path = "asset_preprocessing/arunv_latest.keras"
                model.save(model_path)

                # Calculate final metrics
                training_end_time = datetime.datetime.now()
                training_start_time = datetime.datetime.fromisoformat(training_history["start_time"])
                training_duration = str(training_end_time - training_start_time)

                # Get accuracy and loss from the last epoch
                last_epoch = training_history["epochs"][-1]
                final_accuracy = last_epoch["metrics"]["accuracy"]
                final_loss = last_epoch["metrics"]["loss"]

                # Find best accuracy
                best_accuracy = max(epoch["metrics"]["accuracy"] for epoch in training_history["epochs"])
                best_epoch = next(i + 1 for i, epoch in enumerate(training_history["epochs"]) 
                                if epoch["metrics"]["accuracy"] == best_accuracy)

                # Update final training history
                training_history.update({
                    "end_time": training_end_time.isoformat(),
                    "total_duration": training_duration,
                    "final_accuracy": final_accuracy,
                    "final_loss": final_loss,
                    "best_accuracy": best_accuracy,
                    "best_epoch": best_epoch
                })

                # Save detailed training history
                with open('asset_preprocessing/training_history.json', 'w') as f:
                    json.dump(training_history, f, indent=4)

                # Save complete metadata
                training_metadata = {
                    "training_date": datetime.datetime.now().isoformat(),
                    "model_config": {
                        "embedding_dim": embedding_dim,
                        "learning_rate": learning_rate,
                        "batch_size": batch_size,
                        "epochs": epochs,
                        "layers": layers,
                        "vocab_size": vocab_size,
                        "output_length": output_length
                    },
                    "training_history": training_history
                }

                with open('asset_preprocessing/training_metadata.json', 'w') as f:
                    json.dump(training_metadata, f, indent=4)

                yield f"data:{json.dumps({'progress': 100, 'training_complete': True})}\n\n"

            return Response(stream_response(), mimetype='text/event-stream')

        return generate_training_progress()

    except Exception as e:
        logger.error(f"Training error: {str(e)}")
        return jsonify({"error": str(e)}), 500

from flask import Flask, jsonify
import shutil
import json
from pathlib import Path
import datetime
import logging

# Add these new endpoints and functions to the existing Flask app

@lstm_train.route('/models', methods=['GET'])
def get_models():
    """Get models from logs directory and check active model in asset_preprocessing"""
    try:
        response = {
            "models": [],
            "active_model": None
        }

        # Check for active model in asset_preprocessing
        asset_path = Path("asset_preprocessing")
        if asset_path.exists():
            model_file = asset_path / "arunv_latest.keras"
            metadata_file = asset_path / "training_metadata.json"
            
            if model_file.exists() and metadata_file.exists():
                with open(metadata_file) as f:
                    metadata = json.load(f)
                
                # Extract relevant metrics for active model
                training_history = metadata.get("training_history", {})
                response["active_model"] = {
                    "training_date": metadata.get("training_date"),
                    "configuration": {
                        "embedding_dim": metadata.get("embedding_dim"),
                        "learning_rate": metadata.get("learning_rate"),
                        "batch_size": metadata.get("batch_size"),
                        "epochs": metadata.get("epochs"),
                        "layers": metadata.get("layers")
                    },
                    "metrics": {
                        "final_accuracy": training_history.get("final_accuracy"),
                        "final_loss": training_history.get("final_loss"),
                        "training_duration": training_history.get("training_duration"),
                        "best_accuracy": training_history.get("best_accuracy"),
                        "best_epoch": training_history.get("best_epoch")
                    }
                }

        # Get models from logs directory
        logs_path = Path("logs")
        if logs_path.exists():
            versions = []
            for version_dir in sorted(logs_path.glob("version_*"), 
                                    key=lambda x: x.stat().st_mtime, reverse=True):
                metadata_file = version_dir / "metadata.json"
                model_file = version_dir / "arunv_latest.keras"
                training_metadata = version_dir / "training_metadata.json"
                
                if metadata_file.exists() and model_file.exists():
                    with open(metadata_file) as f:
                        metadata = json.load(f)
                    
                    # Get training metrics if available
                    training_metrics = {}
                    if training_metadata.exists():
                        with open(training_metadata) as f:
                            training_data = json.load(f)
                            training_history = training_data.get("training_history", {})
                            training_metrics = {
                                "final_accuracy": training_history.get("final_accuracy"),
                                "final_loss": training_history.get("final_loss"),
                                "training_duration": training_history.get("training_duration"),
                                "best_accuracy": training_history.get("best_accuracy"),
                                "best_epoch": training_history.get("best_epoch")
                            }
                    
                    model_info = {
                        "version": version_dir.name,
                        "backup_date": metadata.get("backup_date"),
                        "training_metrics": training_metrics
                    }
                    versions.append(model_info)
            
            response["models"] = versions

        return jsonify(response)

    except Exception as e:
        logger.error(f"Error getting models: {str(e)}")
        return jsonify({"error": str(e)}), 500
@lstm_train.route('/models/<version>', methods=['DELETE'])
def delete_model(version):
    """Delete a specific model version from logs"""
    try:
        version_path = Path(f"logs/{version}")
        if not version_path.exists():
            return jsonify({"error": "Model version not found"}), 404

        # Delete the version folder
        shutil.rmtree(version_path)
        
        return jsonify({
            "message": f"Successfully deleted model version {version}",
            "deleted_version": version
        })

    except Exception as e:
        logger.error(f"Error deleting model: {str(e)}")
        return jsonify({"error": str(e)}), 500

@lstm_train.route('/models/<version>/activate', methods=['POST'])
def activate_model(version):
    """Activate a specific model version"""
    try:
        version_path = Path(f"logs/{version}")
        if not version_path.exists():
            return jsonify({"error": "Model version not found"}), 404

        # Backup current asset_preprocessing before activating new model
        backup_path = backup_current_asset_preprocessing()

        # Clear current asset_preprocessing
        if Path("asset_preprocessing").exists():
            shutil.rmtree("asset_preprocessing")

        # Copy selected version to asset_preprocessing
        shutil.copytree(version_path, "asset_preprocessing")

        # Load and verify the newly activated model
        model_file = Path("asset_preprocessing/arunv_latest.keras")
        metadata_file = Path("asset_preprocessing/training_metadata.json")
        
        if not (model_file.exists() and metadata_file.exists()):
            # Rollback if files are missing
            if backup_path:
                shutil.rmtree("asset_preprocessing", ignore_errors=True)
                shutil.copytree(backup_path, "asset_preprocessing")
            return jsonify({"error": "Failed to verify activated model"}), 500

        return jsonify({
            "message": f"Successfully activated model version {version}",
            "activated_version": version,
            "previous_backup": str(backup_path) if backup_path else None
        })

    except Exception as e:
        logger.error(f"Error activating model: {str(e)}")
        # Attempt rollback on error
        if backup_path:
            try:
                shutil.rmtree("asset_preprocessing", ignore_errors=True)
                shutil.copytree(backup_path, "asset_preprocessing")
            except Exception as rollback_error:
                logger.error(f"Rollback failed: {str(rollback_error)}")
        return jsonify({"error": str(e)}), 500