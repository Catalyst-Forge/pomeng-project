# Lili Chatbot

Welcome to the Lili Chatbot project! This project demonstrates a simple chatbot interface using Flask for the backend, along with HTML, CSS, and JavaScript for the frontend.

## Table of Contents

-   [Lili Chatbot](#Lili-chatbot)
    -   [Table of Contents](#table-of-contents)
    -   [Project Overview](#project-overview)
    -   [Features](#features)
    -   [Installation](#installation)
    -   [Usage](#usage)
    -   [File Structure](#file-structure)
    -   [Contributing](#contributing)
    -   [License](#license)

## Project Overview

The Lili Chatbot project provides a basic chatbot interface where users can interact with a bot. The frontend is designed with modern CSS and JavaScript to create a smooth and engaging user experience.

## Features

-   Responsive design
-   Interactive chatbot interface
-   Easy to set up and run locally

## Installation

To get started with the Lili Chatbot project, follow these steps:

1. **Clone the repository**:

    ```sh
    git clone https://github.com/BagasAuliaAlfasyam/Lili-project-master.git
    cd Lili-project-master
    ```

2. **Create a virtual environment**:

    ```sh
    # in linux
    python3 -m venv venv

    # in windows
    python -m venv venv

    source venv/bin/activate
    # On Windows use `venv\Scripts\activate`
    ```

3. **Install the dependencies**:

    ```sh
    pip install -r requirements.txt
    ```

## Usage

To run the Flask application, use the following command:

```sh
python app.py
```

Open your browser and navigate to `http://127.0.0.1:5000/` to see the chatbot interface.

## File Structure

Here's a brief overview of the project structure:

```
Lili-project-master/
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── script.js
│   └── images/
│       └── bro.gif
├── templates/
│   └── index.html
├── app.py
├── requirements.txt
└── README.md
```

-   `static/`: Contains static files such as CSS, JavaScript, and images.
-   `templates/`: Contains HTML templates.
-   `app.py`: The main Flask application file.
-   `requirements.txt`: Lists the project dependencies.
-   `README.md`: Project documentation.

## Contributing

We welcome contributions! Please read our [Contributing Guidelines](CONTRIBUTING.md) for more details.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

---
