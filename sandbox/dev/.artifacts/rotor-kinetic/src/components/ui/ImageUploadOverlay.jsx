import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './card';
import { Button } from './button';
import { ImageDropZone } from './ImageDropZone';
import { RotateCcw } from 'lucide-react';

export function ImageUploadOverlay({ 
  displayImage,
  marqueeImage,
  onDisplayImageChange,
  onMarqueeImageChange,
  onResetToDefaults,
  isLoading,
  className = ""
}) {
  // Check if images are user-uploaded (have a file property)
  const isDisplayUserUploaded = displayImage && displayImage.file;
  const isMarqueeUserUploaded = marqueeImage && marqueeImage.file;

  return (
    <div className={className}>
      <Card 
        className="overflow-hidden border-0 transition-all duration-300 group gap-0"
        style={{
          background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          // border: '1px solid rgba(255, 255, 255, 0.18)',
          borderRadius: '16px'
        }}
      >

        <CardContent className="px-6 pl-6 pr-6 pt-6 pb-6">
          {/* Elegant Divider */}
          <div className="relative py-4">
            <div 
              className="absolute inset-0 flex items-center"
              style={{ opacity: 0.2 }}
            >
              <div 
                className="w-full border-t"
                style={{ borderColor: 'rgba(255, 255, 255, 0.2)' }}
              ></div>
            </div>
            <div className="relative flex justify-center">
              <div 
                className="font-semibold px-4 text-xs rounded-full py-1"
                style={{
                  backgroundColor: 'rgba(255, 255, 255, 0.2)',
                  color: 'rgba(255, 255, 255, 0.6)',
                  fontFamily: "'Plus Jakarta Sans', sans-serif"
                }}
              >
                DISPLAY CYLINDER
              </div>
            </div>
          </div>
          
          {/* Display Image Section */}
          <div className="space-y-3">
              {/* Only show reset button if user has uploaded a custom image */}
              {isDisplayUserUploaded && (
                <div className="flex items-center justify-between">

                  <div className="flex items-center gap-2">
                    <div 
                      className="w-2 h-2 rounded-full"
                      style={{ backgroundColor: '#10b981' }}
                    ></div>
                    <label 
                      className="text-sm font-semibold text-white/90"
                      style={{ color: 'rgba(255, 255, 255, 0.5)' }}>Custom</label>
                  </div>
          
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onResetToDefaults('display')}
                    disabled={isLoading}
                    className="h-8 px-3 rounded-full text-white/70 hover:text-white hover:scale-105 transition-all duration-200 bg-white/5 border-white/20 hover:bg-white/10"
                    style={{
                      fontFamily: "'Plus Jakarta Sans', sans-serif"
                    }}
                  >
                    <RotateCcw className="h-3 w-3 mr-1" />
                    Reset
                  </Button>
                  
                </div>
              )}
            <div 
              className="rounded-xl overflow-hidden transition-all duration-300 hover:scale-[1.02]"
              style={{
                background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%)',
                border: '1px solid rgba(255, 255, 255, 0.1)'
              }}
            >
              <ImageDropZone
                type="display"
                currentImage={displayImage}
                onImageChange={onDisplayImageChange}
                accept="image/jpeg,image/png,image/webp,image/gif,image/apng"
              />
            </div>
          </div>
          
          {/* Elegant Divider */}
          <div className="relative py-4">
            <div 
              className="absolute inset-0 flex items-center"
              style={{ opacity: 0.2 }}
            >
              <div 
                className="w-full border-t"
                style={{ borderColor: 'rgba(255, 255, 255, 0.2)' }}
              ></div>
            </div>
            <div className="relative flex justify-center">
              <div 
                className="font-semibold px-4 text-xs rounded-full py-1"
                style={{
                  backgroundColor: 'rgba(255, 255, 255, 0.2)',
                  color: 'rgba(255, 255, 255, 0.6)',
                  fontFamily: "'Plus Jakarta Sans', sans-serif"
                }}
              >
                MARQUEE STRIP
              </div>
            </div>
          </div>
          
          {/* Marquee Image Section */}
          <div className="space-y-3">
              {/* Only show reset button if user has uploaded a custom image */}
              {isMarqueeUserUploaded && (
                <div className="flex items-center justify-between">

                  <div className="flex items-center gap-2">
                    <div 
                      className="w-2 h-2 rounded-full"
                      style={{ backgroundColor: '#10b981' }}
                    ></div>
                    <label 
                      className="text-sm font-semibold text-white/90"
                      style={{ color: 'rgba(255, 255, 255, 0.5)' }}>Custom</label>
                  </div>
          
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onResetToDefaults('marquee')}
                    disabled={isLoading}
                    className="h-8 px-3 rounded-full text-white/70 hover:text-white hover:scale-105 transition-all duration-200 bg-white/5 border-white/20 hover:bg-white/10"
                    style={{
                      fontFamily: "'Plus Jakarta Sans', sans-serif"
                    }}
                  >
                    <RotateCcw className="h-3 w-3 mr-1" />
                    Reset
                  </Button>
                  
                </div>
              )}
            <div 
              className="rounded-xl overflow-hidden transition-all duration-300 hover:scale-[1.02]"
              style={{
                background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%)',
                border: '1px solid rgba(255, 255, 255, 0.1)'
              }}
            >
              <ImageDropZone
                type="marquee"
                currentImage={marqueeImage}
                onImageChange={onMarqueeImageChange}
                accept="image/jpeg,image/png,image/webp,image/gif,image/apng"
              />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}