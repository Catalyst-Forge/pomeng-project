from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint
from extensions import db
from models.fine_tuning import Finetuning
from flask_login import login_required
import json

fineTuning = Blueprint("fineTuning", __name__)


@fineTuning.route("/dashboard/dataset/fine-tuning/list")
@login_required
def view_finetuning_data():
    finetuning = Finetuning.query.all()
    return render_template(
        "pages/dataset-fine-tuning.html", finetuning=finetuning
    )


@fineTuning.route("/dashboard/dataset/fine-tuning/add", methods=["GET", "POST"])
@login_required
def add_finetuning_data():
    if request.method == "POST":
        messages = []

        for role in ["system", "user", "assistant"]:
            content = request.form.get(role)
            if content:
                messages.append({"role": role, "content": content})

        if len(messages) == 3:
            add_finetuning_data(messages)
            export_to_jsonl()
            flash("Percakapan berhasil ditambahkan!", "success")
            return redirect(url_for("fineTuning.view_finetuning_data"))
        else:
            flash("Semua peran harus diisi!", "danger")

    return render_template("pages/dataset-fine-tuning-create.html")


@fineTuning.route(
    "/dashboard/dataset/fine-tuning/<int:id>/update", methods=["GET", "POST"]
)
@login_required
def update_finetuning_data(id):
    fineTuning = Finetuning.query.get_or_404(id)

    if request.method == "POST":
        # Update messages with data from the form
        messages = []
        for role in ["system", "user", "assistant"]:
            content = request.form.get(role)
            if content:
                messages.append({"role": role, "content": content})

        if len(messages) == 3:
            fineTuning.messages = messages
            db.session.commit()
            export_to_jsonl()
            flash("Percakapan berhasil diperbarui!", "success")
            return redirect(url_for("fineTuning.view_finetuning_data"))
        else:
            flash("Semua peran harus diisi!", "danger")

    return render_template(
        "pages/dataset-fine-tuning-update.html", finetuning=fineTuning
    )


@fineTuning.route("/dashboard/dataset/fine-tuning/<int:id>/delete", methods=["POST"])
@login_required
def delete_finetuning_data(id):
    fineTuning = Finetuning.query.get_or_404(id)
    db.session.delete(fineTuning)
    db.session.commit()
    flash("Percakapan berhasil dihapus!", "success")
    export_to_jsonl()
    return redirect(url_for("fineTuning.view_finetuning_data"))


def add_finetuning_data(messages):
    fineTuning = Finetuning(messages=messages)
    db.session.add(fineTuning)
    db.session.commit()


def export_to_jsonl():
    fineTunings = Finetuning.query.all()
    with open("dataset/finetuning.jsonl", "w") as jsonl_file:
        for fineTuning in fineTunings:
            jsonl_file.write(json.dumps({"messages": fineTuning.messages}) + "\n")
    flash("Data berhasil diekspor ke jsonl", "success")
