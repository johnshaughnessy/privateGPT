FROM python:3.10
RUN apt-get update && apt-get install -y pipx
RUN useradd -ms /bin/bash httpserver
USER httpserver
RUN pipx install poetry
ENV PATH="/home/httpserver/.local/bin:${PATH}"
WORKDIR /usr/src/privateGPT
COPY pyproject.toml ./
COPY poetry.lock ./
RUN poetry env use 3.10
COPY . .
RUN poetry install --no-root
RUN poetry install -E server --no-root
CMD poetry run -- python server.py
