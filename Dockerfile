FROM python:3.13

RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://ollama.com/install.sh | sh

RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH="home/user/.local/bin:$PATH"

WORKDIR $HOME/app

COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY --chown=user . .

RUN chmod +x start.sh

EXPOSE 7860

CMD ["./start.sh"]