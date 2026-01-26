# EE Parity Audit

- Repo: `jgtolentino/odoo-ce`
- Commit: `1d63f114a331ffbe8459e67abd40a5a6dc08ccf0`
- Branch: `claude/github-odoo-governance-H3zwb`
- Generated: 2026-01-26 04:56:50 UTC

## Task Progress
- Total tasks: **233**
- Done: **6**
- Remaining: **227**
- Completion: **2.58%**

## Runnable Gates
| Gate | Status |
|------|--------|
| require_runnable_slice.sh | **pass** |
| check_ipai_foundation.sh | **pass** |

## Inventory
| Item | Value |
|------|-------|
| ipai manifests found | **23** |
| ee-parity-gate workflow | **yes** |

## Blockers
- None detected by heuristic rules.

## Verification Commands
```bash
./scripts/parity/audit_ee_parity.sh
cat reports/parity/ee_parity_audit.md
```

---

## Sample Completed Tasks (first 200)
```
10:- ✅ Create `ipai_foundation` module with `ipai.workspace` model
11:- ✅ Create parity gate scripts (`require_runnable_slice.sh`, `check_ipai_foundation.sh`)
12:- ✅ Add parity validation steps to `ee-parity-gate.yml` workflow
56:- ✅ Add parity gate to CI workflow (require_runnable_slice + check_ipai_foundation)
63:- ✅ Verify `hr_expense` installed
103:- ✅ `ipai_finance_bir_compliance` module exists
```

## Sample Remaining Tasks (first 200)
```
15:- ⬜ Create `ops` schema
16:- ⬜ Create `agent_runs` table with indexes
17:- ⬜ Create `agent_audit_log` table
18:- ⬜ Create `tool_permissions` table
19:- ⬜ Create `portal_sessions` table
20:- ⬜ Configure RLS policies
21:- ⬜ Create Edge Functions for portal API
22:- ⬜ Test schema with sample data
25:- ⬜ Deploy n8n instance (compose)
26:- ⬜ Configure Odoo XML-RPC credentials
27:- ⬜ Configure Supabase credentials
28:- ⬜ Create webhook receiver templates
29:- ⬜ Create base error handling workflow
30:- ⬜ Document workflow patterns
33:- ⬜ Create `ipai_design_system` module scaffold
34:- ⬜ Extract Odoo SCSS variables
35:- ⬜ Create CSS custom properties export
36:- ⬜ Create JSON token export
37:- ⬜ Apply tokens to Odoo theme
38:- ⬜ Document token usage
41:- ⬜ Register `odoo_search` tool
42:- ⬜ Register `odoo_create` tool
43:- ⬜ Register `odoo_update` tool
44:- ⬜ Register `supabase_query` tool
45:- ⬜ Implement permission checking
46:- ⬜ Implement audit logging
47:- ⬜ Write tool tests
50:- ⬜ Create `check_expense_parity.sh`
51:- ⬜ Create `check_procurement_parity.sh`
52:- ⬜ Create `check_equipment_parity.sh`
53:- ⬜ Create `check_project_parity.sh`
54:- ⬜ Create `check_copilot_parity.sh`
55:- ⬜ Create `check_bi_parity.sh`
64:- ⬜ Configure expense categories (PH-specific)
65:- ⬜ Create `ipai.expense.policy` model
66:- ⬜ Implement policy rule engine
67:- ⬜ Create policy violation alerts
68:- ⬜ Configure multi-level approval
69:- ⬜ Test approval delegation
72:- ⬜ Create `ipai.travel.request` model
73:- ⬜ Create travel request form view
74:- ⬜ Link travel to expense reports
75:- ⬜ Implement travel approval workflow
76:- ⬜ Test budget tracking
79:- ⬜ Select OCR provider (Google/AWS/Azure)
80:- ⬜ Create `ipai_expense_ocr` module
81:- ⬜ Build OCR API integration
82:- ⬜ Create n8n `expense_ocr_ingest` workflow
83:- ⬜ Map OCR fields to expense lines
84:- ⬜ Test accuracy
87:- ⬜ Install `account_payment_group`
88:- ⬜ Configure payment methods
89:- ⬜ Create batch grouping logic
90:- ⬜ Create n8n `reimbursement_batch` workflow
91:- ⬜ Test GL posting
92:- ⬜ Create reimbursement reports
95:- ⬜ Create PWA project structure
96:- ⬜ Implement expense capture form
97:- ⬜ Implement camera capture
98:- ⬜ Implement offline storage
99:- ⬜ Create sync mechanism
100:- ⬜ Test offline/online scenarios
104:- ⬜ Configure 2307 withholding tax
105:- ⬜ Create SAWT generation
106:- ⬜ Create QAP generation
107:- ⬜ Test against BIR formats
108:- ⬜ Document compliance procedures
115:- ⬜ Add KYC document fields to partner
116:- ⬜ Create supplier status workflow
117:- ⬜ Implement supplier scoring
118:- ⬜ Create supplier dashboard
119:- ⬜ Test KYC document tracking
122:- ⬜ Install `purchase_requisition`
123:- ⬜ Configure requisition categories
124:- ⬜ Create RFQ template
125:- ⬜ Implement vendor selection
126:- ⬜ Test requisition to PO flow
129:- ⬜ Create `ipai.approval.matrix` model
130:- ⬜ Implement amount thresholds
131:- ⬜ Implement category rules
132:- ⬜ Implement cost center rules
133:- ⬜ Create n8n `po_approval` workflow
134:- ⬜ Test escalation
137:- ⬜ Configure goods receipt
138:- ⬜ Install `purchase_stock_picking_invoice_link`
139:- ⬜ Implement 3-way match logic
140:- ⬜ Create n8n `invoice_match` workflow
141:- ⬜ Handle match exceptions
142:- ⬜ Test matching scenarios
145:- ⬜ Create Next.js portal project
146:- ⬜ Implement Supabase auth
147:- ⬜ Create PO list view
148:- ⬜ Create PO detail view
149:- ⬜ Create invoice submission form
150:- ⬜ Test portal workflow
153:- ⬜ Install `auditlog` OCA module
154:- ⬜ Configure audited models
155:- ⬜ Create audit reports
156:- ⬜ Test audit completeness
157:- ⬜ Document retention policy
164:- ⬜ Create equipment product category
165:- ⬜ Configure equipment attributes
166:- ⬜ Create equipment locations
167:- ⬜ Import equipment master data
168:- ⬜ Test search and filtering
171:- ⬜ Create `ipai.equipment.booking` model
172:- ⬜ Create calendar view
173:- ⬜ Implement conflict detection
174:- ⬜ Create booking form
175:- ⬜ Create n8n `booking_confirm` workflow
176:- ⬜ Test booking scenarios
179:- ⬜ Configure internal transfer route
180:- ⬜ Create check-out wizard
181:- ⬜ Create check-in wizard
182:- ⬜ Create `ipai.equipment.condition` model
183:- ⬜ Create `ipai.custody.log` model
184:- ⬜ Create n8n `checkout_notify` workflow
187:- ⬜ Install `stock_barcodes`
188:- ⬜ Generate QR codes for equipment
189:- ⬜ Create mobile scanning view
190:- ⬜ Test QR workflows
193:- ⬜ Install `maintenance` module
194:- ⬜ Link to equipment products
195:- ⬜ Create maintenance schedules
196:- ⬜ Create n8n `maintenance_schedule` workflow
197:- ⬜ Test maintenance workflow
204:- ⬜ Configure project stages
205:- ⬜ Install `project_task_dependency`
206:- ⬜ Install `project_task_checklist`
207:- ⬜ Configure task templates
208:- ⬜ Test Kanban board
211:- ⬜ Create `ipai.plan.template` model
212:- ⬜ Create template items model
213:- ⬜ Implement template instantiation
214:- ⬜ Create n8n `plan_instantiate` workflow
215:- ⬜ Test template scenarios
218:- ⬜ Install `project_task_recurrent`
219:- ⬜ Configure recurrence patterns
220:- ⬜ Create n8n `task_generate` workflow
221:- ⬜ Test recurrence generation
224:- ⬜ Create n8n `task_assign` workflow
225:- ⬜ Create n8n `due_reminder` workflow
226:- ⬜ Configure email templates
227:- ⬜ Configure Mattermost integration
228:- ⬜ Test notification delivery
235:- ⬜ Select embedding model
236:- ⬜ Create document ingestion pipeline
237:- ⬜ Index Odoo records
238:- ⬜ Index documentation
239:- ⬜ Test retrieval accuracy
242:- ⬜ Create chat UI component
243:- ⬜ Implement conversation state
244:- ⬜ Create prompt templates
245:- ⬜ Implement response streaming
246:- ⬜ Test query scenarios
249:- ⬜ Register `odoo_action` tool
250:- ⬜ Register `docs_search` tool
251:- ⬜ Register `send_notification` tool
252:- ⬜ Register `request_approval` tool
253:- ⬜ Implement error recovery
254:- ⬜ Test tool execution
257:- ⬜ Implement write confirmation flow
258:- ⬜ Implement approval gating
259:- ⬜ Create pending approvals view
260:- ⬜ Create approval workflow
261:- ⬜ Test sensitive actions
264:- ⬜ Log all tool calls to Supabase
265:- ⬜ Generate explanations
266:- ⬜ Create audit dashboard
267:- ⬜ Create explanation view
268:- ⬜ Test audit completeness
271:- ⬜ Configure tool permissions per role
272:- ⬜ Implement permission checking
273:- ⬜ Test role scenarios
274:- ⬜ Document role capabilities
281:- ⬜ Create `analytics` schema
282:- ⬜ Design expense facts/dimensions
283:- ⬜ Design procurement facts/dimensions
284:- ⬜ Design equipment facts/dimensions
285:- ⬜ Design project facts/dimensions
286:- ⬜ Create ETL jobs
287:- ⬜ Test data freshness
290:- ⬜ Create database connection
291:- ⬜ Import datasets
292:- ⬜ Configure RLS rules
293:- ⬜ Certify datasets
294:- ⬜ Test permissions
297:- ⬜ Create expense analytics dashboard
298:- ⬜ Create procurement analytics dashboard
299:- ⬜ Create equipment utilization dashboard
300:- ⬜ Create project workload dashboard
301:- ⬜ Create executive summary dashboard
302:- ⬜ Test all dashboards
305:- ⬜ Configure guest tokens
306:- ⬜ Create Odoo embed action
307:- ⬜ Test embedded dashboards
308:- ⬜ Document embedding
315:- ⬜ Expense end-to-end test
316:- ⬜ Procurement end-to-end test
317:- ⬜ Equipment end-to-end test
```
