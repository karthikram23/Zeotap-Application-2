# Zeotap-Application-2

# Rule Engine and Weather Monitor Application

## Overview

This project consists of a web application built with Flask that allows users to manage and evaluate rules, as well as monitor weather conditions. The application includes functionality for creating, combining, and modifying rules, as well as generating and displaying weather summaries and alerts.

## Features

- User Authentication
- Rule Creation and Evaluation
- Rule Combination
- Weather Data Fetching and Display
- Weather Alerts Based on Custom Thresholds
- Temperature Trend Chart Generation

## Prerequisites

- Python 3.6+
- Flask
- Flask-Login
- SQLAlchemy
- Requests
- Matplotlib

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/username/repo-name.git
    cd your-repo-name
    ```

2. **Create a virtual environment and activate it:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required packages:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set environment variables for Flask and Weather API:**

    - Create a `.env` file in the root directory of the project.
    - Add the following lines to the `.env` file, replacing placeholders with your actual values:

      ```env
      SECRET_KEY=your_secret_key
      WEATHER_API_KEY=your_weather_api_key
      ```

5. **Initialize the database:**

    ```bash
    flask db upgrade
    ```

## Usage

1. **Run the application:**

    ```bash
    flask run
    ```

2. **Navigate to `http://127.0.0.1:5000/` in your web browser to access the application.**

## Endpoints

- **`/`**: Home page (requires login)
- **`/login`**: Login page
- **`/logout`**: Logout
- **`/create_rule`**: Create a new rule (POST request)
- **`/combine_rules`**: Combine existing rules (POST request)
- **`/evaluate_rule`**: Evaluate a rule (POST request)
- **`/modify_rule`**: Modify an existing rule (POST request)
- **`/weather_alerts`**: View weather alerts (requires login)
- **`/weather_summary/<city>`**: View weather summary and temperature chart for a city

## Configuration

- **Flask Configuration**: Update the `SECRET_KEY` and `SQLALCHEMY_DATABASE_URI` in `app.py` as needed.
- **Weather API Configuration**: Add your API key to the `.env` file.

## Testing

For unit testing, ensure you have `pytest` installed and run:

```bash
pytest
