FROM python:3

COPY requirements.txt /requirements.txt
COPY src /src

COPY local.env /local.env

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "src/app.py"]
