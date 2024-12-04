from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    jsonify,
    flash,
    request,
    make_response,
    Blueprint,
)
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
from utils.finetuning.utils import filter_chatbot_models
from config import config
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
from utils.finetuning.utils import (
    update_selected_model,
    validate_model_id,
    get_checkpoints,
)
import logging

logger = logging.getLogger(__name__)
client = OpenAI()
metrics_handler = MetricsHandler()
train_finetuning = Blueprint(
    "train_finetuning",
    __name__,
    template_folder="templates",
    url_prefix="/dashboard/train-model/fine-tuning",
)


@train_finetuning.route("/")
def index():
    return render_template("pages/train-model/fine-tuning/fine-tuning-index.html")


@train_finetuning.route("/list-models")
def list_models():
    try:
        response_model = client.models.list()
        models = []

        for model in response_model.data:
            model_data = {
                "id": model.id,
                "object": model.object,
                "created": datetime.datetime.fromtimestamp(model.created).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "owned_by": model.owned_by,
            }
            models.append(model_data)

        chat_models = [
            model
            for model in models
            if (
                # Include OpenAI and user-owned models
                model["owned_by"] in ["openai", "openai-internal", "system"]
                or model["owned_by"].startswith("user")
            )
            and (
                # Specific chatbot-related models
                model["id"].startswith(("gpt-", "chatgpt", "o1-", "gpt4o", "ft:"))
                or any(
                    keyword in model["id"]
                    for keyword in ["turbo", "preview", "mini", "4o"]
                )
            )
            and not any(
                # Explicitly exclude non-chatbot models
                keyword in model["id"]
                for keyword in [
                    "embedding",
                    "whisper",
                    "dall-e",
                    "tts",
                    "text-",
                    "davinci",
                    "babbage",
                    "audio",
                ]
            )
        ]

        return render_template(
            "pages/train-model/fine-tuning/list-models.html",
            models=chat_models,
            total=len(chat_models),
        )

    except Exception as e:
        return render_template(
            "pages/train-model/fine-tuning/list-models.html",
            error=str(e),
            models=[],
            total=0,
        )


@train_finetuning.route("/list-models/<model_id>", methods=["POST"])
def select_model(model_id: str):
    try:
        validation_error = validate_model_id(model_id, client)
        if validation_error:
            flash(validation_error, "error")
            return redirect(url_for("train_finetuning.list_models"))

        if update_selected_model(model_id):
            flash(f"Successfully selected model: {model_id}", "success")
            return redirect(url_for("train_finetuning.list_models"))

        flash("Failed to update selected model", "error")
        return redirect(url_for("train_finetuning.list_models"))

    except Exception as e:
        logger.error(f"Error selecting model: {str(e)}")
        flash(str(e), "error")
        return redirect(url_for("train_finetuning.list_models"))


@train_finetuning.route("/list-fine-tuning")
def list_finetunings():
    success_message = request.args.get("message")
    error_message = request.args.get("error")
    try:
        response = client.fine_tuning.jobs.list()

        list_fine_tuned = []
        current_time = datetime.datetime.now().timestamp()

        for finetuning in response.data:
            # Default progress
            progress = 0

            if finetuning.status == "running" and finetuning.estimated_finish:
                try:
                    # Hitung progress berdasarkan waktu
                    start_time = finetuning.created_at
                    estimated_finish_time = finetuning.estimated_finish

                    elapsed_time = current_time - start_time
                    total_time = estimated_finish_time - start_time

                    progress = min(100, int((elapsed_time / total_time) * 100))
                except Exception as e:
                    print(f"Error calculating progress: {e}")
                    progress = 0  # Default jika ada error

            finetuning_data = {
                "id": finetuning.id if finetuning.id else "N/A",
                "data": {
                    "base_model": finetuning.model if finetuning.model else "N/A",
                    "created_at": (
                        datetime.datetime.fromtimestamp(finetuning.created_at).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                        if finetuning.created_at
                        else "N/A"
                    ),
                    "estimated_finish": (
                        datetime.datetime.fromtimestamp(
                            finetuning.estimated_finish
                        ).strftime("%Y-%m-%d %H:%M:%S")
                        if finetuning.estimated_finish
                        else "N/A"
                    ),
                    "fine_tuned_model": (
                        finetuning.fine_tuned_model
                        if finetuning.fine_tuned_model
                        else "N/A"
                    ),
                    "status": finetuning.status if finetuning.status else "N/A",
                    "trained_tokens": (
                        finetuning.trained_tokens
                        if finetuning.trained_tokens
                        else "N/A"
                    ),
                    "result_files": (
                        finetuning.result_files if finetuning.result_files else "N/A"
                    ),
                    "progress": progress,
                },
            }
            list_fine_tuned.append(finetuning_data)

        return render_template(
            "pages/train-model/fine-tuning/list-fine-tunings.html",
            finetunings=list_fine_tuned,
            base_models=BASE_MODELS,
            success_message=success_message,
            error_message=error_message,
        )
    except Exception as e:
        print(f"Error fetching fine-tuning jobs: {str(e)}")
        return render_template(
            "pages/train-model/fine-tuning/list-fine-tunings.html", finetunings=[]
        )


@train_finetuning.route("/<string:fine_tuning_id>")
def finetuning_details(fine_tuning_id):
    try:
        response = client.fine_tuning.jobs.retrieve(fine_tuning_id)
        checkpoints = get_checkpoints(fine_tuning_id)

        finetuning_data = {
            "object": response.object if response.object else "N/A",
            "id": response.id if response.id else "N/A",
            "model": response.model if response.model else "N/A",
            "created_at": (
                datetime.datetime.fromtimestamp(response.created_at).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                if response.created_at
                else "N/A"
            ),
            "finished_at": (
                datetime.datetime.fromtimestamp(response.finished_at).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                if response.finished_at
                else "N/A"
            ),
            "fine_tuned_model": (
                response.fine_tuned_model if response.fine_tuned_model else "N/A"
            ),
            "organization_id": (
                response.organization_id if response.organization_id else "N/A"
            ),
            "result_files": response.result_files if response.result_files else "N/A",
            "status": response.status if response.status else "N/A",
            "validation_file": (
                response.validation_file if response.validation_file else "N/A"
            ),
            "training_file": (
                response.training_file if response.training_file else "N/A"
            ),
            "hyperparameters": {
                "n_epochs": (
                    response.hyperparameters.n_epochs
                    if response.hyperparameters
                    else "N/A"
                ),
                "batch_size": (
                    response.hyperparameters.batch_size
                    if response.hyperparameters
                    else "N/A"
                ),
                "learning_rate_multiplier": (
                    response.hyperparameters.learning_rate_multiplier
                    if response.hyperparameters
                    else "N/A"
                ),
            },
            "trained_tokens": (
                response.trained_tokens if response.trained_tokens else "N/A"
            ),
            "integrations": response.integrations if response.integrations else "N/A",
            "seed": response.seed if response.seed else "N/A",
            "estimated_finish": (
                response.estimated_finish if response.estimated_finish else "N/A"
            ),
            "checkpoints": checkpoints,
        }
        return render_template(
            "pages/train-model/fine-tuning/fine-tuning-detail.html",
            finetuning=finetuning_data,
        )
    except Exception as e:
        return f"Error loading fine-tuning details: {str(e)}"


@train_finetuning.route("/<string:fine_tuning_id>/show-metric")
def show_metrics(fine_tuning_id: str) -> str:
    """
    Display metrics for a specific fine-tuning job.

    Args:
        fine_tuning_id (str): The ID of the fine-tuning job

    Returns:
        str: Rendered HTML template or error message
    """
    logger = logging.getLogger("show_metrics")

    referrer = request.referrer

    try:
        logger.info(f"Processing metrics request for fine-tuning ID: {fine_tuning_id}")

        # Get the fine-tuning job details
        job = client.fine_tuning.jobs.retrieve(fine_tuning_id)
        logger.info(f"Retrieved fine-tuning job: {fine_tuning_id}")

        # Initialize default metrics data structure
        metrics_data: Dict[str, list] = {
            "step": [],
            "train_loss": [],
            "train_accuracy": [],
            "valid_loss": [],
            "valid_mean_token_accuracy": [],
        }

        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if job.result_files:
            file_id = job.result_files[0]
            logger.info(f"Processing result file: {file_id}")

            # Try to read existing metrics first
            metrics_data = metrics_handler.read_metrics(file_id)

            if metrics_data is None:
                logger.info("No cached metrics found, processing raw data")

                # Retrieve and process file content
                content = client.files.content(file_id)
                raw_content = content.read()

                df = metrics_handler.process_raw_content(raw_content)

                if df is not None:
                    # Save and calculate metrics
                    save_path = metrics_handler.save_metrics(file_id, df)
                    if save_path:
                        logger.info(f"Saved metrics to: {save_path}")

                    metrics_data = metrics_handler.calculate_metrics(df)
                    logger.info("Successfully calculated metrics")
                else:
                    logger.error("Failed to process metrics data")
        else:
            logger.warning(
                f"No result files found for fine-tuning job: {fine_tuning_id}"
            )

        logger.info(
            f"Rendering template with metrics data available: {bool(metrics_data)}"
        )

        return render_template(
            "pages/train-model/fine-tuning/chart.html",
            fine_tuning_id=fine_tuning_id,
            metrics=metrics_data,
            generated_time=current_time,
            referrer=referrer,
        )

    except Exception as e:
        logger.error(f"Error in show_metrics: {str(e)}", exc_info=True)
        return f"Error loading metrics: {str(e)}"


@train_finetuning.route("/show-steps/<string:fine_tuning_id>")
@train_finetuning.route("/show-steps/<string:fine_tuning_id>/<int:page>")
def show_steps(fine_tuning_id, page=1):
    logger = logging.getLogger("show_metrics")
    items_per_page = 10

    try:
        logger.info(f"Processing metrics request for fine-tuning ID: {fine_tuning_id}")

        # Get the fine-tuning job details
        job = client.fine_tuning.jobs.retrieve(fine_tuning_id)
        logger.info(f"Retrieved fine-tuning job: {fine_tuning_id}")

        # Initialize variables with defaults
        metrics_data = None
        total_pages = 1
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Get the result files
        result_files = job.result_files

        if result_files:
            file_id = result_files[0]
            logger.info(f"Processing result file: {file_id}")

            # Try to read existing metrics first
            metrics_data = metrics_handler.read_metrics(file_id)

            if metrics_data is None:
                logger.info("No cached metrics found, processing raw data")

                # Retrieve and read file content
                content = client.files.content(file_id)
                raw_content = content.read()

                # Process content
                df = metrics_handler.process_raw_content(raw_content)

                if df is not None:
                    # Save metrics
                    save_path = metrics_handler.save_metrics(file_id, df)
                    if save_path:
                        logger.info(f"Saved metrics to: {save_path}")

                    # Calculate metrics
                    metrics_data = metrics_handler.calculate_metrics(df)
                    logger.info("Successfully calculated metrics")
                else:
                    logger.error("Failed to process metrics data")
        else:
            logger.warning(
                f"No result files found for fine-tuning job: {fine_tuning_id}"
            )

        # Handle pagination if metrics exist
        paginated_metrics = None
        if metrics_data and "step" in metrics_data and metrics_data["step"]:
            total_items = len(metrics_data["step"])
            total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)
            page = max(1, min(page, total_pages))  # Ensure page is within bounds

            start_idx = (page - 1) * items_per_page
            end_idx = min(start_idx + items_per_page, total_items)

            # Create paginated version of metrics
            paginated_metrics = {
                # Keep the summary statistics
                "avg_train_loss": metrics_data.get("avg_train_loss"),
                "avg_valid_loss": metrics_data.get("avg_valid_loss"),
                "max_train_accuracy": metrics_data.get("max_train_accuracy"),
                "max_valid_accuracy": metrics_data.get("max_valid_accuracy"),
                "data_points": metrics_data.get("data_points"),
                # Paginate the series data
                "step": (
                    metrics_data["step"][start_idx:end_idx]
                    if metrics_data.get("step")
                    else []
                ),
                "train_loss": (
                    metrics_data["train_loss"][start_idx:end_idx]
                    if metrics_data.get("train_loss")
                    else []
                ),
                "train_accuracy": (
                    metrics_data["train_accuracy"][start_idx:end_idx]
                    if metrics_data.get("train_accuracy")
                    else []
                ),
                "valid_loss": (
                    metrics_data["valid_loss"][start_idx:end_idx]
                    if metrics_data.get("valid_loss")
                    else []
                ),
                "valid_mean_token_accuracy": (
                    metrics_data["valid_mean_token_accuracy"][start_idx:end_idx]
                    if metrics_data.get("valid_mean_token_accuracy")
                    else []
                ),
            }
        else:
            paginated_metrics = {
                "avg_train_loss": None,
                "avg_valid_loss": None,
                "max_train_accuracy": None,
                "max_valid_accuracy": None,
                "data_points": 0,
                "step": [],
                "train_loss": [],
                "train_accuracy": [],
                "valid_loss": [],
                "valid_mean_token_accuracy": [],
            }

        # Log metrics data before rendering
        logger.info(
            f"Rendering template with metrics data available: {bool(paginated_metrics)}"
        )

        return render_template(
            "pages/train-model/fine-tuning/fine-tuning-steps-graph.html",
            fine_tuning_id=fine_tuning_id,
            metrics=paginated_metrics,
            generated_time=current_time,
            current_page=page,
            total_pages=total_pages,
            items_per_page=items_per_page,
        )

    except Exception as e:
        logger.error(f"Error in show_metrics: {str(e)}", exc_info=True)
        return f"Error loading metrics: {str(e)}"


@train_finetuning.route("/create-finetuning", methods=["GET"])
def create_finetuning():
    return render_template(
        "pages/training_finetuning/create-finetunings-jobs.html",
        base_models=BASE_MODELS,
    )


@train_finetuning.route("/create-finetuning/jobs", methods=["POST"])
def create_model():
    schema = FineTuningJobSchema()
    try:
        # Convert form data to dict and handle empty values
        form_data = {
            k: (None if v == "" else v) for k, v in request.form.to_dict().items()
        }

        # Type conversion for numeric fields
        for field, type_func in {
            "batch_size": int,
            "lr_multiplier": float,
            "epochs": int,
        }.items():
            if form_data.get(field):
                try:
                    form_data[field] = type_func(form_data[field])
                except ValueError:
                    flash(f"Invalid value for {field}", "error")
                    return redirect(url_for("train_finetuning.list_finetunings"))

        # Validate data
        validated_data = schema.load(form_data)

        try:
            # Upload training file
            training_file = client.files.create(
                file=open("dataset/finetuning.jsonl", "rb"), purpose="fine-tune"
            )

            # Prepare hyperparameters
            hyperparameters = {
                k: validated_data[v]
                for k, v in {
                    "batch_size": "batch_size",
                    "learning_rate_multiplier": "lr_multiplier",
                    "n_epochs": "epochs",
                }.items()
                if v in validated_data and validated_data[v] is not None
            }

            # Create fine-tuning job with correct parameter names
            job = client.fine_tuning.jobs.create(
                training_file=training_file.id,
                model=validated_data["model"],
                suffix=validated_data["suffix"],
                hyperparameters=hyperparameters,
            )

            flash(f"Fine-tuning job created successfully. Job ID: {job.id}", "success")
            return redirect(url_for("train_finetuning.list_finetunings"))

        except Exception as e:
            flash(f"OpenAI API error: {str(e)}", "error")
            return redirect(url_for("train_finetuning.list_finetunings"))

    except ValidationError as err:
        error_messages = []
        for field, messages in err.messages.items():
            if isinstance(messages, list):
                error_messages.append(f"{field}: {', '.join(messages)}")
            else:
                error_messages.append(f"{field}: {messages}")

        flash(f"Validation error: {'; '.join(error_messages)}", "error")
        return redirect(url_for("train_finetuning.list_finetunings"))


@train_finetuning.route("/model/<string:fine_tuning_id>", methods=["POST"])
def delete_finetuning(fine_tuning_id):
    try:
        # Delete fine-tuning job
        client.models.delete(fine_tuning_id)

        return jsonify(
            {
                "success": True,
                "message": f"Fine-tuning job deleted successfully. Job ID: {fine_tuning_id}",
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": f"OpenAI API error: {str(e)}"}), 400
