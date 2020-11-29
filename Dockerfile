FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /code
EXPOSE 8000
RUN apt-get update && apt-get install -y swig3.0
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
RUN python3 manage.py migrate
CMD ["python3", "manage.py", "runserver"]