FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /market_sim
COPY ./market_sim /market_sim
RUN pip install -r requirements.txt
