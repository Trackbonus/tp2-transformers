
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN groupadd --gid 10001 app \
    && useradd --uid 10001 --gid app --create-home --shell /usr/sbin/nologin app \
    && mkdir -p /workspace \
    && chown -R app:app /workspace

# PyTorch para CPU
RUN python -m pip install --no-cache-dir torch==2.7.1 \
    --index-url https://download.pytorch.org/whl/cu118

WORKDIR /workspace

COPY requirements.txt /tmp/requirements.txt

RUN python -m pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

USER 10001:10001

CMD ["sleep", "infinity"]
