# Keycloak Identity Provider Deployment Guide
## Unified Authentication for InsightPulse AI Ecosystem

**Target Environment**: Production Droplet (159.223.75.148)
**DNS**: `auth.insightpulseai.net` → 159.223.75.148

---

## 🚀 Quick Start Deployment

### Phase 1: Database Setup

1. **SSH to Production Droplet**
   ```bash
   ssh root@159.223.75.148
   cd /opt/odoo-ce
   ```

2. **Run Database Setup Script**
   ```bash
   chmod +x scripts/setup_keycloak_db.sh
   ./scripts/setup_keycloak_db.sh
   ```

3. **Verify Database Creation**
   ```bash
   docker exec odoo_prod_db_1 psql -U odoo -d postgres -c "\l"
   ```

### Phase 2: Keycloak Deployment

1. **Update docker-compose.prod.yml**
   ```bash
   # Add the Keycloak service block from deploy/keycloak-integration.yml
   # to your existing docker-compose.prod.yml
   ```

2. **Set Secure Admin Password**
   ```bash
   # Edit docker-compose.prod.yml and replace:
   # KEYCLOAK_ADMIN_PASSWORD=YOUR_SECURE_PASSWORD_HERE
   # with a strong password
   ```

3. **Deploy Keycloak**
   ```bash
   docker compose -f docker-compose.prod.yml up -d keycloak
   ```

4. **Verify Deployment**
   ```bash
   docker compose -f docker-compose.prod.yml ps
   docker compose -f docker-compose.prod.yml logs keycloak
   ```

5. **Access Keycloak**
   - URL: https://auth.insightpulseai.net
   - Username: `admin`
   - Password: Your secure password

---

## 🔗 Keycloak Configuration

### A. Create InsightPulse Realm

1. **Log in to Keycloak Admin Console**
   - Access: https://auth.insightpulseai.net
   - Use admin credentials

2. **Create New Realm**
   - Click dropdown in top-left corner
   - Select "Create Realm"
   - Name: `insightpulse`
   - Click "Create"

3. **Configure Realm Settings**
   - **Display Name**: InsightPulse AI
   - **Frontend URL**: https://auth.insightpulseai.net
   - **Enabled**: ON
   - **User registration**: OFF (for now)
   - **Login with email**: ON

### B. Create Users

1. **Add Initial Users**
   - Go to **Manage > Users**
   - Click "Add user"
   - Username: `khalil.veracruz@omc.com`
   - Email: `khalil.veracruz@omc.com`
   - First name: `Khalil`
   - Last name: `Veracruz`
   - Email verified: ON

2. **Set Temporary Passwords**
   - Click user > Credentials tab
   - Set temporary password
   - Temporary: ON
   - Click "Set Password"

3. **Repeat for Other Users**
   - Add all team members (RIM, BOM, JPAL, etc.)

### C. Configure Odoo Client

1. **Create Odoo Client**
   - Go to **Clients**
   - Click "Create"
   - **Client ID**: `odoo`
   - **Client Protocol**: `openid-connect`
   - Click "Save"

2. **Configure Client Settings**
   - **Name**: Odoo ERP
   - **Enabled**: ON
   - **Access Type**: `confidential`
   - **Valid Redirect URIs**: `https://erp.insightpulseai.net/*`
   - **Web Origins**: `https://erp.insightpulseai.net`
   - **Admin URL**: `https://erp.insightpulseai.net`

3. **Get Client Secret**
   - Go to **Credentials** tab
   - Copy the "Secret" value
   - Save this for Odoo configuration

### D. Configure Mattermost Client (GitLab Hack)

1. **Create Mattermost Client**
   - Go to **Clients**
   - Click "Create"
   - **Client ID**: `mattermost`
   - **Client Protocol**: `openid-connect`
   - Click "Save"

2. **Configure Client Settings**
   - **Name**: Mattermost Chat
   - **Enabled**: ON
   - **Access Type**: `confidential`
   - **Valid Redirect URIs**: `https://chat.insightpulseai.net/signup/gitlab/complete`
   - **Web Origins**: `https://chat.insightpulseai.net`

3. **Get Client Secret**
   - Go to **Credentials** tab
   - Copy the "Secret" value
   - Save this for Mattermost configuration

---

## 🔗 Service Integration

### A. Odoo Integration

1. **Install OAuth Module**
   ```bash
   # In Odoo, install auth_oauth module
   # Or use OCA auth_oidc if available for Odoo 18
   ```

2. **Configure OAuth Provider**
   - Go to **Settings > Users > OAuth Providers**
   - Create new provider:
     - **Name**: Keycloak
     - **Client ID**: `odoo`
     - **Client Secret**: [From Keycloak]
     - **Auth URL**: `https://auth.insightpulseai.net/realms/insightpulse/protocol/openid-connect/auth`
     - **Token URL**: `https://auth.insightpulseai.net/realms/insightpulse/protocol/openid-connect/token`
     - **UserInfo URL**: `https://auth.insightpulseai.net/realms/insightpulse/protocol/openid-connect/userinfo`
     - **Scope**: `openid profile email`

### B. Mattermost Integration (GitLab Hack)

1. **Configure GitLab Authentication**
   - Go to **System Console > Authentication > GitLab**
   - **Enable GitLab**: `true`
   - **Application ID**: `mattermost`
   - **Application Secret**: [From Keycloak]
   - **GitLab Site URL**: `https://auth.insightpulseai.net/realms/insightpulse`
   - **Token Endpoint**: `https://auth.insightpulseai.net/realms/insightpulse/protocol/openid-connect/token`
   - **User API Endpoint**: `https://auth.insightpulseai.net/realms/insightpulse/protocol/openid-connect/userinfo`

### C. Superset Integration

1. **Create Superset Client**
   - Follow similar steps as Odoo
   - Client ID: `superset`
   - Redirect URI: `https://superset.insightpulseai.net/*`

2. **Configure superset_config.py**
   ```python
   from flask_appbuilder.security.manager import AUTH_OID
   AUTH_TYPE = AUTH_OID
   OIDC_CLIENT_SECRETS = '/app/pythonpath/client_secret.json'
   ```

---

## 🎯 Identity Management Workflows

### User Onboarding
1. **Admin creates user in Keycloak**
2. **User receives temporary password**
3. **User logs in to any service (Odoo/Mattermost/Superset)**
4. **User changes password on first login**

### Single Sign-On Experience
- User visits Odoo → "Login with Keycloak" → Authenticates → Redirected back
- Same flow for Mattermost and Superset
- One password for entire ecosystem

### Password Management
- Users manage passwords in Keycloak
- Password policies enforced centrally
- Self-service password reset available

---

## 🔧 Advanced Configuration

### Traefik Routing
Ensure your Traefik configuration includes:
```yaml
labels:
  - "traefik.http.routers.keycloak.rule=Host(`auth.insightpulseai.net`)"
  - "traefik.http.routers.keycloak.entrypoints=websecure"
  - "traefik.http.routers.keycloak.tls.certresolver=myresolver"
```

### Database Optimization
```sql
-- Monitor Keycloak database performance
SELECT schemaname, tablename, seq_scan, seq_tup_read 
FROM pg_stat_user_tables 
WHERE schemaname = 'public' AND tablename LIKE 'keycloak%';
```

### Backup Strategy
```bash
# Include Keycloak in backups
docker exec odoo_prod_db_1 pg_dump -U odoo keycloak > keycloak_backup.sql

# Export realm configuration
docker exec keycloak /opt/keycloak/bin/kc.sh export --realm insightpulse --file /tmp/realm-export.json
```

---

## 🚨 Troubleshooting

### Common Issues

1. **Keycloak Won't Start**
   ```bash
   # Check logs
   docker compose -f docker-compose.prod.yml logs keycloak
   
   # Verify database connectivity
   docker exec odoo_prod_db_1 psql -U keycloak -d keycloak -c "\conninfo"
   ```

2. **OAuth Not Working**
   - Verify redirect URIs match exactly
   - Check client secret is correct
   - Validate Keycloak realm is accessible

3. **Mattermost GitLab Hack Issues**
   - Verify GitLab configuration matches exactly
   - Check Mattermost logs for OAuth errors
   - Validate Keycloak client configuration

### Health Checks
```bash
# Keycloak health
curl -s https://auth.insightpulseai.net/realms/insightpulse/.well-known/openid-configuration | jq .

# Database connectivity
docker exec odoo_prod_db_1 pg_isready -U keycloak -d keycloak

# Traefik routing
curl -H "Host: auth.insightpulseai.net" http://localhost
```

---

## 📈 Monitoring & Analytics

### Key Metrics to Track
- **User Login Success Rate**: OAuth authentication success
- **Service Integration Health**: Each service's OAuth status
- **User Activity**: Active users across services
- **Password Reset Requests**: Self-service usage

### Log Monitoring
```bash
# Monitor Keycloak logs
docker compose -f docker-compose.prod.yml logs -f keycloak

# Monitor OAuth integration logs
tail -f /var/log/odoo/odoo-server.log | grep oauth
```

---

## 🔄 Future Enhancements

### Phase 2: Advanced Identity Features
- Multi-factor authentication (MFA)
- Social login integration
- User self-registration
- Advanced password policies

### Phase 3: Enterprise Features
- LDAP/Active Directory integration
- Role-based access control (RBAC)
- Session management
- Audit logging

### Phase 4: Mobile Optimization
- Mobile app authentication
- Biometric authentication
- Offline access tokens

---

## ✅ Success Criteria

- [ ] Keycloak accessible at https://auth.insightpulseai.net
- [ ] InsightPulse realm created and configured
- [ ] Users can authenticate via Keycloak
- [ ] Odoo integrated with Keycloak OAuth
- [ ] Mattermost integrated via GitLab hack
- [ ] Single sign-on working across services
- [ ] Database backups include Keycloak data
- [ ] Monitoring and alerting configured

---

## 📞 Support & Maintenance

### Regular Maintenance Tasks
- **Weekly**: Database backups verification
- **Monthly**: Keycloak version updates
- **Quarterly**: User access reviews
- **Annually**: Security audit

### Emergency Contacts
- **Identity Management**: Admin team
- **OAuth Integration**: Development team
- **Database**: Ops team

---

**Last Updated**: 2025-11-24  
**Deployment Status**: Ready for Production
