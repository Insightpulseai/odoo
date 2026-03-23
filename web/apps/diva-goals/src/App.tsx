import { Routes, Route } from 'react-router-dom';
import { AppShell } from './layout/AppShell';
import { GoalListPage } from './pages/GoalListPage';
import { GoalDetailPage } from './pages/GoalDetailPage';

export function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<GoalListPage />} />
        <Route path="/goals/:goalId" element={<GoalDetailPage />} />
      </Routes>
    </AppShell>
  );
}
