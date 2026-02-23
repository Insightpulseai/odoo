import React from 'react';
import { Card, CardContent } from './card';

export function CameraConfigOverlay({ cameraInfo, className = "" }) {
  if (!cameraInfo) {
    return null;
  }

  return (
    <div className={className}>
      <Card 
        className="overflow-hidden border-0 transition-all duration-300"
        style={{
          background: 'transparent',
          borderRadius: '20px',
          border: 'none',
          boxShadow: 'none'
        }}
      >
        <CardContent className="p-6">
          {/* Position Section */}
          <div className="pb-4">
            <div className="flex items-center gap-2 pb-3">
              <div 
                className="w-2 h-2 rounded-full"
                style={{ backgroundColor: '#FF383C' }}
              />
              <label 
                className="text-sm font-semibold"
                style={{ 
                  fontSize: '0.875rem !important',
                  fontWeight: '600 !important',
                  color: 'rgba(255, 255, 255, 0.7)',
                  fontFamily: "'Plus Jakarta Sans', sans-serif",
                  lineHeight: '1.25rem'
                }}
              >
                CAM Position
              </label>
            </div>
            <div 
              className="px-4 py-2 rounded-xl"
              style={{
                background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%)'
              }}
            >
              <div className="flex justify-between gap-4">
                <div className="flex flex-col items-center">
                  <span 
                    className="text-xs mb-1"
                    style={{
                      fontSize: '0.75rem !important',
                      color: 'rgba(255, 255, 255, 0.32)',
                      fontFamily: "'Plus Jakarta Sans', sans-serif"
                    }}
                  >
                    X
                  </span>
                  <span 
                    className="text-sm font-semibold"
                    style={{
                      fontSize: '0.875rem !important',
                      fontWeight: '600 !important',
                      color: 'rgba(255, 255, 255, 0.8)',
                      fontFamily: "'Plus Jakarta Sans', sans-serif"
                    }}
                  >
                    {cameraInfo.position.x.toFixed(2)}
                  </span>
                </div>
                <div className="flex flex-col items-center">
                  <span 
                    className="text-xs mb-1"
                    style={{
                      fontSize: '0.75rem !important',
                      color: 'rgba(255, 255, 255, 0.32)',
                      fontFamily: "'Plus Jakarta Sans', sans-serif"
                    }}
                  >
                    Y
                  </span>
                  <span 
                    className="text-sm font-semibold"
                    style={{
                      fontSize: '0.875rem !important',
                      fontWeight: '600 !important',
                      color: 'rgba(255, 255, 255, 0.8)',
                      fontFamily: "'Plus Jakarta Sans', sans-serif"
                    }}
                  >
                    {cameraInfo.position.y.toFixed(2)}
                  </span>
                </div>
                <div className="flex flex-col items-center">
                  <span 
                    className="text-xs mb-1"
                    style={{
                      fontSize: '0.75rem !important',
                      color: 'rgba(255, 255, 255, 0.32)',
                      fontFamily: "'Plus Jakarta Sans', sans-serif"
                    }}
                  >
                    Z
                  </span>
                  <span 
                    className="text-sm font-semibold"
                    style={{
                      fontSize: '0.875rem !important',
                      fontWeight: '600 !important',
                      color: 'rgba(255, 255, 255, 0.8)',
                      fontFamily: "'Plus Jakarta Sans', sans-serif"
                    }}
                  >
                    {cameraInfo.position.z.toFixed(2)}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}