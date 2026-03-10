# Automated Troubleshooting & Self-Healing Guide

## Overview

This guide documents the automated error handling, self-healing, and troubleshooting capabilities built into the Odoo deployment system.

## Core Components

### 1. Automated Error Handler (`scripts/auto_error_handler.sh`)

**Features:**
- Real-time error pattern detection
- Automated fixes for common issues
- Continuous health monitoring
- Configuration backup/restore
- Detailed logging and reporting

**Usage:**
```bash
# Detect and auto-fix errors
./scripts/auto_error_handler.sh detect

# Run health check
./scripts/auto_error_handler.sh health

# Start continuous monitoring
./scripts/auto_error_handler.sh monitor

# Backup configuration
./scripts/auto_error_handler.sh backup

# Fix specific cron field issues
./scripts/auto_error_handler.sh fix-cron
```

### 2. Error Pattern Database

The system maintains a JSON database of known error patterns with automated fixes:

```json
{
  "patterns": [
    {
      "regex": "Invalid field.*numbercall.*on model.*ir.cron",
      "type": "cron_field_deprecated",
      "severity": "high",
      "auto_fix": true,
      "fix_script": "fix_cron_fields",
      "description": "Odoo 18 removed numbercall field from ir.cron model"
    }
  ]
}
```

### 3. Health Monitoring System

**Checks Performed:**
- Odoo process status
- Database connectivity
- Recent error logs
- File permissions
- Service availability

## Common Error Scenarios & Auto-Fixes

### 1. Cron Field Deprecation (Odoo 18)

**Error Pattern:**
```
ValueError: Invalid field 'numbercall' on model 'ir.cron'
ValueError: Invalid field 'max_calls' on model 'ir.cron'
```

**Auto-Fix Action:**
- Automatically removes deprecated fields from cron XML files
- Processes all cron files in addons directory
- Creates backups before modifications

### 2. Database Connection Issues

**Error Pattern:**
```
Database connection failed
psycopg2.OperationalError
```

**Auto-Fix Action:**
- Restarts database service (Docker or systemd)
- Verifies connection recovery
- Logs restart attempts

### 3. Permission Errors

**Error Pattern:**
```
Permission denied
OSError: [Errno 13]
```

**Auto-Fix Action:**
- Sets proper file permissions for Odoo files
- Ensures script executability
- Maintains security standards

## Monitoring & Alerting

### Continuous Monitoring Mode

The system can run in continuous monitoring mode:
- Health checks every 5 minutes
- Automatic error detection and fixing
- Real-time logging to `/var/log/odoo_auto_heal.log`

### Integration Points

**With Existing Systems:**
- N8N workflows for notification
- Mattermost alerts for critical issues
- Health check endpoints for external monitoring
- CI/CD pipeline integration

## Manual Troubleshooting Procedures

### 1. Module Installation Issues

**Symptoms:**
- Module not found errors
- Dependency resolution failures

**Steps:**
1. Check module availability in addons directory
2. Verify dependencies in `__manifest__.py`
3. Run module update: `docker-compose exec odoo odoo -u module_name`
4. Check logs for specific error details

### 2. Database Migration Problems

**Symptoms:**
- Migration scripts failing
- Data integrity issues

**Steps:**
1. Backup current database
2. Check migration script logs
3. Run manual SQL verification
4. Use `scripts/run_odoo_migrations.sh` for controlled migration

### 3. Performance Issues

**Symptoms:**
- Slow response times
- High resource usage
- Timeout errors

**Steps:**
1. Check system resources (CPU, memory, disk)
2. Analyze database performance
3. Review Odoo worker configuration
4. Monitor network connectivity

## Self-Healing Capabilities

### Automated Recovery Procedures

1. **Configuration Drift Detection**
   - Monitors for unauthorized changes
   - Restores from known good configurations
   - Alerts on configuration changes

2. **Service Health Management**
   - Automatic service restarts
   - Dependency verification
   - Graceful degradation handling

3. **Data Integrity Protection**
   - Regular backup validation
   - Corruption detection
   - Automated recovery procedures

### Recovery Scenarios

**Scenario 1: Service Crash**
- Auto-detection via health checks
- Automatic service restart
- Root cause analysis logging

**Scenario 2: Configuration Corruption**
- Configuration backup restoration
- Validation of restored configuration
- Service restart with clean config

**Scenario 3: Database Issues**
- Connection pool management
- Query optimization
- Index maintenance

## Integration with Agent Framework

### Agent-Based Troubleshooting

The system integrates with the agent framework for advanced troubleshooting:

```yaml
# agents/procedures/EXECUTION_PROCEDURES.yaml
troubleshooting:
  - name: "auto_error_recovery"
    description: "Automated error detection and recovery"
    triggers:
      - "health_check_failed"
      - "error_pattern_detected"
    actions:
      - "run_auto_error_handler detect"
      - "notify_operations_team"
      - "escalate_if_unresolved"
```

### Knowledge Base Integration

Error patterns and solutions are integrated into the knowledge base:
- Automatic documentation of new error patterns
- Solution tracking and effectiveness metrics
- Continuous improvement of auto-fix capabilities

## Best Practices

### 1. Monitoring Configuration

- Set appropriate health check intervals
- Configure meaningful alert thresholds
- Maintain comprehensive logging
- Regular review of error patterns

### 2. Backup Strategy

- Regular configuration backups
- Test restoration procedures
- Version control for critical files
- Disaster recovery planning

### 3. Security Considerations

- Principle of least privilege for auto-fix scripts
- Audit logging for all automated actions
- Secure credential management
- Regular security reviews

## Advanced Features

### 1. Machine Learning Integration

**Planned Features:**
- Predictive error detection
- Anomaly detection in system behavior
- Automated pattern learning
- Intelligent fix recommendation

### 2. Multi-Environment Support

- Development environment testing
- Staging environment validation
- Production environment monitoring
- Environment-specific configurations

### 3. Performance Optimization

- Efficient pattern matching algorithms
- Optimized health check procedures
- Resource usage monitoring
- Scalable monitoring architecture

## Getting Help

### Support Channels

1. **Automated System**
   - Check `/var/log/odoo_auto_heal.log` for recent activity
   - Review error pattern database for known issues
   - Use health check functionality

2. **Manual Intervention**
   - Consult this troubleshooting guide
   - Check agent knowledge base
   - Contact operations team for critical issues

3. **Emergency Procedures**
   - Manual service restart procedures
   - Database recovery protocols
   - Rollback procedures

## Continuous Improvement

The automated troubleshooting system is designed for continuous improvement:

- **Feedback Loop**: All auto-fix actions are logged and reviewed
- **Pattern Updates**: New error patterns are added based on real incidents
- **Performance Metrics**: Success rates and effectiveness are tracked
- **Community Contributions**: Error patterns and fixes can be contributed by the team

---

*Last Updated: $(date)*
*System Version: Auto-Heal v1.0*
