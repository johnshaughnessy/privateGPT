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
RUN poetry lock --no-update
RUN poetry install -E server --no-root
RUN poetry run -- python fix.py

# # The next two lines are for my Linux machine without a torch-compatible GPU
# RUN poetry run -- pip uninstall -y torch
# RUN poetry run -- pip install torch==2.0.1+cpu -f https://download.pytorch.org/whl/torch_stable.html

CMD poetry run -- python server.py
