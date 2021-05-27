FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY . /code
RUN mkdir /code/static
COPY Pipfile Pipfile.lock /code
RUN pip install --upgrade pip
RUN pip install pipenv && pipenv install --system --deploy


