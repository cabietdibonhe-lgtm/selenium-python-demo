#!/usr/bin/env bash
set -e

PORT="${STATIC_SERVER_PORT:-8000}"

echo "=== Start static server (site) on port ${PORT} ==="

ls -la
test -d site
test -f site/index.html

mkdir -p logs

cd site
python3 -m http.server "${PORT}" > ../logs/http_server.log 2>&1 &
echo $! > ../logs/http_server.pid
cd ..

# wait until server ready
for i in {1..20}; do
  if curl -s "http://127.0.0.1:${PORT}/index.html" >/dev/null; then
    echo "Server is UP"
    exit 0
  fi
  sleep 0.5
done

echo "Server failed to start"
exit 1
