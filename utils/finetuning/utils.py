from flask import Flask, render_template, redirect, url_for, jsonify, flash, request, make_response
import os
import datetime
import logging
from marshmallow import ValidationError
import requests
import json
from typing import Dict, Optional
from utils.finetuning.validator import FineTuningJobSchema, BASE_MODELS
import logging
from utils.finetuning.metricsHandler import MetricsHandler
from config import config
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect

load_dotenv()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def update_selected_model(model_id: str) -> bool:
    """
    Update selected model in .env file and environment variables
    
    Args:
        model_id (str): ID of the model to be selected
        
    Returns:
        bool: True if update successful, False otherwise
    """
    env_path = Path('.env')
    
    try:
        # Ensure .env file exists
        env_path.touch(exist_ok=True)
        
        # Read existing content with proper encoding
        content = []
        with open(env_path, 'r', encoding='utf-8') as file:
            content = file.readlines()
        
        # Clean existing content
        content = [line.strip() for line in content if line.strip()]
        
        # Update or add OPENAI_MODEL_SELECTED
        model_var = f'OPENAI_MODEL_SELECTED={model_id}'
        updated = False
        
        for i, line in enumerate(content):
            if line.startswith('OPENAI_MODEL_SELECTED='):
                content[i] = model_var
                updated = True
                break
                
        if not updated:
            content.append(model_var)
            
        # Write back to file
        with open(env_path, 'w', encoding='utf-8') as file:
            file.write('\n'.join(content) + '\n')
            
        # Update runtime environment
        os.environ['OPENAI_MODEL_SELECTED'] = model_id
        load_dotenv(override=True)
        
        return True
        
    except Exception as e:
        logger.error(f"Error updating selected model: {str(e)}")
        return False

def validate_model_id(model_id: str, client: OpenAI) -> Optional[str]:
    """
    Validate if model_id exists in available models
    
    Args:
        model_id (str): ID of the model to validate
        client: OpenAI client instance
        
    Returns:
        Optional[str]: Error message if validation fails, None if successful
    """
    try:
        if not model_id:
            return "model_id cannot be empty"
            
        response_models = client.models.list()
        available_models = [model.id for model in response_models.data]
        
        if model_id not in available_models:
            return f"Model {model_id} not found in available models"
            
        return None
        
    except Exception as e:
        return f"Error validating model: {str(e)}"

def get_checkpoints(fine_tuning_id):
    try:
        headers = {
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"https://api.openai.com/v1/fine_tuning/jobs/{fine_tuning_id}/checkpoints",
            headers=headers
        )
        
        if response.status_code == 200:
            checkpoints_data = []
            data = response.json()
            
            for checkpoint in data.get('data', []):
                checkpoint_info = {
                    "id": checkpoint.get('id', "N/A"),
                    "step_number": checkpoint.get('step_number', "N/A"),
                    "created_at": datetime.datetime.fromtimestamp(checkpoint.get('created_at', 0)).strftime('%Y-%m-%d %H:%M:%S') if checkpoint.get('created_at') else "N/A",
                    "fine_tuned_model_checkpoint": checkpoint.get('fine_tuned_model_checkpoint', "N/A"),
                    "metrics": {
                        "valid_loss": checkpoint.get('metrics', {}).get('full_valid_loss', "N/A"),
                        "valid_accuracy": checkpoint.get('metrics', {}).get('full_valid_mean_token_accuracy', "N/A")
                    }
                }
                checkpoints_data.append(checkpoint_info)
            return checkpoints_data
        else:
            print(f"Error fetching checkpoints: Status code {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Error fetching checkpoints: {str(e)}")
        return []
