#!/usr/bin/bash

set -e

echo "Run apply migrations.."
alembic upgrade head
echo "Migrations applied!"

echo "Creating keys..."
mkdir -p ./certs

echo "Generating private RSA key (2048 bits)..."
if [ ! -f /src/certs/jwt-private.pem ]; then
    openssl genrsa -out /src/certs/jwt-private.pem 2048
    echo "Private key generated successfully"
fi

echo "Extracting public key from the key pair..."
if [ ! -f /src/certs/jwt-public.pem ]; then
    openssl rsa -in /src/certs/jwt-private.pem -outform PEM -pubout -out /src/certs/jwt-public.pem
    echo "Public key extracted successfully"
fi

echo "Keys created!"

echo "Creatings log File"
mkdir -p ./logs
touch ./logs/app.log

echo "Creating Storage folder"
if [ ! -d /src/storage ]; then
    mkdir -p /src/storage
    echo "Storage folder created"
fi

exec "$@"
