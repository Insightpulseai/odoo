# November 2025 PPM Playbook - Go-Live Summary

**Date**: 24 November 2025
**Status**: ✅ **Ready for Go-Live**

---

## 🎯 Current Deployment Status

### ✅ Repository Implementation Complete
- **PPM Monthly Close Module**: Available for installation
- **November 2025 Schedule**: Pre-configured for immediate start (24 Nov 2025)
- **10 Agency Templates**: RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB
- **Automated Workflow**: Owner → Reviewer → Approver with daily reminders
- **Progress Tracking**: Real-time monitoring with ECharts dashboard

### ✅ Odoo Projects Already Active
- **Month-End Closing** (ID: 19) - ✅ Active
- **BIR Tax Filing 2025-2026** (ID: 20) - ✅ Active
- **Tax Filing & BIR Compliance** (ID: 10) - ✅ Active

### 📋 Go-Live Checklist Status

- [x] November 2025 close PPM playbook aligned with live Odoo boards
- [x] Repository implementation complete
- [x] Odoo projects verified and active
- [ ] Install PPM Monthly Close Module via Odoo UI
- [ ] Verify template data and update employee codes
- [ ] Create November 2025 close schedule
- [ ] Share PPM playbook with stakeholders

---

## 🗓️ Key Dates for November 2025

| Date | Activity | Status |
|------|----------|--------|
| **24 Nov 2025 (Mon)** | Prep Start (S) | ✅ TODAY |
| **25 Nov 2025 (Tue)** | Review Due (AM) | ⏳ Upcoming |
| **25 Nov 2025 (Tue)** | Approval Due (EOD) | ⏳ Upcoming |
| **28 Nov 2025 (Fri)** | Month End (C) | ⏳ Upcoming |

---

## 🚀 Immediate Next Steps (Manual Installation Required)

### 1. Install PPM Monthly Close Module
```bash
# Navigate to: https://erp.insightpulseai.com
# Login with admin credentials
# Apps → Update Apps List → Search "PPM Monthly Close" → Install
```

### 2. Verify Installation
- New menu "Monthly Close" appears in top navigation
- 3 submenus: Close Schedules, Tasks, Templates
- 10 pre-configured templates for all agencies

### 3. Configure November 2025 Close
1. **Monthly Close → Close Schedules**
2. Click **Create**
3. Set **Close Month**: `2025-11-01`
4. Click **Save**
5. Click **Generate Tasks** button
6. Click **Start Close Process** button

### 4. Update Employee Codes
- Edit each template to replace placeholder codes with real Odoo user logins
- Assign actual task owners, reviewers, and approvers

---

## 👥 Stakeholder Communication

### Target Groups:
- **CKVC, RIM, BOM, JPAL, LAS, RMQB, JAP, JRMO**

### Communication Template:
```
Subject: November 2025 Close PPM - Go-Live

We are now following the November 2025 Close PPM playbook.

Please check your Odoo board for assigned tasks and deadlines:
- Month-End Closing project
- BIR Tax Filing 2025-2026 project

Key dates:
- Prep Start: Today (24 Nov)
- Review Due: Tomorrow AM (25 Nov)
- Approval Due: Tomorrow EOD (25 Nov)

Documentation: [PPM Playbook Link]
```

---

## 📚 Documentation References

- **PPM Playbook**: `addons/ipai_ppm_monthly_close/INSTALL_NOVEMBER_2025.md`
- **Module Documentation**: `addons/ipai_ppm_monthly_close/README.md`
- **Installation Guide**: `install_ppm_monthly_close.sh`
- **Deployment Status**: `DEPLOYMENT_STATUS.md`

---

## 🎯 Success Metrics

- **100% Task Completion**: All 10 agency tasks completed by 25 Nov EOD
- **Real-time Progress**: Dashboard showing live progress tracking
- **Stakeholder Adoption**: All agencies using the new PPM workflow
- **Zero Manual Spreadsheets**: Complete transition from manual processes

---

## 🔧 Support & Troubleshooting

### Common Issues:
- **Module not visible**: Restart Odoo container and update apps list
- **Wrong dates**: Verify close_month is set to `2025-11-01`
- **No notifications**: Check cron jobs in Settings → Technical → Scheduled Actions

### Contact:
- **Issues**: https://github.com/jgtolentino/odoo-ce/issues
- **Email**: jgtolentino_rn@yahoo.com

---

**Last Updated**: 24 November 2025
**Next Review**: After module installation
