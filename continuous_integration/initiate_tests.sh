#!/bin/sh


# set -e: Exit immediately if a command exits with a non-zero status.
# set -v: Print shell input lines as they are read.
# set -x: Print commands and their arguments as they are executed.
set -evx

# cd into the container's app directory
cd /app

# Run continuous integration tasks
inv ci