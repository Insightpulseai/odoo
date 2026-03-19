'use client';

import { useState } from 'react';
import { PageContainer, PageContent } from '@/components/layout/PageContainer';
import { Header } from '@/components/layout/Header';
import { Card } from '@/components/common/Card';

type OperationType = 'receive' | 'pick' | 'transfer' | 'inventory';

interface Operation {
  type: OperationType;
  title: string;
  description: string;
  icon: string;
  color: string;
}

const operations: Operation[] = [
  {
    type: 'receive',
    title: 'Receive',
    description: 'Receive goods from suppliers',
    icon: '📦',
    color: 'bg-green-600 hover:bg-green-700',
  },
  {
    type: 'pick',
    title: 'Pick',
    description: 'Pick items for orders',
    icon: '🛒',
    color: 'bg-blue-600 hover:bg-blue-700',
  },
  {
    type: 'transfer',
    title: 'Transfer',
    description: 'Move items between locations',
    icon: '🔄',
    color: 'bg-purple-600 hover:bg-purple-700',
  },
  {
    type: 'inventory',
    title: 'Inventory',
    description: 'Count and adjust inventory',
    icon: '📋',
    color: 'bg-orange-600 hover:bg-orange-700',
  },
];

function OperationCard({
  op,
  onClick,
}: {
  op: Operation;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`${op.color} p-6 rounded-lg text-left w-full transition-colors`}
    >
      <span className="text-4xl">{op.icon}</span>
      <h3 className="text-xl font-semibold text-white mt-3">{op.title}</h3>
      <p className="text-white/80 text-sm mt-1">{op.description}</p>
    </button>
  );
}

function RecentScans() {
  const scans = [
    { barcode: 'PROD-001', product: 'Widget A', qty: 10, time: '2 min ago' },
    { barcode: 'PROD-002', product: 'Gadget B', qty: 5, time: '5 min ago' },
    { barcode: 'LOC-A1-01', product: 'Location A1-01', qty: 0, time: '10 min ago' },
  ];

  return (
    <Card>
      <h3 className="text-lg font-semibold text-white mb-4">Recent Scans</h3>
      <div className="space-y-3">
        {scans.map((scan, i) => (
          <div
            key={i}
            className="flex justify-between items-center py-2 border-b border-gray-700 last:border-0"
          >
            <div>
              <p className="text-white font-mono text-sm">{scan.barcode}</p>
              <p className="text-gray-400 text-xs">{scan.product}</p>
            </div>
            <div className="text-right">
              {scan.qty > 0 && (
                <p className="text-green-400 text-sm">+{scan.qty}</p>
              )}
              <p className="text-gray-500 text-xs">{scan.time}</p>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}

function ScannerModal({
  operation,
  onClose,
}: {
  operation: OperationType;
  onClose: () => void;
}) {
  const [barcode, setBarcode] = useState('');
  const [scannedItems, setScannedItems] = useState<string[]>([]);

  const handleScan = () => {
    if (barcode) {
      setScannedItems([...scannedItems, barcode]);
      setBarcode('');
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
      <div className="bg-gray-900 rounded-lg p-6 w-full max-w-md mx-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-white capitalize">
            {operation} Operation
          </h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            ✕
          </button>
        </div>

        <div className="mb-4">
          <input
            type="text"
            value={barcode}
            onChange={(e) => setBarcode(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleScan()}
            placeholder="Scan or enter barcode..."
            className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white text-lg font-mono"
            autoFocus
          />
        </div>

        <button
          onClick={handleScan}
          className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg mb-4"
        >
          📷 Scan Barcode
        </button>

        {scannedItems.length > 0 && (
          <div className="border-t border-gray-700 pt-4">
            <h3 className="text-sm text-gray-400 mb-2">
              Scanned ({scannedItems.length})
            </h3>
            <div className="space-y-2 max-h-40 overflow-y-auto">
              {scannedItems.map((item, i) => (
                <div
                  key={i}
                  className="flex justify-between items-center bg-gray-800 p-2 rounded"
                >
                  <span className="text-white font-mono text-sm">{item}</span>
                  <span className="text-green-400">✓</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="flex gap-2 mt-4">
          <button
            onClick={onClose}
            className="flex-1 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg"
          >
            Cancel
          </button>
          <button className="flex-1 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg">
            Complete
          </button>
        </div>
      </div>
    </div>
  );
}

export default function BarcodePage() {
  const [activeOperation, setActiveOperation] = useState<OperationType | null>(null);

  return (
    <PageContainer>
      <Header
        title="Barcode Scanner"
        subtitle="Inventory operations with barcode scanning"
      />
      <PageContent>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {operations.map((op) => (
          <OperationCard
            key={op.type}
            op={op}
            onClick={() => setActiveOperation(op.type)}
          />
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RecentScans />

        <Card>
          <h3 className="text-lg font-semibold text-white mb-4">Active Sessions</h3>
          <p className="text-gray-400 text-center py-8">
            No active sessions. Start an operation above.
          </p>
        </Card>
      </div>

        {activeOperation && (
          <ScannerModal
            operation={activeOperation}
            onClose={() => setActiveOperation(null)}
          />
        )}
      </PageContent>
    </PageContainer>
  );
}
