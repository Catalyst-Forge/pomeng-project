from flask import flash
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout
from utils.lstm.config import logger, Config
from flask import Response
from threading import Thread
from queue import Queue, Empty
import datetime
import json
import platform
import os
import psutil
def create_model(vocab_size, output_length, sequence_length, config):
    """
    Create a sequential neural network model with configurable layers and optimizers
    
    Parameters:
    -----------
    vocab_size : int
        Size of the vocabulary (number of unique words)
    output_length : int
        Number of output classes
    sequence_length : int
        Length of input sequences
    config : dict
        Configuration dictionary containing model parameters
    """
    model = Sequential()
    
    # Add Embedding Layer
    embedding_config = {
        'input_dim': vocab_size,
        'output_dim': config.get('embedding_dim', 16),
        'mask_zero': config.get('mask_zero', True),
        'input_length': sequence_length  # Make sure to use the sequence_length parameter
    }
    model.add(Embedding(**embedding_config))
    
    if config.get('embedding_dropout', 0) > 0:
        model.add(Dropout(rate=config.get('embedding_dropout')))

    # Add layers from configuration
    layers = config.get('layers', [])
    for i, layer in enumerate(layers):
        layer_type = layer.get('type')
        layer_params = layer.get('params', {})

        if layer_type == 'LSTM':
            # Only allow return_sequences=True if it's not the last LSTM layer
            is_last_lstm = not any(l.get('type') == 'LSTM' for l in layers[i+1:])
            lstm_config = {
                'units': layer_params.get('units', 64),
                'dropout': layer_params.get('dropout', 0.2),
                'recurrent_dropout': layer_params.get('recurrent_dropout', 0.2),
                'return_sequences': False if is_last_lstm else layer_params.get('return_sequences', True),
                'use_cudnn': False
            }
            model.add(LSTM(**lstm_config))
            
        elif layer_type == 'Dense':
            dense_config = {
                'units': layer_params.get('units', 32),
                'activation': layer_params.get('activation', 'relu')
            }
            model.add(Dense(**dense_config))
            
        elif layer_type == 'Dropout':
            dropout_config = {
                'rate': layer_params.get('rate', 0.2)
            }
            model.add(Dropout(**dropout_config))

    # Add final output layer
    model.add(Dense(output_length, activation=config.get('output_activation', 'softmax')))
    
    # Get optimizer configuration
    optimizer_config = config.get('optimizer', {})
    optimizer_name = optimizer_config.get('name', 'adam').lower()
    optimizer_params = optimizer_config.get('params', Config.OPTIMIZER_CONFIGS[optimizer_name])
    
    # Create optimizer based on configuration
    if optimizer_name == 'adam':
        optimizer = tf.keras.optimizers.Adam(**optimizer_params)
    elif optimizer_name == 'sgd':
        optimizer = tf.keras.optimizers.SGD(**optimizer_params)
    elif optimizer_name == 'rmsprop':
        optimizer = tf.keras.optimizers.RMSprop(**optimizer_params)
    elif optimizer_name == 'adagrad':
        optimizer = tf.keras.optimizers.Adagrad(**optimizer_params)
    elif optimizer_name == 'adadelta':
        optimizer = tf.keras.optimizers.Adadelta(**optimizer_params)
    elif optimizer_name == 'adamax':
        optimizer = tf.keras.optimizers.Adamax(**optimizer_params)
    elif optimizer_name == 'nadam':
        optimizer = tf.keras.optimizers.Nadam(**optimizer_params)
    else:
        raise ValueError(f"Unsupported optimizer: {optimizer_name}")
    
    # Compile model
    model.compile(
        loss='categorical_crossentropy',
        optimizer=optimizer,
        metrics=['accuracy']
    )
    
    return model

def train_model_with_progress(model_name, version_path, X_train, Y_train, vocab_size, num_classes, sequence_length, config):
    """
    Train model with progress tracking and streaming response
    
    Args:
        model_name (str): Name of the model
        version_path (Path): Path to save model version
        X_train (np.ndarray): Training input data
        Y_train (np.ndarray): Training target data
        vocab_size (int): Size of vocabulary
        num_classes (int): Number of output classes
        sequence_length (int): Maximum sequence length
        config (dict): Model configuration parameters
    """
    def generate_training_progress():
        model = create_model(vocab_size, num_classes, sequence_length, config)
        
        batch_size = config.get('batch_size', 64)
        epochs = config.get('epochs', 10)

        # Initialize training history
        training_history = {
            "epochs": [],
            "start_time": datetime.datetime.now().isoformat(),
            "total_steps": len(X_train) // batch_size * epochs
        }

        class DetailedTrainingCallback(tf.keras.callbacks.Callback):
            def __init__(self):
                super(DetailedTrainingCallback, self).__init__()
                self.current_epoch_data = None
                self.current_epoch_steps = []
                self.sse_queue = Queue()
            
            def on_train_begin(self, logs=None):
                logger.info("Training started")
            
            def on_train_end(self, logs=None):
                logger.info("Training completed")

            def on_epoch_begin(self, epoch, logs=None):
                logger.info(f"Starting Epoch {epoch + 1}")
                self.current_epoch_data = {
                    "epoch": epoch + 1,
                    "start_time": datetime.datetime.now().isoformat(),
                    "steps": []
                }
                self.current_epoch_steps = []
                
            def on_batch_end(self, batch, logs=None):
                try:
                    batch_data = {
                        "batch": batch,
                        "loss": float(logs.get('loss', 0)),
                        "accuracy": float(logs.get('accuracy', 0))
                    }
                    self.current_epoch_steps.append(batch_data)
                except Exception as e:
                    logger.error(f"Error tracking batch progress: {e}")

            def on_epoch_end(self, epoch, logs=None):
                try:
                    end_time = datetime.datetime.now()
                    start_time = datetime.datetime.fromisoformat(self.current_epoch_data["start_time"])
                    
                    self.current_epoch_data.update({
                        "end_time": end_time.isoformat(),
                        "duration": str(end_time - start_time),
                        "steps": self.current_epoch_steps.copy(),
                        "metrics": {
                            "accuracy": float(logs.get('accuracy', 0)),
                            "loss": float(logs.get('loss', 0))
                        }
                    })
                    
                    training_history["epochs"].append(self.current_epoch_data)
                    
                    logger.info(f"Epoch {epoch + 1} completed. Accuracy: {logs.get('accuracy', 0)}, Loss: {logs.get('loss', 0)}")
                    
                    self.sse_queue.put({
                        'progress': int(((epoch + 1) / epochs) * 100),
                        'epoch_data': {
                            "epoch": epoch + 1,
                            "accuracy": float(logs.get('accuracy', 0)),
                            "loss": float(logs.get('loss', 0))
                        }
                    })
                except Exception as e:
                    logger.error(f"Error in on_epoch_end: {e}")
        
        callback = DetailedTrainingCallback()
        
        def stream_response():
            def train_model_thread():
                try:
                    logger.info("Starting model training...")
                    history = model.fit(
                        X_train, Y_train,
                        batch_size=batch_size,
                        epochs=epochs,
                        verbose=1,
                        callbacks=[callback]
                    )
                    logger.info(f"Training completed. History available: {history is not None}")
                    logger.info(f"Recorded epochs: {len(training_history['epochs'])}")
                except Exception as e:
                    logger.error(f"Model training failed: {e}")
                    logger.exception("Detailed traceback:")
                    callback.sse_queue.put({'error': str(e)})

            training_thread = Thread(target=train_model_thread)
            training_thread.start()

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

            # Save model and metadata if training was successful
            if training_history.get("epochs"):
                try:
                    # Save the model
                    model_path = version_path / "model.keras"
                    model.save(model_path)
                    
                    # Update and save training history
                    training_end_time = datetime.datetime.now()
                    training_start_time = datetime.datetime.fromisoformat(training_history["start_time"])
                    training_duration = str(training_end_time - training_start_time)
                    
                    last_epoch = training_history["epochs"][-1]
                    final_accuracy = last_epoch["metrics"]["accuracy"]
                    final_loss = last_epoch["metrics"]["loss"]
                    
                    best_accuracy = max(epoch["metrics"]["accuracy"] for epoch in training_history["epochs"])
                    best_epoch = next(i + 1 for i, epoch in enumerate(training_history["epochs"]) 
                                    if epoch["metrics"]["accuracy"] == best_accuracy)
                    
                    training_history.update({
                        "end_time": training_end_time.isoformat(),
                        "total_duration": training_duration,
                        "final_accuracy": final_accuracy,
                        "final_loss": final_loss,
                        "best_accuracy": best_accuracy,
                        "best_epoch": best_epoch
                    })
                    
                    # Save detailed training history
                    with open(version_path / 'training_history.json', 'w') as f:
                        json.dump(training_history, f, indent=4)
                    
                    # Save comprehensive metadata
                    training_metadata = {
                        "model_info": {
                            "name": model_name,
                            "version_path": str(version_path),
                            "creation_date": datetime.datetime.now().isoformat(),
                            "framework_version": tf.__version__,
                        },
                        "data_info": {
                            "training_samples": len(X_train),
                            "vocab_size": vocab_size,
                            "num_classes": num_classes,
                            "sequence_length": sequence_length
                        },
                        "model_architecture": {
                            "embedding": {
                                "dim": config.get('embedding_dim', 16),
                                "mask_zero": config.get('mask_zero', True),
                                "dropout": config.get('embedding_dropout', 0),
                            },
                            "layers": config.get('layers', []),
                            "output_activation": config.get('output_activation', 'softmax'),
                        },
                        "training_config": {
                            "optimizer": config.get('optimizer', {}),
                            "batch_size": batch_size,
                            "epochs": epochs,
                            "metrics": ['accuracy'],
                        },
                        "training_results": training_history,
                        "system_info": {
                            "python_version": platform.python_version(),
                            "os_platform": platform.platform(),
                            "cpu_count": os.cpu_count(),
                            "memory_info": psutil.virtual_memory()._asdict() if psutil else None,
                            "gpu_info": tf.config.list_physical_devices('GPU'),
                        }
                    }
                    
                    with open(version_path / 'training_metadata.json', 'w') as f:
                        json.dump(training_metadata, f, indent=4)
                        
                    yield f"data:{json.dumps({'progress': 100, 'training_complete': True})}\n\n"
                except Exception as e:
                    logger.error(f"Error saving model and metadata: {e}")
                    yield f"data:{json.dumps({'error': f'Error saving model: {str(e)}'})}\n\n"
            else:
                error_msg = "No epochs were recorded during training"
                logger.error(error_msg)
                yield f"data:{json.dumps({'error': error_msg})}\n\n"

        return stream_response()

    return Response(generate_training_progress(), mimetype='text/event-stream', content_type='text/event-stream')
