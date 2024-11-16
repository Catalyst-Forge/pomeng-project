export const createTrainingChart = (data) => {
  const ctx = document.getElementById("training-chart");

  if (!ctx) {
    console.error("Cannot find canvas element");
    return;
  }

  // Prepare the data
  const chartData = data.training_history.epochs.map((epoch) => ({
    epoch: epoch.epoch_number,
    accuracy: epoch.metrics.accuracy * 100,
    loss: epoch.metrics.loss,
  }));

  // Create the chart
  try {
    const chart = new Chart(ctx, {
      type: "line",
      data: {
        labels: chartData.map((d) => `Epoch ${d.epoch}`),
        datasets: [
          {
            label: "Accuracy (%)",
            data: chartData.map((d) => d.accuracy),
            borderColor: "rgb(75, 192, 192)",
            backgroundColor: "rgba(75, 192, 192, 0.2)",
            yAxisID: "y",
            tension: 0.1,
          },
          {
            label: "Loss",
            data: chartData.map((d) => d.loss),
            borderColor: "rgb(255, 99, 132)",
            backgroundColor: "rgba(255, 99, 132, 0.2)",
            yAxisID: "y1",
            tension: 0.1,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: "index",
          intersect: false,
        },
        stacked: false,
        plugins: {
          title: {
            display: true,
            text: "Training Progress",
          },
        },
        scales: {
          y: {
            type: "linear",
            display: true,
            position: "left",
            title: {
              display: true,
              text: "Accuracy (%)",
            },
            min: 0,
            max: 100,
          },
          y1: {
            type: "linear",
            display: true,
            position: "right",
            title: {
              display: true,
              text: "Loss",
            },
            grid: {
              drawOnChartArea: false,
            },
          },
        },
      },
    });
  } catch (error) {
    console.error("Error creating chart:", error);
  }
};
