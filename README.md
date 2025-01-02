# 🛠️ Django CLI Application with Ollama Integration

This project implements a Django CLI tool designed to rewrite property information, generate summaries, and provide ratings and reviews using the Ollama model. It also integrates Docker for environment setup and PostgreSQL as the database.

---

## 📖 Features

1. **Rewriting Property Information**:
   - Uses Ollama LLM models to rewrite property titles and descriptions.

2. **Summary Generation**:
   - Creates a summary based on all property-related data and stores it in the database.

3. **Ratings and Reviews**:
   - Generates ratings and reviews for properties using an LLM model.

4. **Database Integration**:
   - Uses PostgreSQL for storing property details, summaries, ratings, and reviews.

5. **Code Coverage**:
   - Ensures at least 90% test coverage for the entire project.

6. **Docker Support**:
   - Includes a Dockerized setup for easy deployment.

---

## 📂 Project Structure

```plaintext
.
├── src/
│   ├── manage.py        # Django CLI entry point
│   ├── app/             # Contains models, views, and other Django app components
│   └── commands/        # Custom CLI commands
├── Dockerfile           # Docker image configuration
├── docker-compose.yml   # Docker multi-container setup
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation

## Here is the raw .md code for the README file tailored to your assignment:

# 🛠️ Django CLI Application with Ollama Integration

This project implements a Django CLI tool designed to rewrite property information, generate summaries, and provide ratings and reviews using the Ollama model. It also integrates Docker for environment setup and PostgreSQL as the database.

---

## 📖 Features

1. **Rewriting Property Information**:
   - Uses Ollama LLM models to rewrite property titles and descriptions.

2. **Summary Generation**:
   - Creates a summary based on all property-related data and stores it in the database.

3. **Ratings and Reviews**:
   - Generates ratings and reviews for properties using an LLM model.

4. **Database Integration**:
   - Uses PostgreSQL for storing property details, summaries, ratings, and reviews.

5. **Code Coverage**:
   - Ensures at least 90% test coverage for the entire project.

6. **Docker Support**:
   - Includes a Dockerized setup for easy deployment.

---

## 📂 Project Structure

```plaintext
.
├── src/
│   ├── manage.py        # Django CLI entry point
│   ├── app/             # Contains models, views, and other Django app components
│   └── commands/        # Custom CLI commands
├── Dockerfile           # Docker image configuration
├── docker-compose.yml   # Docker multi-container setup
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```
## 🚀 Getting Started
Prerequisites

- Python 3.10 or higher
- Docker
## 🔧 Setup Instructions
1. **Run the Scrapy Project**

    Go to https://github.com/Marjia029/Scrappy_test_trip link and setup the scrapy project accordingly and run it first.
2. **Clone the repository**
   ```bash
   git clone https://github.com/Marjia029/ollama-llm.git
   cd ollama-llm
3. **Create a new virtual environment**
    ```bash
    python -m venv venv #or
    python3 -m venv venv #if you have python3 installed
    ```
4. **Activate the virtual environment**
    ```bash
    \venv\Scripts\activate # for windows
    source venv/bin/activate # for linux
    ```
5. **Go to project Directory**
    ```bash
    cd ollamaproject
    ```
5. **Build Docker containers**

    Ensure you have Docker installed. If you are in windows, make sure your docker desktop is open. Then, run the following commands to build the containers:
    ```bash
    docker-compose build
    ```
6. **Start the containers**

    ```bash
    docker-compose up
    ```
    This will start the Django project and the PostgreSQL database.

7. **Make Make the Necessary Migrations**

    Navigate to Django bash and run commands for the migrations

    ```bash
    docker-compose exec django bash
    python manage.py makemigrations #or
    python manage.py makemigrations property
    python manage.py migrate
    ```
8. **Generate Data for the Database**

    In the Django bash run the following commands to create super user

    ```bash
    python manage.py generate_title_and_description
    python manage.py generate_summary
    python manage.py generate_rating_and_review
    ```
9. **Create Super User to see the Database Using Django Admin**

    Navigate to Django bash and run commands for the migrations

    ```bash
    python manage.py createsuperuser
    ```
    Provide necessary information to successfully create super user. Now browse to http://localhost:8000/admin and login with your admin information to see the database.
    