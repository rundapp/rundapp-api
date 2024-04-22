FROM python:3.8

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

# Database Environment Variables
ENV DB_URL=inject_at_deployment

# Server Environment Variables
ENV OPENAPI_URL="/openapi.json"
ENV SERVER_PORT=8000

ENV ENVIRONMENT=development

# Strava Environment Variables
ENV VERIFY_TOKEN=inject_at_deployment
ENV CLIENT_ID=inject_at_deployment
ENV CLIENT_SECRET=inject_at_deployment

# Ethereum Environment Variables
ENV SIGNER_PRIVATE_KEY=inject_at_deployment
ENV SIGNER_ADDRESS=inject_at_deployment
ENV ABI=inject_at_deployment
ENV RPC_URL=inject_at_deployment
ENV CONTRACT_ADDRESS=inject_at_deployment

# Sendgrid Environment Variables
ENV SENDGRID_API_KEY=inject_at_deployment

# Miscellaneous Environment Variables
ENV SENDER_EMAIL_ADDRESS=inject_at_deployment

EXPOSE $SERVER_PORT

CMD ["python", "-m", "app"]


