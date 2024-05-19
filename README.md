# Home Assistant Entity Renamer

## Overview

The Home Assistant Entity Renamer is a Django-based web application designed to manage and rename entities in Home Assistant. This tool provides a user-friendly interface to list, filter, and rename entities using CSV files or regular expressions, enhancing the organization and management of Home Assistant configurations.

## User Interface Preview

![regex_example_1](https://github.com/Coenenp/homeassistant_renamer/assets/17593262/78ce91b8-594e-4579-9dd3-45fbca163439)
Using regex to find entities.

![regex_example_2](https://github.com/Coenenp/homeassistant_renamer/assets/17593262/00b0ccb4-9c50-45a9-82fd-348ab8b38052)
Rename entities using regex.

![csv_example_1](https://github.com/Coenenp/homeassistant_renamer/assets/17593262/3e7a9ed3-e9cc-489c-bc59-feae3fc44077)
Upload a .csv file to rename entities.

## Key Concepts

- **Entities**: Represent Home Assistant devices or objects that users can rename.
- **Renaming**: The core functionality allowing users to update entity IDs and friendly names.

## User Workflow

1. **Access**: Navigate to the home page with a login option to access the main functionalities.
2. **Authentication**: Sign up for an account or log in to access the Home Assistant Entity Renamer dashboard. Needed to store your homeassistant details.
3. **Dashboard**: Main interface displaying options to upload CSV files or use regular expressions for renaming entities.
4. **Functionalities**:

    - **Upload CSV File**: Submit a CSV file containing entity IDs and new names for bulk renaming.
    - **Use Regex**: Define search and replace patterns to rename entities matching a specific regex pattern.
    - **List Entities**: Display a list of entities, filtered by a regex pattern, with options to rename.
    - **Rename Confirmation**: Confirm and apply renaming changes to the listed entities.

## Setup Instructions

To deploy and run the project locally, follow these steps:

1. **Clone this repository**:
    ```bash
    git clone https://github.com/yourusername/home-assistant-entity-renamer.git
    cd home-assistant-entity-renamer
    ```

2. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Set up the Django environment**:
    - Create a `.env` file to store environment variables such as `SECRET_KEY`, `DATABASE_URL`, etc.
    - Run database migrations:
      ```bash
      python manage.py migrate
      ```

4. **Run the development server**:
    ```bash
    python manage.py runserver
    ```

5. **Access the application**:
    - Open a web browser and navigate to `http://localhost:8000`.

## Additional Packages

Below are the additional packages installed for this Django project:

- **requests**: For making HTTP requests to the Home Assistant API.
- **websocket-client**: For interacting with the Home Assistant WebSocket API.
- **python-decouple**: Simplifies handling of settings by separating configuration from code.
- **django-crispy-forms**: Assists in managing Django forms elegantly.
- **crispy-bootstrap5**: Extends crispy_forms to utilize Bootstrap 5 styles for forms.

## Configuration

### Environment Variables

Ensure the following environment variables are set in your `.env` file:

- `SECRET_KEY`: A secret key for Django.
- `DATABASE_URL`: Database connection URL.
- `HOME_ASSISTANT_URL`: URL of your Home Assistant instance.
- `ACCESS_TOKEN`: Access token for Home Assistant API.

### Django Models

The application uses the following Django model to store configurations:

- **AppConfig**: Stores user-specific configuration such as Home Assistant host, TLS settings, and access tokens.

## Public Domain Dedication

All code and subsequent modifications in this project have been created by Pieter Coenen and are hereby released into the public domain. To the extent possible under law, I waive all copyright and related or neighboring rights to this work worldwide.

## Contributors

- Pieter Coenen - Project Lead & Developer

## Acknowledgments

- @Saladpanda for starting the initial command line 'Home Assistant Entity Renamer project. This project essentially adds a User Interface to it.

Feel free to contribute, report issues, or suggest enhancements!
