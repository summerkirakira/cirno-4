FROM python:3.10.12-bookworm
RUN curl https://install.python-poetry.org | python3 -
COPY . /app
WORKDIR /app
RUN /root/.local/bin/poetry install
EXPOSE 8080
CMD ["/root/.local/bin/poetry", "run", "python", "bot.py"]