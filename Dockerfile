FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py ./
COPY templates ./templates
COPY static ./static
ENV DATA_DIR=/app/data
ENV PORT=5003
RUN mkdir -p /app/data/uploads
EXPOSE 5003
CMD ["python", "app.py"]