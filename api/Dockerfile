FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# The command is provided by docker-compose for dev overrides,
# but we supply a default one for production readiness.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
