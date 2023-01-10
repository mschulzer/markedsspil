FROM python:3

# prevent Python from buffering stdin/stdout
ENV PYTHONUNBUFFERED=1

# prevent Python from writing bytecode .pyc to disk
ENV PYTHONDONTWRITEBYTECODE 1

# Create working directory and copy project files
WORKDIR /code
COPY . /code
RUN mkdir -p /code/static
COPY Pipfile Pipfile.lock /code/

# Install pip, pipenv, and requirements
RUN pip install --upgrade pip
RUN pip install django-allauth
RUN pip install django-dbbackup
RUN pip install django-sekizai
RUN pip install factory-boy

RUN pip install pipenv && pipenv install --system --dev --deploy

