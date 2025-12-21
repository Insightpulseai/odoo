'use client';

import { useState, useEffect } from 'react';
import { DollarSign, Shield, Activity, Settings, Zap, ExternalLink } from 'lucide-react';
import { PageContainer, PageContent } from '@/components/layout/PageContainer';
import { Header } from '@/components/layout/Header';
import { Card, CardHeader } from '@/components/common/Card';
import { Badge, StatusBadge } from '@/components/common/Badge';
import { Button } from '@/components/common/Button';
import { DataTable } from '@/components/tables/DataTable';
import { CategoryPieChart } from '@/components/charts/BudgetChart';
import type { AdvisorRecommendation } from '@/types/api';

const categoryIcons = {
  Cost: DollarSign,
  Security: Shield,
  Reliability: Activity,
  OperationalExcellence: Settings,
  Performance: Zap,
};

const categoryColors = {
  Cost: 'text-emerald-400',
  Security: 'text-red-400',
  Reliability: 'text-blue-400',
  OperationalExcellence: 'text-amber-400',
  Performance: 'text-purple-400',
};

export default function AdvisorPage() {
  const [recommendations, setRecommendations] = useState<AdvisorRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [categoryFilter, setCategoryFilter] = useState<string | null>(null);

  const fetchRecommendations = async () => {
    setIsRefreshing(true);
    try {
      const params = new URLSearchParams();
      if (categoryFilter) params.set('category', categoryFilter);
      params.set('dismissed', 'false');

      const res = await fetch(`/api/advisor/recommendations?${params}`);
      if (res.ok) {
        const data = await res.json();
        setRecommendations(data.recommendations || []);
      }
    } catch (error) {
      console.error('Failed to fetch recommendations:', error);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, [categoryFilter]);

  // Calculate totals by category
  const byCategoryCount = recommendations.reduce((acc, rec) => {
    acc[rec.category] = (acc[rec.category] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const totalSavings = recommendations
    .filter(r => r.category === 'Cost' && r.estimatedSavings)
    .reduce((sum, r) => sum + (r.estimatedSavings || 0), 0);

  const pieData = Object.entries(byCategoryCount).map(([name, value]) => ({
    name,
    value,
  }));

  const columns = [
    {
      key: 'category',
      header: 'Category',
      render: (rec: AdvisorRecommendation) => {
        const Icon = categoryIcons[rec.category];
        return (
          <div className="flex items-center gap-2">
            <Icon className={`h-4 w-4 ${categoryColors[rec.category]}`} />
            <span>{rec.category}</span>
          </div>
        );
      },
    },
    {
      key: 'impact',
      header: 'Impact',
      render: (rec: AdvisorRecommendation) => (
        <StatusBadge status={rec.impact} />
      ),
    },
    {
      key: 'shortDescription',
      header: 'Recommendation',
      render: (rec: AdvisorRecommendation) => (
        <div>
          <p className="text-sm font-medium">{rec.shortDescription}</p>
          <p className="text-xs text-surface-400">{rec.impactedResource}</p>
        </div>
      ),
    },
    {
      key: 'resourceType',
      header: 'Resource Type',
      render: (rec: AdvisorRecommendation) => (
        <Badge variant="neutral">{rec.resourceType}</Badge>
      ),
    },
    {
      key: 'estimatedSavings',
      header: 'Est. Savings',
      render: (rec: AdvisorRecommendation) => (
        rec.estimatedSavings ? (
          <span className="text-emerald-400 font-mono">
            ${rec.estimatedSavings.toLocaleString()}/{rec.currency === 'USD' ? 'mo' : 'yr'}
          </span>
        ) : (
          <span className="text-surface-400">-</span>
        )
      ),
    },
    {
      key: 'detectedAt',
      header: 'Detected',
      render: (rec: AdvisorRecommendation) => (
        <span className="text-sm text-surface-200">
          {new Date(rec.detectedAt).toLocaleDateString()}
        </span>
      ),
    },
    {
      key: 'actions',
      header: '',
      render: () => (
        <Button variant="ghost" size="sm" leftIcon={<ExternalLink className="h-3 w-3" />}>
          View
        </Button>
      ),
    },
  ];

  const categories = ['Cost', 'Security', 'Reliability', 'OperationalExcellence', 'Performance'];

  return (
    <PageContainer>
      <Header
        title="Azure Advisor"
        subtitle="Cost, security, and reliability recommendations"
        onRefresh={fetchRecommendations}
        isRefreshing={isRefreshing}
      />

      <PageContent>
        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card>
            <div className="text-center">
              <p className="text-3xl font-bold text-white">{recommendations.length}</p>
              <p className="text-sm text-surface-200">Total Recommendations</p>
            </div>
          </Card>
          <Card className="border-emerald-500/30 bg-emerald-500/5">
            <div className="text-center">
              <p className="text-3xl font-bold text-emerald-400">
                ${totalSavings.toLocaleString()}
              </p>
              <p className="text-sm text-surface-200">Potential Savings</p>
            </div>
          </Card>
          <Card className="border-red-500/30 bg-red-500/5">
            <div className="text-center">
              <p className="text-3xl font-bold text-red-400">
                {recommendations.filter(r => r.impact === 'High').length}
              </p>
              <p className="text-sm text-surface-200">High Impact</p>
            </div>
          </Card>
          <Card className="border-amber-500/30 bg-amber-500/5">
            <div className="text-center">
              <p className="text-3xl font-bold text-amber-400">
                {byCategoryCount['Security'] || 0}
              </p>
              <p className="text-sm text-surface-200">Security Alerts</p>
            </div>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-6">
          {/* Category Filter */}
          <Card>
            <CardHeader title="By Category" />
            <div className="space-y-2">
              <button
                onClick={() => setCategoryFilter(null)}
                className={`w-full flex items-center justify-between px-3 py-2 rounded-md transition-colors ${
                  !categoryFilter
                    ? 'bg-primary-500/20 text-primary-400'
                    : 'hover:bg-surface-700 text-surface-200'
                }`}
              >
                <span>All</span>
                <Badge variant="neutral">{recommendations.length}</Badge>
              </button>
              {categories.map((cat) => {
                const Icon = categoryIcons[cat as keyof typeof categoryIcons];
                const count = byCategoryCount[cat] || 0;
                return (
                  <button
                    key={cat}
                    onClick={() => setCategoryFilter(cat)}
                    className={`w-full flex items-center justify-between px-3 py-2 rounded-md transition-colors ${
                      categoryFilter === cat
                        ? 'bg-primary-500/20 text-primary-400'
                        : 'hover:bg-surface-700 text-surface-200'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <Icon className={`h-4 w-4 ${categoryColors[cat as keyof typeof categoryColors]}`} />
                      <span>{cat}</span>
                    </div>
                    <Badge variant="neutral">{count}</Badge>
                  </button>
                );
              })}
            </div>
          </Card>

          {/* Chart */}
          <div className="lg:col-span-3">
            <CategoryPieChart data={pieData} title="Recommendations by Category" />
          </div>
        </div>

        {/* Recommendations Table */}
        <Card padding="none">
          <div className="p-4 border-b border-surface-700">
            <h3 className="text-lg font-semibold text-white">
              {categoryFilter ? `${categoryFilter} Recommendations` : 'All Recommendations'}
            </h3>
          </div>
          <DataTable
            columns={columns}
            data={recommendations}
            keyField="id"
            loading={loading}
            emptyMessage="No recommendations found"
          />
        </Card>
      </PageContent>
    </PageContainer>
  );
}
