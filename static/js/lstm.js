const optimizerConfigs = {
    adam: {
        beta_1: { default: 0.9, min: 0, max: 1, step: 0.1 },
        beta_2: { default: 0.999, min: 0, max: 1, step: 0.001 },
        epsilon: { default: 1e-7, min: 1e-10, max: 1e-5, step: 1e-8 },
        amsgrad: { default: false, type: "boolean" },
    },
    sgd: {
        momentum: { default: 0.0, min: 0, max: 1, step: 0.1 },
        nesterov: { default: false, type: "boolean" },
    },
    rmsprop: {
        rho: { default: 0.9, min: 0, max: 1, step: 0.1 },
        momentum: { default: 0.0, min: 0, max: 1, step: 0.1 },
        epsilon: { default: 1e-7, min: 1e-10, max: 1e-5, step: 1e-8 },
        centered: { default: false, type: "boolean" },
    },
    adagrad: {
        initial_accumulator_value: { default: 0.1, min: 0, max: 1, step: 0.1 },
        epsilon: { default: 1e-7, min: 1e-10, max: 1e-5, step: 1e-8 },
    },
    adadelta: {
        rho: { default: 0.95, min: 0, max: 1, step: 0.01 },
        epsilon: { default: 1e-7, min: 1e-10, max: 1e-5, step: 1e-8 },
    },
    adamax: {
        beta_1: { default: 0.9, min: 0, max: 1, step: 0.1 },
        beta_2: { default: 0.999, min: 0, max: 1, step: 0.001 },
        epsilon: { default: 1e-7, min: 1e-10, max: 1e-5, step: 1e-8 },
    },
    nadam: {
        beta_1: { default: 0.9, min: 0, max: 1, step: 0.1 },
        beta_2: { default: 0.999, min: 0, max: 1, step: 0.001 },
        epsilon: { default: 1e-7, min: 1e-10, max: 1e-5, step: 1e-8 },
    },
};

function updateOptimizerParams() {
    const optimizer = document.querySelector('[name="optimizer_name"]').value;
    const container = document.getElementById("optimizer-params");
    container.innerHTML = "";

    const params = optimizerConfigs[optimizer];
    Object.entries(params).forEach(([param, config]) => {
        const col = document.createElement("div");
        col.className = "col-md-6 mb-3";

        const label = document.createElement("label");
        label.className = "form-label";
        label.textContent = param.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());

        let input;
        if (config.type === "boolean") {
            input = document.createElement("select");
            input.className = "form-select";
            input.innerHTML = `
                <option value="true">True</option>
                <option value="false" ${!config.default ? "selected" : ""}>False</option>
            `;
        } else {
            input = document.createElement("input");
            input.type = "number";
            input.className = "form-control";
            input.step = config.step;
            input.min = config.min;
            input.max = config.max;
            input.value = config.default;
        }
        input.name = param;

        col.appendChild(label);
        col.appendChild(input);
        container.appendChild(col);
    });
}

function addLayer() {
    const container = document.getElementById("layers-container");
    container.appendChild(createLayerConfig("LSTM"));
}

// Hapus fungsi getLayerConfigs yang lama
// function getLayerConfigs() { ... }

// Fungsi helper untuk layer configuration tetap dipertahankan
function createLayerConfig(type) {
    const config = document.createElement("div");
    config.className = "layer-config border rounded p-3 mb-3";

    let innerHTML = `
        <div class="row mb-3">
            <div class="col-md-6">
                <label class="form-label">Layer Type</label>
                <select class="form-select" name="layer_type" onchange="updateLayerParams(this)">
                    <option value="LSTM" ${type === "LSTM" ? "selected" : ""}>LSTM</option>
                    <option value="Dense" ${type === "Dense" ? "selected" : ""}>Dense</option>
                    <option value="Dropout" ${type === "Dropout" ? "selected" : ""}>Dropout</option>
                </select>
            </div>
        </div>
    `;

    config.innerHTML = innerHTML;
    updateLayerParams(config.querySelector("select"), type);

    const removeBtn = document.createElement("button");
    removeBtn.className = "btn btn-sm btn-danger position-absolute top-0 end-0 m-2";
    removeBtn.innerHTML = '<i class="bi bi-trash"></i>';
    removeBtn.onclick = function () {
        config.remove();
    };

    config.style.position = "relative";
    config.appendChild(removeBtn);
    return config;
}

function updateLayerParams(select, type = null) {
    const layerType = type || select.value;
    const container = select.closest(".layer-config");
    const paramsDiv = container.querySelector(".layer-params");

    if (paramsDiv) {
        paramsDiv.remove();
    }

    const newParamsDiv = document.createElement("div");
    newParamsDiv.className = "layer-params row";

    let paramsHTML = "";
    switch (layerType) {
        case "LSTM":
            paramsHTML = `
                <div class="col-md-6 mb-3">
                    <label class="form-label">Units</label>
                    <input type="number" class="form-control" name="units" min="1" max="512" value="128" required />
                </div>
                <div class="col-md-6 mb-3">
                    <label class="form-label">Dropout</label>
                    <input type="number" class="form-control" name="dropout" min="0" max="1" step="0.1" value="0.2" />
                </div>
                <div class="col-md-6 mb-3">
                    <label class="form-label">Recurrent Dropout</label>
                    <input type="number" class="form-control" name="recurrent_dropout" min="0" max="1" step="0.1" value="0.2" />
                </div>
                <div class="col-md-6 mb-3">
                    <label class="form-label">Return Sequences</label>
                    <select class="form-select" name="return_sequences">
                        <option value="true">True</option>
                        <option value="false">False</option>
                    </select>
                </div>
            `;
            break;
        case "Dense":
            paramsHTML = `
                <div class="col-md-6 mb-3">
                    <label class="form-label">Units</label>
                    <input type="number" class="form-control" name="units" min="1" max="512" value="64" required />
                </div>
                <div class="col-md-6 mb-3">
                    <label class="form-label">Activation</label>
                    <select class="form-select" name="activation">
                        <option value="relu">ReLU</option>
                        <option value="tanh">Tanh</option>
                        <option value="sigmoid">Sigmoid</option>
                        <option value="linear">Linear</option>
                    </select>
                </div>
            `;
            break;
        case "Dropout":
            paramsHTML = `
                <div class="col-md-6 mb-3">
                    <label class="form-label">Rate</label>
                    <input type="number" class="form-control" name="rate" min="0" max="1" step="0.1" value="0.2" required />
                </div>
            `;
            break;
    }

    newParamsDiv.innerHTML = paramsHTML;
    container.appendChild(newParamsDiv);
}

// Fungsi baru untuk mendapatkan semua konfigurasi
function getFormConfigurations() {
    const formData = {};

    // Get basic configurations
    formData.model_name = document.querySelector('[name="model_name"]').value;
    formData.batch_size = parseInt(document.querySelector('[name="batch_size"]').value);
    formData.epochs = parseInt(document.querySelector('[name="epochs"]').value);
    formData.output_activation = document.querySelector('[name="output_activation"]').value;

    // Get embedding configurations
    formData.embedding_dim = parseInt(document.querySelector('[name="embedding_dim"]').value);
    formData.embedding_dropout = parseFloat(document.querySelector('[name="embedding_dropout"]').value);
    formData.mask_zero = document.querySelector('[name="mask_zero"]').value === "true";

    // Get layer configurations
    formData.layers = [];
    document.querySelectorAll(".layer-config").forEach((layerDiv) => {
        const type = layerDiv.querySelector('[name="layer_type"]').value;
        const layerConfig = {
            type: type,
            params: {},
        };

        // Get parameters based on layer type
        switch (type) {
            case "LSTM":
                layerConfig.params = {
                    units: parseInt(layerDiv.querySelector('[name="units"]').value),
                    dropout: parseFloat(layerDiv.querySelector('[name="dropout"]').value),
                    recurrent_dropout: parseFloat(layerDiv.querySelector('[name="recurrent_dropout"]').value),
                    return_sequences: layerDiv.querySelector('[name="return_sequences"]').value === "true",
                };
                break;
            case "Dense":
                layerConfig.params = {
                    units: parseInt(layerDiv.querySelector('[name="units"]').value),
                    activation: layerDiv.querySelector('[name="activation"]').value,
                };
                break;
            case "Dropout":
                layerConfig.params = {
                    rate: parseFloat(layerDiv.querySelector('[name="rate"]').value),
                };
                break;
        }
        formData.layers.push(layerConfig);
    });

    // Get optimizer configurations
    const optimizerName = document.querySelector('[name="optimizer_name"]').value;
    formData.optimizer_name = optimizerName;
    formData.learning_rate = parseFloat(document.querySelector('[name="learning_rate"]').value);

    // Get optimizer specific parameters
    const optimizerParamsDiv = document.getElementById("optimizer-params");
    if (optimizerParamsDiv) {
        optimizerParamsDiv.querySelectorAll("input, select").forEach((input) => {
            if (input.type === "number") {
                formData[input.name] = parseFloat(input.value);
            } else if (input.type === "select-one") {
                formData[input.name] = input.value === "true";
            }
        });
    }

    return formData;
}

function updateTrainingProgress(progress, epochData = null) {
    // Update progress bar
    const progressContainer = document.getElementById("training-progress");
    const progressBar = document.getElementById("training-progress-bar");
    const statusText = document.getElementById("training-status");

    if (progressContainer) {
        progressContainer.style.display = "block";
    }

    if (progress !== null) {
        const percentage = Math.round(progress);

        if (progressBar) {
            progressBar.style.width = `${percentage}%`;
            progressBar.setAttribute("aria-valuenow", percentage);
            progressBar.textContent = `${percentage}%`;
        }

        if (statusText) {
            statusText.textContent = `Training Progress: ${percentage}%`;
        }

        // Pindahkan pengecekan progress 100 ke dalam blok if
        if (percentage === 100) {
            setTimeout(() => {
                window.location.reload();
            }, 5000);
        }
    }

    // Update epoch metrics if provided
    if (epochData) {
        const metricsContainer = document.getElementById("training-metrics");
        if (!metricsContainer) {
            // Create metrics container if it doesn't exist
            const container = document.createElement("div");
            container.id = "training-metrics";
            container.className = "mt-3";
            container.innerHTML = `
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Training Metrics</h5>
                        <div class="row">
                            <div class="col-md-4">
                                <p>Epoch: <span id="current-epoch">-</span></p>
                            </div>
                            <div class="col-md-4">
                                <p>Accuracy: <span id="current-accuracy">-</span></p>
                            </div>
                            <div class="col-md-4">
                                <p>Loss: <span id="current-loss">-</span></p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            progressContainer.parentNode.insertBefore(container, progressContainer.nextSibling);
        }

        document.getElementById("current-epoch").textContent = epochData.epoch;
        document.getElementById("current-accuracy").textContent = (epochData.accuracy * 100).toFixed(2) + "%";
        document.getElementById("current-loss").textContent = epochData.loss.toFixed(4);
    }
}

async function trainModel() {
    try {
        const modalElement = document.getElementById("createTrainingModal");
        const modal = bootstrap.Modal.getInstance(modalElement);

        const config = getFormConfigurations();
        const errors = validateConfigurations(config);

        if (errors.length > 0) {
            showValidationErrors(errors);
            return;
        }

        // Show loading state
        const trainButton = document.querySelector('button[onclick="trainModel()"]');
        trainButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Training...';
        trainButton.disabled = true;

        if (modal) {
            modal.hide();
        }

        // Reset and show progress
        updateTrainingProgress(0);

        const response = await fetch("/train", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(config),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || "Training failed");
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            const text = decoder.decode(value);
            const lines = text.split("\n").filter((line) => line.trim());

            lines.forEach((line) => {
                try {
                    // Check if line contains progress data
                    if (line.includes("progress")) {
                        const jsonStart = line.indexOf("data:");
                        if (jsonStart >= 0) {
                            const jsonStr = line.substring(jsonStart + 5);
                            const data = JSON.parse(jsonStr);

                            if (data.progress !== undefined) {
                                updateTrainingProgress(data.progress);
                            }
                        }
                    }
                    // Check if line contains epoch data
                    else if (line.includes("epoch_data")) {
                        const epochData = JSON.parse(line.match(/\{.*\}/)[0]);
                        updateTrainingProgress(null, epochData);
                    }
                } catch (e) {
                    console.error("Error parsing line:", line);
                    console.error(e);
                }
            });
        }

        showSuccessMessage("Model training completed successfully!");
    } catch (error) {
        showErrorMessage(error.message);
    } finally {
        // Reset button state
        const trainButton = document.querySelector('button[onclick="trainModel()"]');
        trainButton.innerHTML = '<i class="bi bi-play-circle"></i> Train Model';
        trainButton.disabled = false;
    }
}
// Show error message in a toast or alert
function showErrorMessage(message) {
    const alertContainer = document.getElementById("alert-container");
    if (!alertContainer) {
        // Create alert container if it doesn't exist
        const container = document.createElement("div");
        container.id = "alert-container";
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            max-width: 400px;
        `;
        document.body.appendChild(container);
    }

    const alert = document.createElement("div");
    alert.className = "alert alert-danger alert-dismissible fade show";
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    document.getElementById("alert-container").appendChild(alert);

    // Remove alert after 5 seconds
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

// Show success message in a toast or alert
function showSuccessMessage(message) {
    const alertContainer = document.getElementById("alert-container");
    if (!alertContainer) {
        const container = document.createElement("div");
        container.id = "alert-container";
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            max-width: 400px;
        `;
        document.body.appendChild(container);
    }

    const alert = document.createElement("div");
    alert.className = "alert alert-success alert-dismissible fade show";
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    document.getElementById("alert-container").appendChild(alert);

    // Remove alert after 5 seconds
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

// Show validation errors
function showValidationErrors(errors) {
    const errorsList = errors.map((error) => `<li>${error}</li>`).join("");
    const message = `
        <strong>Please fix the following errors:</strong>
        <ul>${errorsList}</ul>
    `;
    showErrorMessage(message);
}

// Validate configuration object
function validateConfigurations(config) {
    const errors = [];

    // Basic validation
    if (!config.model_name?.trim()) {
        errors.push("Model name is required");
    }

    if (!config.batch_size || config.batch_size < 1 || config.batch_size > 512) {
        errors.push("Batch size must be between 1 and 512");
    }

    if (!config.epochs || config.epochs < 1 || config.epochs > 1000) {
        errors.push("Number of epochs must be between 1 and 1000");
    }

    // Embedding validation
    if (!config.embedding_dim || config.embedding_dim < 1 || config.embedding_dim > 1024) {
        errors.push("Embedding dimension must be between 1 and 1024");
    }

    if (config.embedding_dropout < 0 || config.embedding_dropout > 1) {
        errors.push("Embedding dropout must be between 0 and 1");
    }

    // Layers validation
    if (!config.layers?.length) {
        errors.push("At least one layer is required");
    }

    // Validate each layer
    config.layers?.forEach((layer, index) => {
        switch (layer.type) {
            case "LSTM":
                if (!layer.params.units || layer.params.units < 1) {
                    errors.push(`LSTM layer ${index + 1}: Units must be greater than 0`);
                }
                if (layer.params.dropout < 0 || layer.params.dropout > 1) {
                    errors.push(`LSTM layer ${index + 1}: Dropout must be between 0 and 1`);
                }
                if (layer.params.recurrent_dropout < 0 || layer.params.recurrent_dropout > 1) {
                    errors.push(`LSTM layer ${index + 1}: Recurrent dropout must be between 0 and 1`);
                }
                break;
            case "Dense":
                if (!layer.params.units || layer.params.units < 1) {
                    errors.push(`Dense layer ${index + 1}: Units must be greater than 0`);
                }
                if (!["relu", "tanh", "sigmoid", "linear"].includes(layer.params.activation)) {
                    errors.push(`Dense layer ${index + 1}: Invalid activation function`);
                }
                break;
            case "Dropout":
                if (layer.params.rate < 0 || layer.params.rate > 1) {
                    errors.push(`Dropout layer ${index + 1}: Rate must be between 0 and 1`);
                }
                break;
            default:
                errors.push(`Invalid layer type: ${layer.type}`);
        }
    });

    // Learning rate validation
    if (!config.learning_rate || config.learning_rate <= 0 || config.learning_rate > 1) {
        errors.push("Learning rate must be between 0 and 1");
    }

    return errors;
}
