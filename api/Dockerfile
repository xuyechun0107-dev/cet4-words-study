FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN groupadd --gid 1000 appgroup \
    && useradd --uid 10001 --gid appgroup --create-home --shell /usr/sbin/nologin appuser

COPY --chown=10001:1000 app ./app

USER 10001:1000

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
