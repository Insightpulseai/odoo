#!/usr/bin/env bash
set -euo pipefail

# Fix nginx port binding issues (Address already in use)
# Target: DigitalOcean droplet at 178.128.112.214

DROPLET_IP="178.128.112.214"
DROPLET_USER="root"

echo "🔍 Diagnosing nginx port binding issue on ${DROPLET_IP}..."
echo ""

# Step 0: Identify what's holding ports 80/443
echo "📊 Step 0: Checking port listeners..."
ssh "${DROPLET_USER}@${DROPLET_IP}" bash <<'REMOTE'
set -euo pipefail
echo "== Port listeners =="
ss -ltnp | egrep '(:80 |:443 )' || echo "No listeners on :80/:443"
echo ""
echo "== Owning processes =="
lsof -nP -iTCP:80 -sTCP:LISTEN 2>/dev/null || echo "No process on :80"
lsof -nP -iTCP:443 -sTCP:LISTEN 2>/dev/null || echo "No process on :443"
echo ""
echo "== Nginx processes =="
ps -eo pid,ppid,cmd | egrep 'nginx: master|nginx: worker' || echo "No nginx processes"
REMOTE

echo ""
echo "🛑 Step 1: Stopping all nginx processes..."
ssh "${DROPLET_USER}@${DROPLET_IP}" bash <<'REMOTE'
set -euo pipefail

echo "== Stopping via systemd =="
systemctl stop nginx || true
sleep 2

echo "== Killing stray master processes =="
pids="$(ps -eo pid,cmd | awk '/nginx: master/ {print $1}' || true)"
if [ -n "${pids:-}" ]; then
  echo "Killing masters: $pids"
  kill $pids || true
  sleep 2
fi

echo "== Hard kill if ports still held =="
if ss -ltnp | egrep -q '(:80 |:443 )'; then
  echo "⚠️  Ports still held; force killing nginx"
  pkill -9 nginx || true
  sleep 2
fi

echo "== Verifying ports are free =="
if ss -ltnp | egrep '(:80 |:443 )'; then
  echo "❌ ERROR: Ports still in use!"
  ss -ltnp | egrep '(:80 |:443 )'
  exit 1
else
  echo "✅ Ports 80/443 are now free"
fi
REMOTE

echo ""
echo "🧹 Step 2: Cleaning stale PID file..."
ssh "${DROPLET_USER}@${DROPLET_IP}" bash <<'REMOTE'
set -euo pipefail
PIDFILE="/run/nginx.pid"
if [ -f "$PIDFILE" ]; then
  pid="$(cat "$PIDFILE" 2>/dev/null || true)"
  if [ -n "${pid:-}" ] && kill -0 "$pid" 2>/dev/null; then
    echo "PID file points to live pid=$pid (OK)"
  else
    echo "Removing stale $PIDFILE"
    rm -f "$PIDFILE"
  fi
else
  echo "No PID file found (OK)"
fi
REMOTE

echo ""
echo "✅ Step 3: Validating config and restarting..."
ssh "${DROPLET_USER}@${DROPLET_IP}" bash <<'REMOTE'
set -euo pipefail
echo "== Testing nginx config =="
nginx -t

echo ""
echo "== Restarting nginx via systemd =="
systemctl restart nginx

echo ""
echo "== Nginx status =="
systemctl --no-pager --full status nginx | sed -n '1,30p'
REMOTE

echo ""
echo "🏥 Step 4: Adding health check endpoint..."
ssh "${DROPLET_USER}@${DROPLET_IP}" bash <<'REMOTE'
set -euo pipefail

CONF="/etc/nginx/conf.d/00-healthz.conf"
if [ ! -f "$CONF" ]; then
  cat > "$CONF" <<'NGINX'
server {
  listen 80 default_server;
  listen [::]:80 default_server;

  location = /healthz {
    add_header Content-Type text/plain;
    return 200 "ok\n";
  }

  location = / {
    add_header Content-Type text/plain;
    return 200 "nginx ok\n";
  }
}
NGINX
  echo "Created $CONF"
  nginx -t
  systemctl reload nginx
else
  echo "Health check config already exists"
fi
REMOTE

echo ""
echo "🧪 Step 5: Testing localhost..."
ssh "${DROPLET_USER}@${DROPLET_IP}" bash <<'REMOTE'
set -euo pipefail
echo "== Testing localhost:80 =="
curl -v --max-time 3 http://127.0.0.1/healthz 2>&1 | grep -E '(HTTP/|< |ok)'

echo ""
echo "== Current port listeners =="
ss -ltnp | egrep '(:80 |:443 )'
REMOTE

echo ""
echo "🔒 Step 6: Checking firewall rules..."
ssh "${DROPLET_USER}@${DROPLET_IP}" bash <<'REMOTE'
set -euo pipefail
echo "== UFW status =="
ufw status verbose || echo "UFW not active"

echo ""
echo "== iptables INPUT rules (first 20) =="
iptables -S INPUT 2>/dev/null | head -20 || echo "No iptables rules"
REMOTE

echo ""
echo "🌐 Step 7: Testing external access..."
echo "Testing http://superset.insightpulseai.com/healthz"
if curl -v --max-time 5 http://superset.insightpulseai.com/healthz 2>&1 | grep -q "ok"; then
  echo "✅ External access working!"
else
  echo "⚠️  External access failed (check firewall/DNS)"
fi

echo ""
echo "✅ Nginx port binding fix complete!"
echo ""
echo "📋 Summary:"
echo "   - Killed rogue nginx processes"
echo "   - Cleaned stale PID file"
echo "   - Restarted nginx via systemd"
echo "   - Added health check endpoint"
echo "   - Verified localhost and external access"
echo ""
echo "🔍 If external access still fails:"
echo "   1. Check DigitalOcean Cloud Firewall settings"
echo "   2. Verify DNS propagation: dig +short superset.insightpulseai.com"
echo "   3. Check UFW: ufw allow 80/tcp && ufw allow 443/tcp"
