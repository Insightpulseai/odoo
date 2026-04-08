import { randomUUID } from 'crypto';

// Replicate branded type since we are disconnected from build momentarily
type CorrelationId = string;

export class CorrelationContext {
  private tree: Map<CorrelationId, CorrelationId[]> = new Map();

  createRoot(): CorrelationId {
    const id = randomUUID() as CorrelationId;
    this.tree.set(id, []);
    return id;
  }

  createChild(parent: CorrelationId): CorrelationId {
    const child = randomUUID() as CorrelationId;
    if (!this.tree.has(parent)) {
      this.tree.set(parent, []);
    }
    this.tree.get(parent)!.push(child);
    this.tree.set(child, []);
    return child;
  }

  getTree(root: CorrelationId): object {
    const buildTree = (nodeId: CorrelationId): any => {
      const children = this.tree.get(nodeId) || [];
      return {
        id: nodeId,
        children: children.map(buildTree)
      };
    };
    return buildTree(root);
  }
}
