FROM python:3.10-alpine

WORKDIR /app

COPY . .

CMD ["python", "-u", "src/simplesocket", "server", "3000"]
