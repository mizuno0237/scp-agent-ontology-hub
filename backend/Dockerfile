FROM python:3.12.8-slim

WORKDIR /srv
COPY backend/requirements.txt /srv/requirements.txt
RUN pip install --no-cache-dir -r /srv/requirements.txt
COPY backend/app /srv/app
COPY samples /samples
ENV SAMPLE_ROOT=/samples/supply-chain
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
