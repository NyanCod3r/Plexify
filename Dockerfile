FROM python:3.12.4-alpine3.19

ENV SPOTIPY_CLIENT_ID ""
ENV SPOTIPY_CLIENT_SECRET ""
ENV PLEX_URL ""
ENV PLEX_TOKEN ""
ENV SPOTIFY_URIS ""
ENV SPOTIPY_PATH ""
ENV SECONDS_TO_WAIT 3600

WORKDIR /app/

COPY spotify-sync.py /app/spotify-sync.py
COPY requirements.txt /app/requirements.txt

RUN apk add --no-cache ffmpeg
RUN pip install -r requirements.txt

CMD python spotify-sync.py