#!/bin/bash

# Capture the docker command as argument
DOCKER_COMMAND="$@"

# Run tests
cd ../medical-insights-extractor/tests
echo "Running tests..."
pytest

# Check the exit status of pytest
if [ $? -eq 0 ]; then
    echo "Tests passed successfully. Proceeding to build Docker image."
    cd ../../demo-site
    eval "$DOCKER_COMMAND"
else
    echo "Tests failed. Aborting Docker image build."
fi
