from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint
from extensions import db
from models.fine_tuning import Conversation
from flask_login import login_required
import json

fineTuning = Blueprint("fineTuning", __name__)


@fineTuning.route("/dashboard/dataset/fine-tuning/list")
@login_required
def view_conversations():
    conversations = Conversation.query.all()
    return render_template(
        "pages/dataset-fine-tuning.html", conversations=conversations
    )


@fineTuning.route("/dashboard/dataset/fine-tuning/add", methods=["GET", "POST"])
@login_required
def add_conversation():
    if request.method == "POST":
        messages = []

        for role in ["system", "user", "assistant"]:
            content = request.form.get(role)
            if content:
                messages.append({"role": role, "content": content})

        if len(messages) == 3:
            add_conversation(messages)
            export_to_jsonl()
            flash("Percakapan berhasil ditambahkan!", "success")
            return redirect(url_for("fineTuning.view_conversations"))
        else:
            flash("Semua peran harus diisi!", "danger")

    return render_template("pages/dataset-fine-tuning-create.html")


@fineTuning.route(
    "/dashboard/dataset/fine-tuning/<int:id>/update", methods=["GET", "POST"]
)
@login_required
def update_conversation(id):
    conversation = Conversation.query.get_or_404(id)

    if request.method == "POST":
        # Update messages with data from the form
        messages = []
        for role in ["system", "user", "assistant"]:
            content = request.form.get(role)
            if content:
                messages.append({"role": role, "content": content})

        if len(messages) == 3:
            conversation.messages = messages
            db.session.commit()
            export_to_jsonl()
            flash("Percakapan berhasil diperbarui!", "success")
            return redirect(url_for("fineTuning.view_conversations"))
        else:
            flash("Semua peran harus diisi!", "danger")

    return render_template(
        "pages/dataset-fine-tuning-update.html", conversation=conversation
    )


@fineTuning.route("/dashboard/dataset/fine-tuning/<int:id>/delete", methods=["POST"])
@login_required
def delete_conversation(id):
    conversation = Conversation.query.get_or_404(id)
    db.session.delete(conversation)
    db.session.commit()
    flash("Percakapan berhasil dihapus!", "success")
    export_to_jsonl()
    return redirect(url_for("fineTuning.view_conversations"))


def add_conversation(messages):
    conversation = Conversation(messages=messages)
    db.session.add(conversation)
    db.session.commit()


def export_to_jsonl():
    conversations = Conversation.query.all()
    with open("dataset/conversations.jsonl", "w") as jsonl_file:
        for conversation in conversations:
            jsonl_file.write(json.dumps({"messages": conversation.messages}) + "\n")
    flash("Data berhasil diekspor ke conversations.jsonl", "success")
