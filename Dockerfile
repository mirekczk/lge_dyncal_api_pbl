    FROM python:3.11-slim

    WORKDIR /app
    COPY main.py database.py models.py logger.py requirements.txt  /app/

    ENV login_test=
    ENV password_test=
    ENV login_prod=
    ENV password_prod=

    RUN pip install -r requirements.txt

    COPY templates/ /app/templates/

    EXPOSE 5052

    CMD ["python", "/app/main.py"]
