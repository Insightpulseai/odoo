# Nginx Configuration for IPAI Services

Reverse proxy configurations for n8n, Superset, and MCP services.

---

## Services

| Service  | Domain                      | Backend Port         | Status                     |
| -------- | --------------------------- | -------------------- | -------------------------- |
| n8n      | n8n.insightpulseai.com      | 5678                 | ✅ Configured              |
| Superset | superset.insightpulseai.com | (existing)           | ✅ Working                 |
| MCP      | mcp.insightpulseai.com      | 8000 (TODO: confirm) | ⚠️ Port needs verification |

---

## Quick Start

### 1. Deploy nginx configurations

```bash
cd infra/nginx

# Dry run (preview changes)
./deploy-nginx-configs.sh --dry-run

# Deploy to droplet
./deploy-nginx-configs.sh
```

### 2. Verify HTTP access

```bash
curl -I http://n8n.insightpulseai.com
curl -I http://mcp.insightpulseai.com
```

### 3. Set up HTTPS

```bash
# Dry run (preview changes)
./setup-https.sh --dry-run

# Deploy SSL certificates
./setup-https.sh
```

### 4. Verify HTTPS access

```bash
curl -I https://n8n.insightpulseai.com
curl -I https://superset.insightpulseai.com
curl -I https://mcp.insightpulseai.com
```

---

## Configuration Files

### n8n.insightpulseai.com.conf

- **Backend**: `http://localhost:5678`
- **Features**: WebSocket support, 300s timeout for long workflows
- **HTTPS**: Configured by certbot

### mcp.insightpulseai.com.conf

- **Backend**: `http://localhost:8000` (TODO: confirm port)
- **Features**: WebSocket support, 300s timeout
- **HTTPS**: Configured by certbot

---

## Manual Deployment (Alternative)

If you prefer manual deployment:

### Deploy n8n config

```bash
scp n8n.insightpulseai.com.conf root@178.128.112.214:/etc/nginx/sites-available/
ssh root@178.128.112.214 "ln -sf /etc/nginx/sites-available/n8n.insightpulseai.com.conf /etc/nginx/sites-enabled/"
ssh root@178.128.112.214 "nginx -t && systemctl reload nginx"
```

### Deploy MCP config

```bash
# First, confirm MCP port and update mcp.insightpulseai.com.conf

scp mcp.insightpulseai.com.conf root@178.128.112.214:/etc/nginx/sites-available/
ssh root@178.128.112.214 "ln -sf /etc/nginx/sites-available/mcp.insightpulseai.com.conf /etc/nginx/sites-enabled/"
ssh root@178.128.112.214 "nginx -t && systemctl reload nginx"
```

### Set up HTTPS

```bash
ssh root@178.128.112.214 "certbot --nginx -d n8n.insightpulseai.com -d superset.insightpulseai.com -d mcp.insightpulseai.com --non-interactive --agree-tos -m admin@insightpulseai.com"
```

---

## Troubleshooting

### Check nginx status

```bash
ssh root@178.128.112.214 "systemctl status nginx"
```

### View nginx error logs

```bash
ssh root@178.128.112.214 "tail -f /var/log/nginx/error.log"
```

### Test nginx configuration

```bash
ssh root@178.128.112.214 "nginx -t"
```

### Check service ports

```bash
# n8n (should be 5678)
ssh root@178.128.112.214 "netstat -tlnp | grep 5678"

# MCP (confirm actual port)
ssh root@178.128.112.214 "netstat -tlnp | grep -E '(3000|8000|8080)'"
```

### Check SSL certificate status

```bash
ssh root@178.128.112.214 "certbot certificates"
```

### Test SSL certificate renewal

```bash
ssh root@178.128.112.214 "certbot renew --dry-run"
```

---

## MCP Port Configuration

**TODO**: Confirm MCP service port and update `mcp.insightpulseai.com.conf`

Common MCP ports:

- 3000 (Node.js default)
- 8000 (Python default)
- 8080 (Alternative HTTP)

To find the actual port:

```bash
ssh root@178.128.112.214 "ps aux | grep mcp"
ssh root@178.128.112.214 "netstat -tlnp | grep mcp"
```

---

## Security Notes

### HTTPS Configuration

- Certificates auto-renew via systemd timer
- Check renewal status: `systemctl status certbot.timer`
- Manual renewal: `certbot renew`

### Firewall

Ensure ports 80 and 443 are open:

```bash
ssh root@178.128.112.214 "ufw status"
```

### Rate Limiting (Optional)

Add to nginx config if needed:

```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req zone=api_limit burst=20 nodelay;
```

---

## References

- [Nginx Reverse Proxy Guide](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)
- [Certbot Documentation](https://certbot.eff.org/instructions)
- [n8n Self-Hosting Guide](https://docs.n8n.io/hosting/)
