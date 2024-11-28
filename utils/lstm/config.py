import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration settings
class Config:
    DATASET_PATH = 'dataset/arun.json'
    LOGS_DIRECTORY = 'logs'
    MODEL_EXTENSIONS = {
        'preprocessing': ['words.pkl', 'classes.pkl', 'le.pkl', 'tokenizer.pkl', 'metadata.json'],
        'model': ['.keras', 'training_history.json', 'training_metadata.json']
    }
    
    # Default model training parameters
    DEFAULT_PARAMS = {
        # Embedding Layer Parameters
        'embedding_dim': 16,
        'embedding_dropout': 0.2,
        'mask_zero': True,
        'mask_zero': 16,
        
        # Default Layer Structure
        'layers': [
            {
                'type': 'LSTM',
                'params': {
                    'units': 64,
                    'dropout': 0.2,
                    'recurrent_dropout': 0.2,
                    'return_sequences': True
                }
            },
            {
                'type': 'LSTM',
                'params': {
                    'units': 32,
                    'dropout': 0.2,
                    'recurrent_dropout': 0.2,
                    'return_sequences': False
                }
            },
            {
                'type': 'Dense',
                'params': {
                    'units': 32,
                    'activation': 'relu'
                }
            },
            {
                'type': 'Dropout',
                'params': {
                    'rate': 0.2
                }
            }
        ],
        
        # Training Parameters
        'batch_size': 64,
        'epochs': 10,
        
        # Optimizer Configuration
        'optimizer': {
            'name': 'adam',
            'params': {
                'learning_rate': 0.001,
                'beta_1': 0.9,
                'beta_2': 0.999,
                'epsilon': 1e-7,
                'amsgrad': False
            }
        },
        
        # Output Layer Configuration
        'output_activation': 'softmax'
    }
    
    # Optimizer specific configurations
    OPTIMIZER_CONFIGS = {
        'adam': {
            'learning_rate': 0.001,
            'beta_1': 0.9,
            'beta_2': 0.999,
            'epsilon': 1e-7,
            'amsgrad': False
        },
        'sgd': {
            'learning_rate': 0.01,
            'momentum': 0.0,
            'nesterov': False
        },
        'rmsprop': {
            'learning_rate': 0.001,
            'rho': 0.9,
            'momentum': 0.0,
            'epsilon': 1e-7,
            'centered': False
        },
        'adagrad': {
            'learning_rate': 0.01,
            'initial_accumulator_value': 0.1,
            'epsilon': 1e-7
        },
        'adadelta': {
            'learning_rate': 1.0,
            'rho': 0.95,
            'epsilon': 1e-7
        },
        'adamax': {
            'learning_rate': 0.002,
            'beta_1': 0.9,
            'beta_2': 0.999,
            'epsilon': 1e-7
        },
        'nadam': {
            'learning_rate': 0.002,
            'beta_1': 0.9,
            'beta_2': 0.999,
            'epsilon': 1e-7
        }
    }
    
    LOSS_CONFIGS = {
    'binary_crossentropy': {
        'from_logits': False,
        'label_smoothing': 0.0
    },
    'categorical_crossentropy': {
        'from_logits': False,
        'label_smoothing': 0.0
    },
    'sparse_categorical_crossentropy': {
        'from_logits': False,
    },
    'mean_squared_error': {},  # No specific parameters
    'mean_absolute_error': {},  # No specific parameters
    'huber': {
        'delta': 1.0
    },
    'kl_divergence': {
        'from_logits': False
    },
    'poisson': {
        'from_logits': False
    }
}