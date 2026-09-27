import os
import time

from fastapi import FastAPI, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from redis import Redis

app = FastAPI(title="DevOps Evaluation API")

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
redis_client = Redis.from_url(REDIS_URL, decode_responses=True)

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["endpoint", "code"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["endpoint"],
)

APP_VERSION = os.getenv("APP_VERSION", "dev")

VERSION_INFO = Gauge(
    "app_version_info",
    "Currently deployed application version",
    ["version"],
)


@app.middleware("http")
async def metrics_middleware(request, call_next):
    start_time = time.perf_counter()

    response = await call_next(request)

    duration = time.perf_counter() - start_time
    endpoint = request.url.path
    code = str(response.status_code)

    REQUEST_COUNT.labels(
        endpoint=endpoint,
        code=code,
    ).inc()

    REQUEST_LATENCY.labels(
        endpoint=endpoint,
    ).observe(duration)

    return response


@app.on_event("startup")
def startup():
    VERSION_INFO.labels(version=APP_VERSION).set(1)


@app.get("/")
def root():
    redis_client.incr("requests")

    return {
        "message": "DevOps Evaluation API",
        "version": APP_VERSION,
    }


@app.get("/health")
def health():
    redis_client.ping()

    return {
        "status": "healthy",
        "version": APP_VERSION,
    }


@app.get("/test-error")
def test_error():
    return Response(
        content='{"error":"intentional test error"}',
        status_code=500,
        media_type="application/json",
    )


@app.get("/test-slow")
def test_slow():
    time.sleep(0.6)

    return {
        "message": "intentional slow response",
    }


@app.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
