#!/bin/sh
set -e

CONFIG="/data/gitea/conf/app.ini"
USERNAME="waynelee"
FULLNAME="WAYNE LEE"
EMAIL="2400968@sit.singaporetech.edu.sg"
PASSWORD="2400968@SIT.singaporetech.edu.sg"
GITEA_URL="http://gitea:3000"

# Make sure curl is available in this container (gitea-init shares the gitea image).
# wget (busybox) is present by default and used as a fallback for the wait-loop.
if ! command -v curl > /dev/null 2>&1; then
  apk add --no-cache curl > /dev/null 2>&1 || true
fi

check_api() {
  if command -v curl > /dev/null 2>&1; then
    curl -sf "$GITEA_URL/api/healthz" > /dev/null 2>&1
  else
    wget -q -O- "$GITEA_URL/api/healthz" > /dev/null 2>&1
  fi
}

echo "Waiting for Gitea config to exist..."
until [ -f "$CONFIG" ]; do
  sleep 2
done

echo "Waiting for Gitea HTTP API to be reachable at $GITEA_URL..."
until check_api; do
  sleep 2
done

echo "Checking if user '$USERNAME' already exists..."
if su git -c "gitea admin user list --config $CONFIG" | awk '{print $2}' | grep -qx "$USERNAME"; then
  echo "User '$USERNAME' already exists. Skipping creation."
else
  echo "Creating Gitea user '$USERNAME'..."
  su git -c "gitea admin user create \
    --config $CONFIG \
    --username $USERNAME \
    --password '$PASSWORD' \
    --email '$EMAIL' \
    --must-change-password=false"
fi

# Full name (display name) isn't settable via the CLI, so set it through the REST API.
echo "Setting full name to '$FULLNAME' via API..."
curl -sf -u "$USERNAME:$PASSWORD" \
  -X PATCH "$GITEA_URL/api/v1/user/settings" \
  -H "Content-Type: application/json" \
  -d "{\"full_name\": \"$FULLNAME\"}" \
  > /dev/null \
  && echo "Full name set successfully." \
  || echo "Warning: could not set full name via API (non-fatal, can be set manually in profile settings)."

echo "Gitea identity setup complete: username=$USERNAME, full_name=$FULLNAME, email=$EMAIL"
