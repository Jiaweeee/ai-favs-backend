#!/bin/bash

if ! command -v uvicorn &> /dev/null
then
    echo "uvicorn could not be found, please install it to use this script."
    exit 1
fi

uvicorn app.server:app --host 0.0.0.0 --port 8000