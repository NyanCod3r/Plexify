FROM python:3.12.4-alpine3.19

ARG RELEASE_VERSION
ENV RELEASE_VERSION=${RELEASE_VERSION}

ENV SPOTIPY_CLIENT_ID ""
ENV SPOTIPY_CLIENT_SECRET ""
ENV PLEX_URL ""
ENV PLEX_TOKEN ""
ENV SPOTIFY_URIS ""
ENV MUSIC_PATH ""
ENV LOG_LEVEL ""
ENV SPOTDL_LOG_LEVEL ""
ENV SECONDS_TO_WAIT ""
ENV DOWNLOAD_DELAY ""
ENV PREFER_FLAC ""

WORKDIR /app

# Copy all project files into the container
COPY . .

# Add build dependencies before pip install
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    python3-dev

# Install dependencies
RUN apk add --no-cache ffmpeg
RUN pip install -r /app/src/requirements.txt

# Remove build dependencies to keep image small
RUN apk del .build-deps

# Print ASCII art with release version
RUN echo "██████╗ ██╗     ███████╗██╗  ██╗ ██╗ ███████╗██╗   ██╗" > /ascii_art.txt && \
    echo "██╔══██╗██║     ██╔════╝╚██╗██╔╝ ██║ ██╔════╝╚██╗ ██╔╝" >> /ascii_art.txt && \
    echo "██████╔╝██║     █████╗   ╚███╔╝  ██║ █████╗   ╚████╔╝ " >> /ascii_art.txt && \
    echo "██╔═══╝ ██║     ██╔══╝   ██╔██╗  ██║ ██╔══╝    ╚██╔╝  " >> /ascii_art.txt && \
    echo "██║     ███████╗███████╗██╔╝ ██╗ ██║ ██║        ██║   " >> /ascii_art.txt && \
    echo "╚═╝     ╚══════╝╚══════╝╚═╝  ╚═╝ ╚═╝ ╚═╝        ╚═╝   " >> /ascii_art.txt && \
    echo "Release Version: ${RELEASE_VERSION}" >> /ascii_art.txt

# Run the main script
CMD ["sh", "-c", "cat /ascii_art.txt && python /app/src/main.py"]