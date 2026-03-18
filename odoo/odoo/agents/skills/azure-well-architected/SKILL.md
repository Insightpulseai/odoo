---
name: azure-well-architected
description: Elite Azure Well-Architected Framework (WAF) standards for building reliable, secure, and optimized cloud workloads.
---

# Azure Well-Architected Framework (WAF)

This skill provides comprehensive guidance for designing, implementing, and reviewing Azure workloads based on the five pillars of the Microsoft Azure Well-Architected Framework.

## Core Pillars

### 1. Reliability

Ensures workloads meet uptime and recovery targets (SLO/SLA).

- **Redundancy**: Use Availability Zones and Multi-region deployments for business continuity.
- **Resiliency**: Implement retry patterns, circuit breakers, and bulkhead patterns.
- **Disaster Recovery**: Maintain a validated Multi-region DR plan with defined RTO/RPO.
- **Reliability Testing**: Perform Fault Injection (Chaos Engineering) and DR drills.

### 2. Security

Defends workloads against threats and ensures confidentiality, integrity, and availability.

- **Zero Trust**: Validate every request, use least-privileged access, and assume breach.
- **Data Protection**: Encrypt data at rest (CMK where possible) and in transit (TLS 1.2+).
- **Identity & Access**: Leverage Entra ID (formerly Azure AD) with MFA and Conditional Access.
- **Threat Modeling**: Conduct regular threat modeling for all system components.

### 3. Cost Optimization

Maximizes the value of every dollar spent on Azure.

- **Optimization Mindset**: Continuously monitor and refine resource usage.
- **Right-sizing**: Match resource capacity to demand; use Autoscale where applicable.
- **Commitments**: Leverage Azure Reservations and Savings Plans for predictable workloads.
- **Cost Observability**: Use Azure Cost Management and Tags for granular visibility.

### 4. Operational Excellence

Ensures smooth deployments and high observability.

- **Infrastructure as Code (IaC)**: Use Bicep, Terraform, or ARM Templates for all deployments.
- **Observability**: Use Azure Monitor, Application Insights, and Log Analytics for health checks.
- **Automation**: Automate CI/CD pipelines with integrated policy gates.
- **Software Quality**: Implement comprehensive unit, integration, and performance testing.

### 5. Performance Efficiency

Scales workloads to meet user demand efficiently.

- **Scaling**: Favor Horizontal Scaling (Scale-out) over Vertical Scaling (Scale-up).
- **Load Balancing**: Use Azure Front Door, Application Gateway, or Traffic Manager.
- **Performance Profiling**: Regular load testing and bottleneck analysis.
- **Data Patterns**: Use Caching (Azure Cache for Redis) and CDN for static assets.

## Specific Workload Guidance

- **AI/LLM Workloads**: Optimize GPU utilization, manage API rate limits (AOAI), and monitor prompt tokens for cost control.
- **SaaS Solutions**: Implement multi-tenant isolation, scalable data partitions, and metering/billing integration.
