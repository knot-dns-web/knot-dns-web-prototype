FROM cznic/knot:latest

WORKDIR /app

COPY requirements.txt requirements.txt

#RUN \
#    apt-get update && \
#    apt-get install python3 -y && \
#    apt-get install python3-pip -y && \
#    apt-get install python3-venv -y && \
#    rm -rf /var/lib/apt/lists/* && \
#    python3 -m venv /app/.venv && \
#    . /app/.venv/bin/activate && \
#    pip install --upgrade pip && \
#    pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /app/.venv && \
    /app/.venv/bin/pip install --upgrade pip && \
    /app/.venv/bin/pip install --no-cache-dir -r requirements.txt

ENV PATH="/app/.venv/bin:$PATH"

COPY ./src/backend/src /app/src
COPY ./.devcontainer /app/.devcontainer
COPY ./.gitignore /app/.gitignore
COPY ./.dockerignore /app/.dockerignore
COPY ./docker /app/docker
COPY ./docker/launch.json /app/.vscode/launch.json
COPY ./docker/settings.json /app/.vscode/settings.json

COPY ./conftest.py /app/conftest.py
COPY ./pytest.ini /app/pytest.ini
COPY ./check_knot.py /app/check_knot.py
COPY ./run_check.sh /app/run_check.sh

# Setup entrypoint
COPY ./src/backend/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]