import { EvalMetricsAggregator } from '../evals/metrics.js';
import { AgentRegistry } from '../registry/registry.js';
import { registryHealth } from '../registry/registry-health.js';
import * as http from 'http';

export class FoundryExporter {
  private aggregator = new EvalMetricsAggregator();
  private registry = new AgentRegistry();

  getMetricsPayload(): string {
    const allAgents = this.registry.list();
    const health = registryHealth(this.registry);
    
    let prometheusDoc = `# HELP agent_registry_health System health status (1=healthy, 0=degraded)\n`;
    prometheusDoc += `# TYPE agent_registry_health gauge\n`;
    prometheusDoc += `agent_registry_health ${health.status === 'healthy' ? 1 : 0}\n\n`;

    prometheusDoc += `# HELP agent_count Total registered agents\n`;
    prometheusDoc += `# TYPE agent_count gauge\n`;
    prometheusDoc += `agent_count ${health.totalAgents}\n\n`;

    prometheusDoc += `# HELP agent_eval_score Latest evaluation score per agent\n`;
    prometheusDoc += `# TYPE agent_eval_score gauge\n`;

    for (const agent of allAgents) {
      const stats = this.aggregator.getMetrics(agent.data.id);
      prometheusDoc += `agent_eval_score{agent_id="${agent.data.id}",domain="${agent.data.domain}"} ${stats.averageScore}\n`;
    }

    return prometheusDoc;
  }

  startServer(port: number = 9091) {
    http.createServer((req, res) => {
      if (req.url === '/metrics') {
        res.writeHead(200, { 'Content-Type': 'text/plain' });
        res.end(this.getMetricsPayload());
      } else {
        res.writeHead(404);
        res.end();
      }
    }).listen(port, () => {
      console.log(`[FoundryExporter] Prometheus metrics running on :${port}/metrics`);
    });
  }
}
