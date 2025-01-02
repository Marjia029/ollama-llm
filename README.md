# 🛠️ Django CLI Application with Ollama Integration

This project implements a Django CLI tool designed to rewrite property information, generate summaries, and provide ratings and reviews using the Google Generative AI LLM model Gemini. It also integrates Docker for environment setup and PostgreSQL as the database.

---

## 📖 Features

1. **Rewriting Property Information**:
   - Uses Ollama Gemini LLM model to rewrite property titles and descriptions.

2. **Summary Generation**:
   - Creates a summary based on all property-related data and stores it in the database.

3. **Ratings and Reviews**:
   - Generates ratings and reviews for properties using an LLM model.

4. **Database Integration**:
   - Uses PostgreSQL for storing property details, summaries, ratings, and reviews.

5. **Docker Support**:
   - Includes a Dockerized setup for easy deployment.

---

## 📂 Project Structure

```plaintext
ollama-llm/
├── ollamaproject/           # Main Django project directory
│   ├── ollamaproject/       # Django project-specific settings
│   ├── property/            # Django app for property
│   └── manage.py            # Django CLI entry point
│   ├── Dockerfile           # Docker image configuration
│   ├── docker-compose.yml   # Docker multi-container setup
│   └── requirements.txt     # Python dependencies
└── README.md                # Project documentation

```
## 🚀 Prerequisites
- Python 3.10 or higher
- Docker

## 🔧 Setup Instructions
1. **Run the Scrapy Project**

    Go to https://github.com/Marjia029/Scrappy_test_trip link and setup the scrapy project accordingly and run it first following the given istructions.
2. **Clone the repository**
   ```bash
   git clone https://github.com/Marjia029/ollama-llm.git
   cd ollama-llm
3. **Create a new virtual environment**
    ```bash
    python -m venv venv #or
    python3 -m venv venv #on linux
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

    Navigate to Django bash

    ```bash
    docker-compose exec django bash
    ```
    Now run commands for the migrations
    ```bash
    python manage.py makemigrations #or
    python manage.py makemigrations property
    python manage.py migrate
    ```
8. **Generate Data for the Database**

    In the Django bash run the following commands to generate the data

    ```bash
    python manage.py generate_title_and_description
    python manage.py generate_summary
    python manage.py generate_rating_and_review
    ```
9. **Create Super User to see the Database Using Django Admin**

    Navigate to Django bash and run commands for creating super user

    ```bash
    python manage.py createsuperuser
    ```
    Provide necessary information to successfully create super user. Now browse to http://localhost:8000/admin and login with your admin information to see the database.

## ⚙️ Testing

For running tests first navigate to the django bash-
```bash
docker-compose exec django bash
```
Now run the following command
```bash
python manage.py test
```
For inspecting coverage run-
```bash
coverage run manage.py test
coverage report
```
## 🙌 Contributing
Contributions are welcome! Feel free to fork this project, open issues, and submit pull requests.

    