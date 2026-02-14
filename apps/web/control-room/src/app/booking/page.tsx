import { Suspense } from 'react';
import { PageContainer, PageContent } from '@/components/layout/PageContainer';
import { Header } from '@/components/layout/Header';
import { Card } from '@/components/common/Card';
import { Badge } from '@/components/common/Badge';

interface Calendar {
  id: string;
  name: string;
  slug: string;
  timezone: string;
  default_duration: number;
  is_active: boolean;
  upcoming_count: number;
}

async function getCalendars(): Promise<Calendar[]> {
  // TODO: Fetch from Supabase
  return [
    {
      id: '1',
      name: 'Sales Consultations',
      slug: 'sales-consult',
      timezone: 'America/New_York',
      default_duration: 30,
      is_active: true,
      upcoming_count: 12,
    },
    {
      id: '2',
      name: 'Technical Support',
      slug: 'tech-support',
      timezone: 'America/New_York',
      default_duration: 45,
      is_active: true,
      upcoming_count: 8,
    },
  ];
}

function CalendarCard({ calendar }: { calendar: Calendar }) {
  return (
    <Card>
      <div className="flex justify-between items-start">
        <div>
          <h3 className="text-lg font-semibold text-white">{calendar.name}</h3>
          <p className="text-gray-400 text-sm mt-1">
            {calendar.default_duration} min • {calendar.timezone}
          </p>
        </div>
        <Badge variant={calendar.is_active ? 'success' : 'neutral'}>
          {calendar.is_active ? 'Active' : 'Inactive'}
        </Badge>
      </div>

      <div className="mt-4 flex gap-2">
        <span className="text-blue-400 text-sm">
          {calendar.upcoming_count} upcoming
        </span>
      </div>

      <div className="mt-4 flex gap-2">
        <a
          href={`/booking/${calendar.slug}`}
          className="px-3 py-1 text-sm bg-gray-700 hover:bg-gray-600 rounded text-white"
        >
          Manage
        </a>
        <a
          href={`/book/${calendar.slug}`}
          className="px-3 py-1 text-sm bg-blue-600 hover:bg-blue-700 rounded text-white"
        >
          Booking Link
        </a>
      </div>
    </Card>
  );
}

async function CalendarsList() {
  const calendars = await getCalendars();

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {calendars.map((cal) => (
        <CalendarCard key={cal.id} calendar={cal} />
      ))}
    </div>
  );
}

export default function BookingPage() {
  return (
    <PageContainer>
      <Header
        title="Appointments"
        subtitle="Manage booking calendars and availability"
      />
      <PageContent>
        <div className="mb-6 flex justify-end">
        <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg">
          + New Calendar
        </button>
      </div>

      <Suspense fallback={<div className="text-gray-400">Loading calendars...</div>}>
        <CalendarsList />
      </Suspense>

        <div className="mt-8">
          <h2 className="text-xl font-semibold text-white mb-4">Today's Appointments</h2>
          <Card>
            <p className="text-gray-400 text-center py-4">
              No appointments scheduled for today
            </p>
          </Card>
        </div>
      </PageContent>
    </PageContainer>
  );
}
