FROM python:3.10-alpine

WORKDIR /app

COPY . .

RUN pip install .

CMD ["python", "-m", "simplesocket", "server", "3000"]
