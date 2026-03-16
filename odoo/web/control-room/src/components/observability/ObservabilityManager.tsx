'use client';

import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTrigger,
  DialogSurface,
  DialogBody,
  DialogTitle,
  DialogContent,
  TabList,
  Tab,
  SelectTabData,
  SelectTabEvent,
  Spinner,
  Button,
} from '@fluentui/react-components';
import {
  TaskListSquareLtr24Regular,
  Bot24Regular,
  HeartPulse24Regular,
  Organization24Regular,
  Dismiss24Regular,
} from '@fluentui/react-icons';
import { JobsTab } from './JobsTab';
import { AgentsTab } from './AgentsTab';
import { HealthTab } from './HealthTab';
import { TopologyTab } from './TopologyTab';

type TabValue = 'jobs' | 'agents' | 'health' | 'topology';

interface ObservabilityManagerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  defaultTab?: TabValue;
  isMobile?: boolean;
}

/**
 * ObservabilityManager - Platform Kit style dialog for managing
 * jobs, agents, service health, and ecosystem topology
 */
export function ObservabilityManager({
  open,
  onOpenChange,
  defaultTab = 'jobs',
  isMobile = false,
}: ObservabilityManagerProps) {
  const [selectedTab, setSelectedTab] = useState<TabValue>(defaultTab);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (open) {
      // Simulate initial load
      setIsLoading(true);
      const timer = setTimeout(() => setIsLoading(false), 500);
      return () => clearTimeout(timer);
    }
  }, [open]);

  const handleTabSelect = (_event: SelectTabEvent, data: SelectTabData) => {
    setSelectedTab(data.value as TabValue);
  };

  const renderTabContent = () => {
    if (isLoading) {
      return (
        <div className="flex items-center justify-center h-64">
          <Spinner size="large" label="Loading observability data..." />
        </div>
      );
    }

    switch (selectedTab) {
      case 'jobs':
        return <JobsTab />;
      case 'agents':
        return <AgentsTab />;
      case 'health':
        return <HealthTab />;
      case 'topology':
        return <TopologyTab />;
      default:
        return null;
    }
  };

  return (
    <Dialog open={open} onOpenChange={(_, data) => onOpenChange(data.open)}>
      <DialogSurface
        className={isMobile ? 'w-full h-full max-w-none m-0 rounded-none' : 'w-[90vw] max-w-6xl h-[85vh]'}
      >
        <DialogBody className="h-full flex flex-col">
          <DialogTitle className="flex items-center justify-between pr-2">
            <span className="text-xl font-semibold">Observability Platform</span>
            <Button
              appearance="subtle"
              icon={<Dismiss24Regular />}
              onClick={() => onOpenChange(false)}
              aria-label="Close"
            />
          </DialogTitle>

          <DialogContent className="flex-1 overflow-hidden flex flex-col">
            <TabList
              selectedValue={selectedTab}
              onTabSelect={handleTabSelect}
              className="mb-4 border-b border-surface-100"
            >
              <Tab
                value="jobs"
                icon={<TaskListSquareLtr24Regular />}
                className="font-medium"
              >
                Jobs
              </Tab>
              <Tab
                value="agents"
                icon={<Bot24Regular />}
                className="font-medium"
              >
                Agents
              </Tab>
              <Tab
                value="health"
                icon={<HeartPulse24Regular />}
                className="font-medium"
              >
                Health
              </Tab>
              <Tab
                value="topology"
                icon={<Organization24Regular />}
                className="font-medium"
              >
                Topology
              </Tab>
            </TabList>

            <div className="flex-1 overflow-auto">
              {renderTabContent()}
            </div>
          </DialogContent>
        </DialogBody>
      </DialogSurface>
    </Dialog>
  );
}

export default ObservabilityManager;
