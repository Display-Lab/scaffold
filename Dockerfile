# This dockerfile uses a multi-stage Docker build
# to try to keep the image size as small as possible.
# (Saves about 500MB at time of writing)
# See here: https://docs.docker.com/build/building/multi-stage/

#----build container----#
FROM python:3.10-slim-bullseye as build-pkgs

WORKDIR /code/app

# Install build dependencies
RUN apt-get update && apt-get install -y build-essential cmake pkg-config g++ gcc gfortran libopenblas-dev && apt-get clean

# Set up a pythone virtual environment to aid
# in copying python packages later
RUN mkdir -p /code/app/venv && python3 -m venv /code/app/venv

# Activate virtual environment and install requirements
ENV PATH="/code/app/venv/bin:$PATH"
COPY requirements.txt /code/app
RUN pip3 install --no-cache-dir --upgrade -r /code/app/requirements.txt

#----application container----#
FROM python:3.10-slim-bullseye

# Create an unprivileged user because this container runs as root otherwise
RUN groupadd -g 1334 python-runner \
    && useradd -r -u 1334 -g python-runner python-runner

# make a home directory and app code directory
RUN mkdir -p /code/app \
    && mkdir -p /home/python-runner \
    && chown python-runner:python-runner /code/app /home/python-runner

WORKDIR /code/app

# Copy venv from previous stage and application code
COPY --chown=python-runner:python-runner --from=build-pkgs /code/app/venv /code/app/venv
COPY --chown=python-runner:python-runner . /code/app

# Run this applicaiton as the unprivileged user we created
# earlier
USER 1334

# Activate the virtual python environment
# that was built in the previous stage
ENV PATH="/code/app/venv/bin:$PATH"

# Start up main app
EXPOSE 8080
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]

