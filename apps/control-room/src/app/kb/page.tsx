import { Suspense } from 'react';
import PageContainer from '@/components/layout/PageContainer';
import Card from '@/components/common/Card';

interface Space {
  id: string;
  name: string;
  description: string;
  slug: string;
  icon: string;
  artifact_count: number;
}

async function getSpaces(): Promise<Space[]> {
  // TODO: Fetch from Supabase
  return [
    {
      id: '1',
      name: 'Business Processes',
      description: 'Core business process documentation',
      slug: 'business-processes',
      icon: '📋',
      artifact_count: 24,
    },
    {
      id: '2',
      name: 'Data Models',
      description: 'Entity relationship and schema docs',
      slug: 'data-models',
      icon: '🗄️',
      artifact_count: 18,
    },
    {
      id: '3',
      name: 'Runbooks',
      description: 'Operational procedures and guides',
      slug: 'runbooks',
      icon: '📖',
      artifact_count: 12,
    },
  ];
}

function SpaceCard({ space }: { space: Space }) {
  return (
    <a href={`/kb/${space.slug}`}>
      <Card className="hover:border-blue-500 transition-colors cursor-pointer">
        <div className="flex items-start gap-4">
          <span className="text-4xl">{space.icon}</span>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-white">{space.name}</h3>
            <p className="text-gray-400 text-sm mt-1">{space.description}</p>
            <p className="text-blue-400 text-sm mt-2">
              {space.artifact_count} artifacts
            </p>
          </div>
        </div>
      </Card>
    </a>
  );
}

async function SpacesList() {
  const spaces = await getSpaces();

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {spaces.map((space) => (
        <SpaceCard key={space.id} space={space} />
      ))}
    </div>
  );
}

export default function KnowledgeBasePage() {
  return (
    <PageContainer
      title="Knowledge Base"
      description="Explore documentation, processes, and runbooks"
    >
      <div className="mb-6 flex justify-between items-center">
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Search artifacts..."
            className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 w-64"
          />
          <select className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white">
            <option value="">All Personas</option>
            <option value="admin">Admin</option>
            <option value="finance">Finance</option>
            <option value="operations">Operations</option>
            <option value="hr">HR</option>
          </select>
        </div>
        <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg">
          + New Space
        </button>
      </div>

      <Suspense fallback={<div className="text-gray-400">Loading spaces...</div>}>
        <SpacesList />
      </Suspense>
    </PageContainer>
  );
}
