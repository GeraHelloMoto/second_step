FROM python:3.12-slim


RUN addgroup --system --gid 1000 appuser && \
    adduser --system --uid 1000 --ingroup appuser --home /home/appuser appuser

WORKDIR /app


COPY pyproject.toml uv.lock ./
COPY src/ ./src/


RUN chown -R appuser:appuser /app


RUN pip install uv


USER appuser


RUN uv sync --frozen --no-dev

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]