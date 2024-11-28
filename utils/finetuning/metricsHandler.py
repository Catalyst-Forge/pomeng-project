import pandas as pd
from pathlib import Path
import base64
from io import StringIO
import numpy as np
from typing import Dict, List, Optional, Union
import logging
import json
import datetime

class MetricsHandler:
    def __init__(self, metrics_folder: str = "metrics"):
        self.metrics_folder = Path(metrics_folder)
        self.metrics_folder.mkdir(exist_ok=True)
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('MetricsHandler')

    def validate_file_id(self, file_id: str) -> bool:
        """Validate file ID format."""
        import re
        return bool(re.match(r'^[\w\-]+$', file_id))

    def process_raw_content(self, raw_content: bytes) -> Optional[pd.DataFrame]:
        """Process raw content into a pandas DataFrame with improved error handling."""
        try:
            # Try to decode as base64 first
            try:
                decoded_content = base64.b64decode(raw_content).decode('utf-8')
                df = pd.read_csv(StringIO(decoded_content))
            except (base64.binascii.Error, UnicodeDecodeError):
                # If not base64, try direct CSV parsing
                df = pd.read_csv(StringIO(raw_content.decode('utf-8')))

            # Validate required columns
            required_columns = ["step", "train_loss", "train_accuracy", "valid_loss", "valid_mean_token_accuracy"]
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                self.logger.error(f"Missing required columns: {missing_columns}")
                return None

            # Convert numeric columns except step
            numeric_columns = [col for col in required_columns if col != "step"]
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Ensure step is integer
            df['step'] = df['step'].astype(int)

            # Sort by step
            df = df.sort_values('step')
            
            self.logger.info(f"Successfully processed data with {len(df)} rows")
            return df

        except Exception as e:
            self.logger.error(f"Error processing content: {str(e)}", exc_info=True)
            return None

    def calculate_metrics(self, df: pd.DataFrame) -> Dict[str, Union[List[float], float, None]]:
        """Calculate metrics with improved error handling and validation."""
        try:
            # Ensure DataFrame is not empty
            if df.empty:
                self.logger.error("Empty DataFrame provided")
                return {}

            # Process series with proper error handling
            def process_series(series: pd.Series, is_step: bool = False) -> List[Optional[Union[int, float]]]:
                try:
                    if is_step:
                        return [int(x) if pd.notnull(x) else None for x in series]
                    return [float(x) if pd.notnull(x) else None for x in series]
                except Exception as e:
                    self.logger.error(f"Error processing series {series.name}: {str(e)}")
                    return [None] * len(series)

            # Main metrics processing
            metrics = {
                "step": process_series(df["step"], is_step=True),
                "train_loss": process_series(df["train_loss"]),
                "train_accuracy": process_series(df["train_accuracy"]),
                "valid_loss": process_series(df["valid_loss"]),
                "valid_mean_token_accuracy": process_series(df["valid_mean_token_accuracy"])
            }

            # Calculate statistical metrics
            def safe_calculate(series: pd.Series, operation: str) -> Optional[float]:
                try:
                    clean_series = series.dropna()
                    if clean_series.empty:
                        return None
                    if operation == "mean":
                        return float(clean_series.mean())
                    elif operation == "max":
                        return float(clean_series.max())
                    elif operation == "min":
                        return float(clean_series.min())
                except Exception as e:
                    self.logger.error(f"Error calculating {operation} for {series.name}: {str(e)}")
                    return None

            metrics.update({
                "avg_train_loss": safe_calculate(df["train_loss"], "mean"),
                "avg_valid_loss": safe_calculate(df["valid_loss"], "mean"),
                "max_train_accuracy": safe_calculate(df["train_accuracy"], "max"),
                "max_valid_accuracy": safe_calculate(df["valid_mean_token_accuracy"], "max"),
                "min_train_loss": safe_calculate(df["train_loss"], "min"),
                "max_train_loss": safe_calculate(df["train_loss"], "max"),
                "min_valid_loss": safe_calculate(df["valid_loss"], "min"),
                "max_valid_loss": safe_calculate(df["valid_loss"], "max")
            })

            # Data quality metrics
            metrics.update({
                "data_points": len(df),
                "valid_train_loss_points": int(df["train_loss"].notna().sum()),
                "valid_valid_loss_points": int(df["valid_loss"].notna().sum()),
                "valid_train_accuracy_points": int(df["train_accuracy"].notna().sum()),
                "valid_valid_accuracy_points": int(df["valid_mean_token_accuracy"].notna().sum())
            })

            # Log metrics summary
            self.logger.info(f"Calculated metrics summary: {json.dumps({k: v for k, v in metrics.items() if not isinstance(v, list)})}")
            
            return metrics

        except Exception as e:
            self.logger.error(f"Error calculating metrics: {str(e)}", exc_info=True)
            return {}

    def save_metrics(self, file_id: str, df: pd.DataFrame) -> Optional[str]:
        """Save metrics with error handling."""
        try:
            file_path = self.metrics_folder / f"{file_id}.csv"
            df.to_csv(file_path, index=False)
            self.logger.info(f"Saved metrics to {file_path}")
            return str(file_path)
        except Exception as e:
            self.logger.error(f"Error saving metrics: {str(e)}", exc_info=True)
            return None

    def read_metrics(self, file_id: str) -> Optional[Dict]:
        """Read metrics with improved error handling."""
        try:
            file_path = self.metrics_folder / f"{file_id}.csv"
            if not file_path.exists():
                self.logger.warning(f"Metrics file not found: {file_path}")
                return None

            df = pd.read_csv(file_path)
            metrics = self.calculate_metrics(df)
            
            if not metrics:
                self.logger.error("Failed to calculate metrics from saved file")
                return None

            return metrics

        except Exception as e:
            self.logger.error(f"Error reading metrics file {file_id}: {str(e)}", exc_info=True)
            return None