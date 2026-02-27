import Docker from 'dockerode';

const docker = new Docker({ socketPath: '/var/run/docker.sock' });

export interface ContainerStatus {
  id: string;
  name: string;
  status: string;
  state: string;
  health?: string;
  uptime: string;
}

export async function getContainerStatus(containerId: string): Promise<ContainerStatus> {
  const container = docker.getContainer(containerId);
  const info = await container.inspect();
  
  return {
    id: info.Id.substring(0, 12),
    name: info.Name.replace(/^\//, ''),
    status: info.State.Status,
    state: info.State.Status,
    health: info.State.Health?.Status,
    uptime: info.State.StartedAt
  };
}

export async function restartContainer(containerId: string): Promise<void> {
  const container = docker.getContainer(containerId);
  await container.restart();
}

export async function streamLogs(containerId: string, tail = 100) {
  const container = docker.getContainer(containerId);
  const logs = await container.logs({
    stdout: true,
    stderr: true,
    tail,
    timestamps: true
  });
  
  return logs.toString('utf-8');
}

export async function execShell(containerId: string, command: string): Promise<string> {
  const container = docker.getContainer(containerId);
  const exec = await container.exec({
    Cmd: ['/bin/bash', '-c', command],
    AttachStdout: true,
    AttachStderr: true
  });

  const stream = await exec.start({ hijack: true, stdin: false });
  
  return new Promise((resolve, reject) => {
    let output = '';
    stream.on('data', (chunk: Buffer) => {
      output += chunk.toString('utf-8');
    });
    stream.on('end', () => resolve(output));
    stream.on('error', reject);
  });
}

export async function listContainersByProject(projectId: string) {
  const containers = await docker.listContainers({ all: true });
  
  return containers
    .filter(container => container.Labels['com.docker.compose.project'] === projectId)
    .map(container => ({
      id: container.Id.substring(0, 12),
      name: container.Names[0].replace(/^\//, ''),
      state: container.State,
      status: container.Status,
      image: container.Image
    }));
}
