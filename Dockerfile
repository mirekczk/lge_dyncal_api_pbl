    FROM python:3.11

    ADD main.py .

    ADD database.py .

    ADD models.py .

    ADD requirements.txt .

    RUN pip install -r requirements.txt

    COPY templates/ /templates/

    CMD ["python", "./main.py"]