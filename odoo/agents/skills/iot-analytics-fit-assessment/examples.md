# iot-analytics-fit-assessment — Examples

## Example 1: OUT_OF_SCOPE — Marketing Dashboard

**Input**: "We need real-time marketing analytics. Campaign data from Google Ads, Meta, and TikTok APIs refreshed every 15 minutes with anomaly detection on spend and conversions."

**Output**:

Verdict: OUT_OF_SCOPE

Justification:
- Data sources are SaaS APIs (Google Ads, Meta, TikTok), not IoT devices
- "Real-time" means 15-minute refresh, which is micro-batch territory
- Anomaly detection on marketing metrics does not require streaming ingestion
- No device management, no sub-second latency, no high-volume telemetry

Alternative:
- Recommended approach: Scheduled micro-batch pipeline (Databricks Jobs every 15 minutes)
- Why: API-sourced data with 15-minute granularity is perfectly served by scheduled jobs writing to Delta Lake. Anomaly detection runs as a post-ingestion step.

---

## Example 2: IN_SCOPE — Manufacturing Floor Monitoring

**Input**: "500 machines on the factory floor, each emitting 10 sensor readings per second. Need sub-second anomaly detection to trigger maintenance alerts. Device firmware updates managed centrally."

**Output**:

Verdict: IN_SCOPE

Justification:
- Physical devices (500 machines) generating telemetry: strong IoT signal
- 500 machines x 10 readings/sec = 5,000 events/sec sustained: borderline but with growth headroom
- Sub-second anomaly detection: genuine streaming latency requirement
- Device firmware management: IoT Hub device management needed

Recommendation: Azure IoT Hub for device management and ingestion, Azure Data Explorer for time-series analytics and anomaly detection, Databricks for batch retraining of anomaly detection models.

---

## Example 3: CONDITIONAL — Smart Building Energy

**Input**: "Smart building with 200 sensors measuring temperature, humidity, and occupancy. Want to optimize HVAC in near-real-time. Also need monthly energy reports."

**Output**:

Verdict: CONDITIONAL

Justification:
- Physical sensors (200): IoT signal present but small scale
- "Near-real-time" HVAC optimization: could be 1-minute control loops (streaming) or 5-minute adjustments (micro-batch)
- 200 sensors x ~1 reading/min = ~3 events/sec: low volume, does not require streaming infrastructure
- Monthly energy reports: clearly batch

Clarification needed:
- What latency is acceptable for HVAC adjustments? (seconds vs. minutes)
- Are sensors managed centrally or independently?
- Is the sensor count expected to grow significantly?

If latency is minutes: OUT_OF_SCOPE — use micro-batch with Databricks Jobs.
If latency is seconds with growth to 1,000+ sensors: IN_SCOPE — use IoT Hub + streaming.

---

## Example 4: OUT_OF_SCOPE — CRM Event Processing

**Input**: "We want real-time processing of CRM events (lead creation, deal stage changes, email opens) for instant lead scoring and routing."

**Output**:

Verdict: OUT_OF_SCOPE

Justification:
- Data sources are CRM application events, not IoT devices
- "Real-time" means event-driven processing, not streaming telemetry
- Volume is low (CRM events are typically < 100/second even for large orgs)
- No device management, no sensor data, no time-series analytics

Alternative:
- Recommended approach: Change Data Capture (CDC) from CRM database or webhook-based event processing
- Why: CRM events are application-level events best handled by CDC, webhooks, or message queues (Azure Service Bus). IoT infrastructure would be massive over-engineering.
