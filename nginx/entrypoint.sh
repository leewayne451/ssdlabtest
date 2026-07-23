#!/bin/sh
set -e

# Generate self-signed cert if it doesn't already exist
if [ ! -f /etc/nginx/ssl/nginx.crt ]; then
  mkdir -p /etc/nginx/ssl
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/nginx.key \
    -out /etc/nginx/ssl/nginx.crt \
    -subj "/C=SG/ST=Singapore/L=Singapore/O=SIT/CN=127.0.0.1"
fi

# Create/refresh the htpasswd file from env vars every start
htpasswd -bc /etc/nginx/.htpasswd "$ADMIN_USER" "$ADMIN_PASS"

exec nginx -g "daemon off;"
