FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements.txt

COPY app.py .
COPY src/ src/
COPY assets/ assets/
COPY data/app/ data/app/
COPY models/model_manifest.json models/model_manifest.json
COPY models/zensus_hgb_meta.json models/zensus_hgb_meta.json
COPY reports/algorithm_benchmark.json reports/algorithm_benchmark.json
COPY reports/dataset_build_report.json reports/dataset_build_report.json
COPY reports/final_model_evaluation.json reports/final_model_evaluation.json
COPY reports/mlflow_publish.json reports/mlflow_publish.json

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health', timeout=3)"

CMD ["python", "-m", "streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
