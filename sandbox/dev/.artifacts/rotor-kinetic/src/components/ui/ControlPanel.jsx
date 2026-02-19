import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './card';
import { Button } from './button';
import { Slider } from './slider';
import { Separator } from './separator';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from './sheet';
import { RotateCcw, Settings, Menu } from 'lucide-react';

export function ControlPanel({ 
  onResetToDefaults,
  animationSpeeds,
  onAnimationSpeedChange,
  isLoading
}) {
  const [isOpen, setIsOpen] = React.useState(false);

  return (
    <>
      {/* Floating Control Button - Updated Style */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          position: 'fixed',
          top: '48px',
          right: '24px',
          zIndex: '80',
          backgroundColor: 'rgba(3, 2, 19, 0.16)',
          backdropFilter: 'blur(8px)',
          WebkitBackdropFilter: 'blur(8px)',
          border: 'none',
          borderRadius: '9999px',
          fontFamily: 'Plus Jakarta Sans, sans-serif',
          fontWeight: '600',
          color: 'white',
          padding: '8px 16px',
          display: 'flex',
          alignItems: 'center',
          cursor: 'pointer',
          transition: 'all 0.2s ease',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
        }}
        onMouseEnter={(e) => {
          e.target.style.transform = 'scale(1.05)';
          e.target.style.boxShadow = '0 8px 15px rgba(0, 0, 0, 0.2)';
        }}
        onMouseLeave={(e) => {
          e.target.style.transform = 'scale(1)';
          e.target.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
        }}
      >
        <Menu style={{ width: '16px', height: '16px', marginRight: '8px', color: 'white' }} />
        Controls
      </button>

      {/* Control Panel Sheet */}
      <Sheet open={isOpen} onOpenChange={setIsOpen}>
        <SheetContent side="right" className="overflow-y-auto z-[100] p-6" 
          style={{ 
            zIndex: '100',
            width: '250px',
          }}>
          <SheetHeader className="pb-2 font-[Plus_Jakarta_Sans] font-bold">
            <SheetTitle>Gallery Controls</SheetTitle>
          </SheetHeader>
          
          <div className="space-y-1">
        
            {/* Animation Settings */}
            <Card style={{
                marginBottom: '12px'
            }}>
              <CardHeader className="font-[Plus_Jakarta_Sans] font-bold">
                <CardTitle>Animation Settings</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 pb-3">
                  <div className="flex justify-between items-center" style={{paddingBottom: '4px'}}>
                    <label 
                      className="text-sm font-bold"
                      style={{
                        color: 'rgba(0, 0, 0, 0.8)'
                      }}>
                      Display Speed
                    </label>
                    <span 
                      className="text-sm font-medium"
                      style={{
                        color: 'rgba(0, 0, 0, 0.5)',
                      }}>
                      {animationSpeeds.display.toFixed(3)}
                    </span>
                  </div>
                  <Slider
                    value={[animationSpeeds.display * 1000]}
                    onValueChange={([value]) => 
                      onAnimationSpeedChange('display', value / 1000)
                    }
                    min={0}
                    max={50} // Increased from 5 to 50 to allow speeds up to 0.05
                    step={1} // Changed from 0.1 to 1 for better control
                    className="w-full"
                  />
                </div>
                
                <div className="space-y-2">

                  <div className="flex justify-between items-center" style={{paddingBottom: '4px'}}>
                    <label 
                      className="text-sm font-bold"
                      style={{
                        color: 'rgba(0, 0, 0, 0.8)'
                      }}>
                      Marquee Speed
                    </label>
                    <span 
                      className="text-sm font-medium"
                      style={{
                        color: 'rgba(0, 0, 0, 0.5)',
                      }}>
                      {(animationSpeeds.marquee * 30).toFixed(1)}
                    </span>
                  </div>
                  
                  <Slider
                    value={[animationSpeeds.marquee * 30]}
                    onValueChange={([value]) => 
                      onAnimationSpeedChange('marquee', value / 30)
                    }
                    min={0}
                    max={5}
                    step={0.1}
                    className="w-full"
                  />
                </div>
              </CardContent>
            </Card>
                
            {/* Reset All */}
            <Button 
              variant="outline" 
              className="w-full rounded-full font-[Plus_Jakarta_Sans] font-semibold"
              onClick={() => onResetToDefaults('all')}
              disabled={isLoading}
            >
            <RotateCcw className="h-4 w-4 mr-2" />
              Reset to Defaults
            </Button>
            
          </div>
        </SheetContent>
      </Sheet>
    </>
  );
}