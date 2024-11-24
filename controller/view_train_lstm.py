from flask import Flask, render_template, request, jsonify, Response, Blueprint, flash, redirect, url_for
from threading import Thread
from queue import Queue, Empty
import json
import datetime
import traceback
import os
import shutil
from utils.lstm.config import Config, logger
from utils.lstm.preprocessing import create_version_folder, preprocess_data
from utils.lstm.model import create_model, train_model_with_progress
import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict

train_lstm = Blueprint('train_lstm', __name__, template_folder='templates')
logger = logging.getLogger(__name__)

def get_training_metadata(model_dir: Path) -> Dict:
    """Extract training metadata directly from model directory."""
    try:
        # Get metadata file path
        metadata_path = model_dir / "training_metadata.json"
        
        if not metadata_path.exists():
            logger.warning(f"No training_metadata.json found in {model_dir}")
            return None
        
        logger.debug(f"Reading metadata from: {metadata_path}")
        with open(metadata_path, "r") as f:
            data = json.load(f)
            
            # Get training history
            history = data.get("training_results", {})
            
            # Extract and format the metrics
            duration = history.get("total_duration", "N/A")
            
            # Handle accuracy
            accuracy = history.get("final_accuracy", history.get("final_accuracy", 0))
            if isinstance(accuracy, (int, float)):
                formatted_accuracy = f"{round(accuracy * 100, 2)}%"
            else:
                formatted_accuracy = "N/A"
            
            # Handle loss
            loss = history.get("final_loss", history.get("loss", 0))
            if isinstance(loss, (int, float)):
                formatted_loss = round(loss, 4)
            else:
                formatted_loss = "N/A"
            
            return {
                "created_at": data.get("training_date", 
                    datetime.fromtimestamp(metadata_path.stat().st_ctime).strftime("%Y-%m-%dT%H:%M:%S.%f")),
                "duration": duration,
                "accuracy": formatted_accuracy,
                "loss": formatted_loss
            }
            
    except Exception as e:
        logger.error(f"Error reading metadata for model {model_dir}: {str(e)}")
        logger.exception(e)  # Print stack trace for debugging
        return None

def list_models() -> List[Dict]:
    """List all models in the logs directory with their metadata."""
    models = []
    logs_path = Path(Config.LOGS_DIRECTORY)
    
    try:
        # Ensure logs directory exists
        if not logs_path.exists():
            logger.warning(f"Logs directory {Config.LOGS_DIRECTORY} does not exist")
            return []
        
        # Get all model directories
        model_dirs = [d for d in logs_path.iterdir() if d.is_dir()]
        
        for model_dir in model_dirs:
            # Get metadata from the model directory
            metadata = get_training_metadata(model_dir)
            
            if metadata:
                model_info = {
                    "name": model_dir.name,
                    "status": "completed",
                    **metadata
                }
                logger.debug(f"Found model with metadata: {model_info}")
            else:
                # Default values if no metadata found
                model_info = {
                    "name": model_dir.name,
                    "status": "incomplete",
                    "created_at": datetime.fromtimestamp(model_dir.stat().st_ctime).strftime("%Y-%m-%dT%H:%M:%S.%f"),
                    "duration": "N/A",
                    "accuracy": "N/A",
                    "loss": "N/A"
                }
                logger.debug(f"Found model without metadata: {model_info}")
            
            models.append(model_info)
        
        # Sort models by creation date (newest first)
        models.sort(key=lambda x: x["created_at"], reverse=True)
        
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        logger.exception(e)
    
    return models

#GET MODEL
@train_lstm.route('/manage/model', methods=['GET'])
def get_models():
    try:
        models = list_models()
        # Debug logging
        logger.info(f"Found {len(models)} models")
        for model in models:
            logger.info(f"Model: {model['name']}")
            logger.info(f"  Created: {model['created_at']}")
            logger.info(f"  Duration: {model['duration']}")
            logger.info(f"  Accuracy: {model['accuracy']}")
            logger.info(f"  Loss: {model['loss']}")
        
        return render_template('pages/index-train-lstm.html', models=models)
    except Exception as e:
        logger.error(f"Error in get_models route: {str(e)}")
        logger.exception(e)
        flash("Error loading models", "danger")
        return render_template('pages/index-train-lstm.html', models=[]), 500

@train_lstm.route('/model/<model_name>/details', methods=['GET'])
def get_models_details(model_name):
    try:
        logs_path = Path(Config.LOGS_DIRECTORY)
        model_dir = logs_path / model_name
        
        # Baca kedua file JSON
        model_config_path = model_dir / "model_config.json"
        training_metadata_path = model_dir / "training_metadata.json"
        
        if not model_config_path.exists() or not training_metadata_path.exists():
            logger.warning(f"Configuration files not found for model {model_name}")
            flash("Model details not found", "error")
            return redirect(url_for('train_lstm.get_models'))
        
        # Baca kedua file
        with open(model_config_path, 'r') as f:
            model_config = json.load(f)
            
        with open(training_metadata_path, 'r') as f:
            training_metadata = json.load(f)
        
        # Gabungkan data untuk template
        combined_data = {
            "model_config": model_config,
            "training_metadata": training_metadata
        }
            
        logger.info(f"Loading details for model {model_name}")    
        
        return render_template('partials/details.html', 
                             model_name=model_name, 
                             data=combined_data)
                             
    except Exception as e:
        logger.error(f"Error in get_models_details route: {str(e)}")
        logger.exception(e)
        flash("Error loading model details", "danger")
        return redirect(url_for('train_lstm.get_models'))
    

#GET MODEL METRICS
@train_lstm.route('/model/<model_name>/metrics', methods=['GET'])
def get_model_metrics(model_name):
    try:
        logs_path = Path(Config.LOGS_DIRECTORY)
        model_dir = logs_path / model_name
        metadata_path = model_dir / "training_history.json"
        
        if not metadata_path.exists():
            logger.warning(f"No training_metadata.json found for model {model_name}")
            flash("Model metrics not found", "error")
            return redirect(url_for('train_lstm.get_models'))
            
        with open(metadata_path, "r") as f:
            data = json.load(f)
            training_history = data.get("epochs", [])
            
            # Extract epoch level metrics
            epochs = []
            accuracies = []
            losses = []
            
            for epoch in training_history:
                epochs.append(epoch['epoch'])
                accuracies.append(epoch['metrics']['accuracy'])
                losses.append(epoch['metrics']['loss'])
            
            summary = {
                'final_accuracy': data.get('final_accuracy', 0) * 100,  # Convert to percentage
                'final_loss': data.get('final_loss', 0),
                'best_accuracy': data.get('best_accuracy', 0) * 100,    # Convert to percentage
                'best_epoch': data.get('best_epoch', 0),
                'total_duration': data.get('total_duration', 'N/A')
            }
        logger.error(f"Get data:\n {summary, epochs, accuracies, losses}")    
        logger.error(f"Get Training:\n {metadata_path}")    
        return render_template('partials/metrics.html', 
                            model_name=model_name,
                            epochs=epochs,
                            accuracies=accuracies,
                            losses=losses,
                            summary=summary)
    except Exception as e:
        logger.error(f"Error getting metrics for model {model_name}: {str(e)}")
        logger.exception(e)
        flash(f"Error loading metrics {e}", "error"), 500
        return redirect(url_for('train_lstm.get_models'))

@train_lstm.route('/train', methods=['POST'])
def train_model():
    try:
        data = request.get_json()
        model_name = data.get("model_name")
        
        # Use default params if not provided
        # Construct layer configuration
        layers = []
        if data.get("layers"):
            layers = data.get("layers")
        else:
            # Default structure with LSTM and output layers
            layers = [
                {
                    'type': 'LSTM',
                    'params': {
                        'units': data.get("lstm_units", Config.DEFAULT_PARAMS['layers'][0]['params']['units']),
                        'dropout': data.get("lstm_dropout", Config.DEFAULT_PARAMS['layers'][0]['params']['dropout']),
                        'recurrent_dropout': data.get("lstm_recurrent_dropout", Config.DEFAULT_PARAMS['layers'][0]['params']['recurrent_dropout']),
                        'return_sequences': False  # Force to False for final prediction
                    }
                }
            ]
            
            # Add Dense layer if specified
            if data.get("dense_units"):
                layers.append({
                    'type': 'Dense',
                    'params': {
                        'units': data.get("dense_units", Config.DEFAULT_PARAMS['layers'][2]['params']['units']),
                        'activation': data.get("dense_activation", Config.DEFAULT_PARAMS['layers'][2]['params']['activation'])
                    }
                })
                
                if data.get("dense_dropout"):
                    layers.append({
                        'type': 'Dropout',
                        'params': {
                            'rate': data.get("dense_dropout", Config.DEFAULT_PARAMS['layers'][3]['params']['rate'])
                        }
                    })
        
        # Construct optimizer configuration
        optimizer_config = {
            'name': data.get("optimizer_name", "adam"),
            'params': {
                'learning_rate': data.get("learning_rate", Config.OPTIMIZER_CONFIGS['adam']['learning_rate'])
            }
        }
        
        # Optimizer-specific parameters
        optimizer_mappings = {
            'adam': ['beta_1', 'beta_2', 'epsilon', 'amsgrad'],
            'sgd': ['momentum', 'nesterov'],
            'rmsprop': ['rho', 'momentum', 'epsilon', 'centered'],
            'adagrad': ['initial_accumulator_value', 'epsilon'],
            'adadelta': ['rho', 'epsilon'],
            'adamax': ['beta_1', 'beta_2', 'epsilon'],
            'nadam': ['beta_1', 'beta_2', 'epsilon']
        }
        
        # Update optimizer parameters based on selected optimizer
        if optimizer_config['name'] in optimizer_mappings:
            optimizer_config['params'].update({
                param: data.get(param, Config.OPTIMIZER_CONFIGS[optimizer_config['name']][param])
                for param in optimizer_mappings[optimizer_config['name']]
            })
        
        # Complete configuration
        config = {
            # Embedding Layer Parameters
            "embedding_dim": data.get("embedding_dim", Config.DEFAULT_PARAMS['embedding_dim']),
            "embedding_dropout": data.get("embedding_dropout", Config.DEFAULT_PARAMS['embedding_dropout']),
            "mask_zero": data.get("mask_zero", Config.DEFAULT_PARAMS['mask_zero']),
            
            # Layer Architecture
            "layers": layers,
            
            # Optimizer Configuration
            "optimizer": optimizer_config,
            
            # Training Parameters
            "batch_size": data.get("batch_size", Config.DEFAULT_PARAMS['batch_size']),
            "epochs": data.get("epochs", Config.DEFAULT_PARAMS['epochs']),
            
            # Output Layer Configuration
            "output_activation": "softmax"  # Force softmax for classification
        }

        # Create version folder and preprocess data
        version_path = create_version_folder(model_name)
        X_train, Y_train, vocab_size, num_classes, sequence_length = preprocess_data(version_path, model_name)
        
        # Log shapes for debugging
        logger.info(f"Training shapes - X: {X_train.shape}, Y: {Y_train.shape}")
        logger.info(f"Model parameters - vocab_size: {vocab_size}, num_classes: {num_classes}, sequence_length: {sequence_length}")
        
        # Save model configuration
        config_path = version_path / "model_config.json"
        with open(config_path, 'w') as f:
            json.dump({
                **config,
                "vocab_size": vocab_size,
                "num_classes": num_classes,
                "sequence_length": sequence_length,
                "training_date": datetime.now().isoformat()
            }, f, indent=4)
        
        # Return the streaming response
        return train_model_with_progress(
            model_name, 
            version_path, 
            X_train, 
            Y_train, 
            vocab_size, 
            num_classes, 
            sequence_length, 
            config
        )

    except Exception as e:
        logger.error(f"Training error: {str(e)}")
        logger.error(traceback.format_exc())  # Log full traceback
        return jsonify({"error": str(e)}), 500

@train_lstm.route('/model/<model_name>/delete', methods=['POST'])  # Ubah ke POST karena HTML form tidak support DELETE
def delete_model(model_name):
    """
    Delete a model directory and all its contents
    """
    try:
        logs_path = Path(Config.LOGS_DIRECTORY)
        model_dir = logs_path / model_name
        
        # Cek apakah direktori ada
        if not model_dir.exists():
            logger.warning(f"Model directory not found: {model_name}")
            flash(f"Model {model_name} not found", "error")
            return redirect(url_for('train_lstm.get_models'))
            
        # Hapus direktori dan semua isinya
        shutil.rmtree(model_dir)
        
        logger.info(f"Successfully deleted model: {model_name}")
        flash(f"Model {model_name} has been successfully deleted", "success")
        
    except PermissionError as e:
        logger.error(f"Permission error while deleting model {model_name}: {str(e)}")
        flash("Permission denied: Unable to delete model directory", "error")
        
    except Exception as e:
        logger.error(f"Error deleting model {model_name}: {str(e)}")
        logger.exception(e)
        flash(f"Error deleting model: {str(e)}", "error")
        
    return redirect(url_for('train_lstm.get_models'))