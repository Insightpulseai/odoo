# SSL Certificates

This directory should contain SSL certificates for the Nginx reverse proxy.

## Development (Self-signed)

Generate a self-signed certificate for development:

```bash
cd docker/nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout odoo.key -out odoo.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
```

## Production

For production, use certificates from a trusted CA (e.g., Let's Encrypt):

1. Place your certificate as `odoo.crt`
2. Place your private key as `odoo.key`
3. Optionally add CA chain as `ca.crt`

## File Permissions

Ensure proper permissions:

```bash
chmod 644 odoo.crt
chmod 600 odoo.key
```

## Let's Encrypt with Certbot

```bash
certbot certonly --webroot -w /var/www/certbot \
    -d your-domain.com \
    --email your-email@example.com
```

Then symlink or copy:
```bash
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem odoo.crt
cp /etc/letsencrypt/live/your-domain.com/privkey.pem odoo.key
```
