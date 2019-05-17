FROM python:3

COPY . .

# COPY requirements.txt /requirements.txt
# COPY src /src

# COPY local.env /local.env

RUN pip install -r requirements.txt

EXPOSE 80

CMD ["python", "-u", "src/app.py"]
