FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY clinicapp/ clinicapp/

ENV FLASK_APP=clinicapp/index.py

EXPOSE 5000

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]
