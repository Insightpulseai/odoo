import { Suspense } from 'react';
import PageContainer from '@/components/layout/PageContainer';
import Card from '@/components/common/Card';
import Badge from '@/components/common/Badge';

interface Job {
  id: string;
  reference: string;
  title: string;
  status: 'new' | 'assigned' | 'dispatched' | 'in_transit' | 'on_site' | 'in_progress' | 'completed';
  priority: number;
  customer_name: string;
  customer_address: string;
  scheduled_start: string;
  technician_name?: string;
}

interface Technician {
  id: string;
  name: string;
  status: 'available' | 'busy' | 'offline';
  current_job?: string;
  jobs_today: number;
}

async function getJobs(): Promise<Job[]> {
  // TODO: Fetch from Supabase
  return [
    {
      id: '1',
      reference: 'FSM-20240115-0001',
      title: 'HVAC Maintenance',
      status: 'assigned',
      priority: 3,
      customer_name: 'Acme Corp',
      customer_address: '123 Main St, Suite 100',
      scheduled_start: '2024-01-15T09:00:00',
      technician_name: 'John Smith',
    },
    {
      id: '2',
      reference: 'FSM-20240115-0002',
      title: 'Emergency Repair',
      status: 'new',
      priority: 1,
      customer_name: 'Tech Industries',
      customer_address: '456 Oak Ave',
      scheduled_start: '2024-01-15T10:30:00',
    },
  ];
}

async function getTechnicians(): Promise<Technician[]> {
  return [
    { id: '1', name: 'John Smith', status: 'busy', current_job: 'FSM-0001', jobs_today: 3 },
    { id: '2', name: 'Jane Doe', status: 'available', jobs_today: 2 },
    { id: '3', name: 'Bob Wilson', status: 'offline', jobs_today: 0 },
  ];
}

const statusColors: Record<string, 'default' | 'warning' | 'success' | 'error' | 'info'> = {
  new: 'warning',
  assigned: 'info',
  dispatched: 'info',
  in_transit: 'info',
  on_site: 'warning',
  in_progress: 'warning',
  completed: 'success',
};

function JobCard({ job }: { job: Job }) {
  return (
    <Card className="hover:border-gray-600 transition-colors">
      <div className="flex justify-between items-start">
        <div>
          <p className="text-gray-500 text-xs">{job.reference}</p>
          <h3 className="text-white font-medium">{job.title}</h3>
          <p className="text-gray-400 text-sm">{job.customer_name}</p>
          <p className="text-gray-500 text-xs">{job.customer_address}</p>
        </div>
        <div className="text-right">
          <Badge variant={statusColors[job.status]}>{job.status}</Badge>
          {job.priority === 1 && (
            <p className="text-red-400 text-xs mt-1">🚨 High Priority</p>
          )}
        </div>
      </div>
      {job.technician_name && (
        <p className="text-blue-400 text-sm mt-2">
          👤 {job.technician_name}
        </p>
      )}
    </Card>
  );
}

function TechnicianRow({ tech }: { tech: Technician }) {
  const statusColors: Record<string, string> = {
    available: 'bg-green-500',
    busy: 'bg-yellow-500',
    offline: 'bg-gray-500',
  };

  return (
    <div className="flex items-center justify-between py-2 border-b border-gray-700 last:border-0">
      <div className="flex items-center gap-3">
        <div className={`w-2 h-2 rounded-full ${statusColors[tech.status]}`} />
        <span className="text-white">{tech.name}</span>
      </div>
      <div className="text-gray-400 text-sm">
        {tech.jobs_today} jobs today
      </div>
    </div>
  );
}

async function DispatchBoard() {
  const [jobs, technicians] = await Promise.all([getJobs(), getTechnicians()]);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 space-y-4">
        <h2 className="text-lg font-semibold text-white">Active Jobs</h2>
        {jobs.map((job) => (
          <JobCard key={job.id} job={job} />
        ))}
      </div>

      <div>
        <h2 className="text-lg font-semibold text-white mb-4">Technicians</h2>
        <Card>
          {technicians.map((tech) => (
            <TechnicianRow key={tech.id} tech={tech} />
          ))}
        </Card>
      </div>
    </div>
  );
}

export default function FSMPage() {
  return (
    <PageContainer
      title="Field Service"
      description="Dispatch board and job management"
    >
      <div className="mb-6 flex justify-between items-center">
        <div className="flex gap-2">
          <select className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white">
            <option value="">All Status</option>
            <option value="new">New</option>
            <option value="assigned">Assigned</option>
            <option value="in_progress">In Progress</option>
          </select>
          <select className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white">
            <option value="">All Technicians</option>
          </select>
        </div>
        <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg">
          + New Job
        </button>
      </div>

      <Suspense fallback={<div className="text-gray-400">Loading dispatch board...</div>}>
        <DispatchBoard />
      </Suspense>
    </PageContainer>
  );
}
