FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .

RUN pip install -e .

ENV PYTHONUNBUFFERED=1

CMD ["bash"]