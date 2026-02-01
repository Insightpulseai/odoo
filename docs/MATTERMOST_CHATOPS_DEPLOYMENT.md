# Mattermost ChatOps Deployment Guide
## Integration with Odoo ERP and AI Agents

**Target Environment**: Production Droplet (159.223.75.148)
**DNS**: `chat.insightpulseai.com` → 159.223.75.148

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
   chmod +x scripts/setup_mattermost_db.sh
   ./scripts/setup_mattermost_db.sh
   ```

3. **Verify Database Creation**
   ```bash
   docker exec odoo_prod_db_1 psql -U odoo -d postgres -c "\l"
   ```

### Phase 2: Mattermost Deployment

1. **Update docker-compose.prod.yml**
   ```bash
   # Add the Mattermost service block from deploy/mattermost-integration.yml
   # to your existing docker-compose.prod.yml
   ```

2. **Deploy Mattermost**
   ```bash
   docker compose -f docker-compose.prod.yml up -d mattermost
   ```

3. **Verify Deployment**
   ```bash
   docker compose -f docker-compose.prod.yml ps
   docker compose -f docker-compose.prod.yml logs mattermost
   ```

4. **Access Mattermost**
   - URL: https://chat.insightpulseai.com
   - Create admin account on first access

---

## 🔗 Integration Configuration

### A. Mattermost Webhook Setup

1. **Create Incoming Webhook**
   - Go to **System Console > Integrations > Incoming Webhooks**
   - Create webhook for `Finance` channel
   - Copy webhook URL: `https://chat.insightpulseai.com/hooks/xyz...`

2. **Create Outgoing Webhook for AI Agent**
   - Go to **System Console > Integrations > Outgoing Webhooks**
   - Trigger Words: `@agent`, `?`
   - Callback URL: `https://mattermost-rag-egb6n.ondigitalocean.app/webhook`
   - Copy generated token

### B. Odoo Integration

1. **Configure Automated Actions**
   - Go to **Settings > Technical > Automation > Automated Actions**
   - Create actions using the code from `scripts/odoo_mattermost_integration.py`

2. **Update Webhook URLs**
   - Replace `YOUR_WEBHOOK_ID` with actual Mattermost webhook URL
   - Test with sample purchase orders and expenses

### C. AI Agent Integration

1. **Configure mattermost-rag App**
   - Set environment variable: `MATTERMOST_TOKEN=your_generated_token`
   - Verify webhook endpoint responds correctly

---

## 🎯 ChatOps Workflows

### 1. Purchase Order Approvals
**Trigger**: PO state changes to 'to approve'
**Action**: Mattermost notification with approver tagging
**Result**: Faster approval cycles, reduced email dependency

### 2. Expense Approvals
**Trigger**: New expense submission
**Action**: Mattermost notification to finance team
**Result**: Real-time expense tracking

### 3. AI-Powered Assistance
**Trigger**: User types `@agent` or `?`
**Action**: Query mattermost-rag AI agent
**Result**: Context-aware responses based on company knowledge

---

## 🔧 Advanced Configuration

### Traefik Routing
Ensure your Traefik configuration includes:
```yaml
labels:
  - "traefik.http.routers.mattermost.rule=Host(`chat.insightpulseai.com`)"
  - "traefik.http.routers.mattermost.entrypoints=websecure"
  - "traefik.http.routers.mattermost.tls.certresolver=myresolver"
```

### Database Optimization
```sql
-- Monitor Mattermost database performance
SELECT schemaname, tablename, seq_scan, seq_tup_read
FROM pg_stat_user_tables
WHERE schemaname = 'public';
```

### Backup Strategy
```bash
# Include Mattermost in backups
docker exec odoo_prod_db_1 pg_dump -U odoo mattermost > mattermost_backup.sql
```

---

## 🚨 Troubleshooting

### Common Issues

1. **Mattermost Won't Start**
   ```bash
   # Check logs
   docker compose -f docker-compose.prod.yml logs mattermost

   # Verify database connectivity
   docker exec odoo_prod_db_1 psql -U mmuser -d mattermost -c "\conninfo"
   ```

2. **Webhooks Not Working**
   - Verify Mattermost URL is accessible
   - Check firewall rules for port 8065
   - Validate webhook URL in Odoo automated actions

3. **AI Agent Not Responding**
   - Verify outgoing webhook configuration
   - Check mattermost-rag app logs
   - Validate MATTERMOST_TOKEN environment variable

### Health Checks
```bash
# Mattermost health
curl -s https://chat.insightpulseai.com/api/v4/system/ping | jq .

# Database connectivity
docker exec odoo_prod_db_1 pg_isready -U mmuser -d mattermost

# Traefik routing
curl -H "Host: chat.insightpulseai.com" http://localhost
```

---

## 📈 Monitoring & Analytics

### Key Metrics to Track
- **Approval Response Time**: PO/expense approval cycle time
- **AI Agent Usage**: Number of @agent queries
- **User Engagement**: Active Mattermost users
- **Integration Health**: Webhook success rates

### Log Monitoring
```bash
# Monitor Mattermost logs
docker compose -f docker-compose.prod.yml logs -f mattermost

# Monitor Odoo integration logs
tail -f /var/log/odoo/odoo-server.log | grep mattermost
```

---

## 🔄 Future Enhancements

### Phase 2: Keycloak Integration
- Deploy Keycloak for unified authentication
- Configure OAuth for Odoo + Mattermost
- Single sign-on across all services

### Phase 3: Advanced ChatOps
- Custom slash commands for common tasks
- Integration with n8n workflows
- Advanced AI agent capabilities

### Phase 4: Mobile Optimization
- Mattermost mobile app configuration
- Push notifications for critical approvals
- Mobile-first approval workflows

---

## ✅ Success Criteria

- [ ] Mattermost accessible at https://chat.insightpulseai.com
- [ ] Purchase order approvals trigger Mattermost notifications
- [ ] Expense submissions notify finance team in Mattermost
- [ ] AI agent responds to @agent queries
- [ ] All services integrated with Traefik routing
- [ ] Database backups include Mattermost data
- [ ] Monitoring and alerting configured

---

## 📞 Support & Maintenance

### Regular Maintenance Tasks
- **Weekly**: Database backups verification
- **Monthly**: Mattermost version updates
- **Quarterly**: Integration health checks

### Emergency Contacts
- **Infrastructure**: Ops team
- **Odoo Integration**: Development team
- **AI Agent**: AI/ML team

---

**Last Updated**: 2025-11-24
**Deployment Status**: Ready for Production
