# Nginx Troubleshooting Guide

Common issues and solutions for nginx deployment on DigitalOcean droplet.

---

## Issue: Port Binding Error (Address Already in Use)

### Symptoms

```
nginx: [emerg] bind() to 0.0.0.0:80 failed (98: Address already in use)
nginx: [emerg] bind() to 0.0.0.0:443 failed (98: Address already in use)
```

### Root Cause

Multiple nginx master processes running, or another service holding ports 80/443.

### Quick Fix

```bash
cd infra/nginx
./fix-port-binding.sh
```

### Manual Fix

#### 1. Identify port holders

```bash
ssh root@178.128.112.214 "ss -ltnp | egrep '(:80 |:443 )'"
ssh root@178.128.112.214 "lsof -nP -iTCP:80 -sTCP:LISTEN"
```

#### 2. Stop all nginx processes

```bash
ssh root@178.128.112.214 "systemctl stop nginx"
ssh root@178.128.112.214 "pkill -9 nginx"
```

#### 3. Clean stale PID file

```bash
ssh root@178.128.112.214 "rm -f /run/nginx.pid"
```

#### 4. Restart via systemd

```bash
ssh root@178.128.112.214 "nginx -t && systemctl restart nginx"
```

---

## Issue: Localhost Works, External Fails

### Symptoms

- `curl http://127.0.0.1/healthz` works
- `curl http://superset.insightpulseai.com/healthz` times out

### Root Cause

Firewall blocking external access (UFW, iptables, or DigitalOcean Cloud Firewall).

### Fix

#### Check UFW

```bash
ssh root@178.128.112.214 "ufw status verbose"
```

#### Allow HTTP/HTTPS

```bash
ssh root@178.128.112.214 "ufw allow 80/tcp"
ssh root@178.128.112.214 "ufw allow 443/tcp"
ssh root@178.128.112.214 "ufw reload"
```

#### Check DigitalOcean Cloud Firewall

1. Go to DigitalOcean Console → Networking → Firewalls
2. Ensure inbound rules allow:
   - HTTP (port 80) from all sources
   - HTTPS (port 443) from all sources

---

## Issue: DNS Not Resolving

### Symptoms

```
curl: (6) Could not resolve host: n8n.insightpulseai.com
```

### Fix

#### Check DNS propagation

```bash
dig +short n8n.insightpulseai.com A
# Should return: 178.128.112.214
```

#### Wait for propagation

DNS changes can take 1-5 minutes (or up to 48 hours globally).

#### Force DNS refresh (local)

```bash
# macOS
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder

# Linux
sudo systemd-resolve --flush-caches
```

---

## Issue: Nginx Config Test Fails

### Symptoms

```
nginx: [emerg] unknown directive "proxy_pass" in /etc/nginx/sites-enabled/n8n.insightpulseai.com:10
```

### Fix

#### Test config

```bash
ssh root@178.128.112.214 "nginx -t"
```

#### Check for syntax errors

- Missing semicolons
- Incorrect directive names
- Invalid file paths

#### Reload after fix

```bash
ssh root@178.128.112.214 "nginx -t && systemctl reload nginx"
```

---

## Issue: Backend Service Not Responding

### Symptoms

- Nginx returns 502 Bad Gateway
- Nginx returns 504 Gateway Timeout

### Fix

#### Check backend service is running

```bash
# n8n (port 5678)
ssh root@178.128.112.214 "netstat -tlnp | grep 5678"

# MCP (port 8000)
ssh root@178.128.112.214 "netstat -tlnp | grep 8000"
```

#### Start backend service

```bash
# Example for n8n
ssh root@178.128.112.214 "systemctl start n8n"
```

#### Check backend logs

```bash
ssh root@178.128.112.214 "journalctl -u n8n -n 50"
```

---

## Issue: SSL Certificate Errors

### Symptoms

```
curl: (60) SSL certificate problem: unable to get local issuer certificate
```

### Fix

#### Check certificate status

```bash
ssh root@178.128.112.214 "certbot certificates"
```

#### Renew certificate

```bash
ssh root@178.128.112.214 "certbot renew"
```

#### Force renewal

```bash
ssh root@178.128.112.214 "certbot renew --force-renewal"
```

---

## Diagnostic Commands

### Check nginx status

```bash
ssh root@178.128.112.214 "systemctl status nginx"
```

### View nginx error logs

```bash
ssh root@178.128.112.214 "tail -f /var/log/nginx/error.log"
```

### View nginx access logs

```bash
ssh root@178.128.112.214 "tail -f /var/log/nginx/access.log"
```

### Check all listening ports

```bash
ssh root@178.128.112.214 "ss -ltnp"
```

### Check nginx processes

```bash
ssh root@178.128.112.214 "ps aux | grep nginx"
```

---

## Prevention

### Ensure nginx starts on boot

```bash
ssh root@178.128.112.214 "systemctl enable nginx"
```

### Always use systemd

```bash
# ✅ Correct
systemctl start nginx
systemctl stop nginx
systemctl restart nginx
systemctl reload nginx

# ❌ Avoid
nginx
/usr/sbin/nginx
service nginx start
```

### Test before reload

```bash
nginx -t && systemctl reload nginx
```

---

## Emergency Rollback

### Disable all custom configs

```bash
ssh root@178.128.112.214 "rm /etc/nginx/sites-enabled/*"
ssh root@178.128.112.214 "nginx -t && systemctl reload nginx"
```

### Restore default config

```bash
ssh root@178.128.112.214 "cp /etc/nginx/nginx.conf.backup /etc/nginx/nginx.conf"
ssh root@178.128.112.214 "nginx -t && systemctl restart nginx"
```

---

## References

- [Nginx Documentation](https://nginx.org/en/docs/)
- [DigitalOcean Nginx Tutorials](https://www.digitalocean.com/community/tags/nginx)
- [Certbot Documentation](https://certbot.eff.org/docs/)
