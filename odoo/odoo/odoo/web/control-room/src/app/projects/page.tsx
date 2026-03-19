'use client';

import { useState, useEffect } from 'react';
import { Search, Filter } from 'lucide-react';
import { PageContainer, PageContent } from '@/components/layout/PageContainer';
import { Header } from '@/components/layout/Header';
import { Card } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { ProjectsTable } from '@/components/tables/ProjectsTable';
import type { Project, PaginatedResponse } from '@/types/api';

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  const [priorityFilter, setPriorityFilter] = useState<string | null>(null);

  const fetchProjects = async () => {
    setIsRefreshing(true);
    try {
      const params = new URLSearchParams();
      params.set('page', String(page));
      params.set('pageSize', String(pageSize));
      if (search) params.set('search', search);
      if (statusFilter) params.set('status', statusFilter);
      if (priorityFilter) params.set('priority', priorityFilter);

      const res = await fetch(`/api/projects?${params}`);
      if (res.ok) {
        const data: PaginatedResponse<Project> = await res.json();
        setProjects(data.data);
        setTotal(data.total);
      }
    } catch (error) {
      console.error('Failed to fetch projects:', error);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, [page, statusFilter, priorityFilter]);

  const handleSearch = () => {
    setPage(1);
    fetchProjects();
  };

  const handleProjectClick = (project: Project) => {
    // Navigate to project detail or open modal
    console.log('Selected project:', project);
  };

  const statuses = ['Planning', 'In Progress', 'Completed', 'On Hold'];
  const priorities = ['High', 'Medium', 'Low'];

  return (
    <PageContainer>
      <Header
        title="Projects"
        subtitle="Project portfolio management"
        onRefresh={fetchProjects}
        isRefreshing={isRefreshing}
      />

      <PageContent>
        {/* Search and Filters */}
        <Card className="mb-6">
          <div className="flex flex-wrap items-center gap-4">
            {/* Search */}
            <div className="flex-1 min-w-[200px]">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-surface-400" />
                <input
                  type="text"
                  placeholder="Search projects..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                  className="w-full pl-10 pr-4 py-2 bg-surface-800 border border-surface-700 rounded-md text-white placeholder-surface-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
            </div>

            {/* Status Filter */}
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-surface-400" />
              <select
                value={statusFilter || ''}
                onChange={(e) => {
                  setStatusFilter(e.target.value || null);
                  setPage(1);
                }}
                className="bg-surface-800 border border-surface-700 rounded-md px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">All Statuses</option>
                {statuses.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>

            {/* Priority Filter */}
            <div>
              <select
                value={priorityFilter || ''}
                onChange={(e) => {
                  setPriorityFilter(e.target.value || null);
                  setPage(1);
                }}
                className="bg-surface-800 border border-surface-700 rounded-md px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">All Priorities</option>
                {priorities.map((p) => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
            </div>

            <Button onClick={handleSearch}>Search</Button>
          </div>
        </Card>

        {/* Projects Table */}
        <ProjectsTable
          projects={projects}
          total={total}
          page={page}
          pageSize={pageSize}
          loading={loading}
          onPageChange={setPage}
          onProjectClick={handleProjectClick}
        />
      </PageContent>
    </PageContainer>
  );
}
