FROM python:3.12.4-alpine3.19

ARG RELEASE_VERSION
ENV RELEASE_VERSION=${RELEASE_VERSION}

ENV SPOTIPY_CLIENT_ID ""
ENV SPOTIPY_CLIENT_SECRET ""
ENV PLEX_URL ""
ENV PLEX_TOKEN ""
ENV SPOTIFY_URIS ""
ENV SPOTIPY_PATH ""
ENV SECONDS_TO_WAIT 3600

WORKDIR /app/

# Copy all Python files from the src folder into the container
COPY . /app/

# Install dependencies
RUN apk add --no-cache ffmpeg
RUN pip install -r /app/requirements.txt

# Print ASCII art with release version
RUN echo "██████╗ ██╗     ███████╗██╗  ██╗ ██╗ ███████╗██╗   ██╗" > /ascii_art.txt && \
    echo "██╔══██╗██║     ██╔════╝╚██╗██╔╝ ██║ ██╔════╝╚██╗ ██╔╝" >> /ascii_art.txt && \
    echo "██████╔╝██║     █████╗   ╚███╔╝  ██║ █████╗   ╚████╔╝ " >> /ascii_art.txt && \
    echo "██╔═══╝ ██║     ██╔══╝   ██╔██╗  ██║ ██╔══╝    ╚██╔╝  " >> /ascii_art.txt && \
    echo "██║     ███████╗███████╗██╔╝ ██╗ ██║ ██║        ██║   " >> /ascii_art.txt && \
    echo "╚═╝     ╚══════╝╚══════╝╚═╝  ╚═╝ ╚═╝ ╚═╝        ╚═╝   " >> /ascii_art.txt && \
    echo "Release Version: ${RELEASE_VERSION}" >> /ascii_art.txt

# Run the main script
CMD ["sh", "-c", "cat /ascii_art.txt && python /app/main.py"]