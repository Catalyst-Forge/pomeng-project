import { createTrainingChart } from "../utils/createTrainingChart.js";

export const displayTrainingHistory = (data) => {
  // Create modal HTML
  const modalHtml =
    /* html */
    `<div class="modal fade" id="training-modal" tabindex="-1" aria-labelledby="training-model" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered modal-xl">
      
      <!-- Modal Body -->
      <div class="modal-content">
        <!-- Header -->
        <div class="modal-header">
          <h2 class="modal-title">Model Training Details</h2>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>

        <!-- Content Sections -->
        <div class="modal-body">
          <div class="row">
            <!-- Model Configuration -->
            <div class="card col-4">
              <div class="card-body">
                <h3 class="card-title mb-4">Model Configuration</h3>

                <div>
                  <p><strong>Batch Size:</strong> ${data.model_config.batch_size}</p>
                  <p><strong>Embedding Dimension:</strong> ${data.model_config.embedding_dim}</p>
                  <p><strong>Learning Rate:</strong> ${data.model_config.learning_rate}</p>
                  <p><strong>Epochs:</strong> ${data.model_config.epochs}</p>
                </div>

                <div>
                  <p><strong>Vocabulary Size:</strong> ${data.model_config.vocab_size}</p>
                  <p><strong>Output Length:</strong> ${data.model_config.output_length}</p>
                  <p><strong>Training Date:</strong> ${new Date(data.training_date).toLocaleString()}</p>
                </div>
              </div>
            </div>

            <!-- Layer Configuration -->
            <div class="card col-4">
              <div class="card-body">
                <h3 class="card-title">Layer Configuration:</h3>
                <div>
                  ${data.model_config.layers
                    .map(
                      (layer, index) => `
                      <div>
                        <p>Layer ${index + 1}: ${layer.type} (${layer.type === "Dropout" ? "Rate" : "Neurons"}: ${layer.neurons})</p>
                      </div>`
                    )
                    .join("")}
                </div>
              </div>
            </div>

            <!-- Training Summary -->
            <div class="card col-4">
              <div class="card-body">
                <h4 class="card-title">Training Summary</h4>

                <div>
                  <p><strong>Final Accuracy:</strong> ${(data.training_history.final_accuracy * 100).toFixed(2)}%</p>
                  <p><strong>Best Accuracy:</strong> ${(data.training_history.best_accuracy * 100).toFixed(2)}%</p>
                  <p><strong>Best Epoch:</strong> ${data.training_history.best_epoch}</p>
                  <p><strong>Final Loss:</strong> ${data.training_history.final_loss.toFixed(4)}</p>
                </div>

                <div>
                  <p><strong>Total Duration:</strong> ${data.training_history.total_duration}</p>
                  <p><strong>Steps per Epoch:</strong> ${data.training_history.steps_per_epoch}</p>
                  <p><strong>Total Steps:</strong> ${data.training_history.total_steps}</p>
                  <p><strong>Start Time:</strong> ${new Date(data.training_history.start_time).toLocaleString()}</p>
                </div>
              </div>
            </div>

            <!-- Epoch Details Table -->
            <div>
              <h3>Epoch Details</h3>

              <div class="epoch-table-container">
                <table class="table table-info">
                  <thead>
                    <tr class="text-center">
                      <th scope="col">Epoch</th>
                      <th scope="col">Accuracy</th>
                      <th scope="col">Loss</th>
                      <th scope="col">Duration</th>
                      <th scope="col">Steps</th>
                    </tr>
                  </thead>
                  
                  <tbody>
                    ${data.training_history.epochs
                      .map(
                        (epoch, index) => `
                          <tr class="text-center ${index >= 20 ? "scrollable-row" : ""}">
                            <td>${epoch.epoch_number}</td>
                            <td>${(epoch.metrics.accuracy * 100).toFixed(2)}%</td>
                            <td>${epoch.metrics.loss.toFixed(4)}</td>
                            <td>${epoch.duration}</td>
                            <td>${epoch.steps.length}</td>
                          </tr>`
                      )
                      .join("")}
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Training Progress Chart -->
            <div>
              <h3>Training Progress</h3>
              <div>
                <div style="position: relative; height: 400px; width: 100%;">
                  <canvas id="training-chart"></canvas>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" aria-label="Close">
              Close
          </button>
        </div>
      </div>
    </div>
  </div>`;

  document.body.insertAdjacentHTML("beforeend", modalHtml);

  const modalElement = document.getElementById("training-modal");
  const bootstrapModal = new bootstrap.Modal(modalElement, { backdrop: true });
  bootstrapModal.show();

  setTimeout(() => createTrainingChart(data), 100);
};
