#!/bin/bash

# set -o: option-name - set the variable corresponding to option-name
# nounset: same as -u, which is: Treat unset variables as an error when substituting.
# errexit: same as -e, which is: Exit immediately if a command exits with a non-zero status.
# xtrace: same as -x, which is: Print commands and their arguments as they are executed.
# For more information, type, "help set", in your terminal
set -o nounset -o errexit -o xtrace

cd /app/continuous_integration
python initialize_database.py

# Change directories back to /app
cd ..

# Migrate Schemas to test database
alembic upgrade head
