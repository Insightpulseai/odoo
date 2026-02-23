import React, { useCallback, useState } from 'react';
import { Button } from './button';
import { Upload, X, Image as ImageIcon, Plus } from 'lucide-react';

export function ImageDropZone({ 
  type, 
  onImageChange, 
  currentImage,
  accept = "image/jpeg,image/png,image/webp,image/gif,image/apng",
  maxFileSize = 10 * 1024 * 1024 // 10MB
}) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [error, setError] = useState(null);
  
  // Check if this is a user-uploaded image (has a file property)
  const isUserUploaded = currentImage && currentImage.file;
  
  const validateFile = (file) => {
    if (file.size > maxFileSize) {
      return 'File too large (max 10MB)';
    }
    
    const acceptedMimeTypes = accept.split(',').map(t => t.trim());
    const validMimeTypes = [];
    
    acceptedMimeTypes.forEach(type => {
      if (type === 'image/jpeg') {
        validMimeTypes.push('image/jpeg', 'image/jpg');
      } else if (type === 'image/png') {
        validMimeTypes.push('image/png');
      } else if (type === 'image/webp') {
        validMimeTypes.push('image/webp');
      } else if (type === 'image/gif') {
        validMimeTypes.push('image/gif');
      } else if (type === 'image/apng') {
        validMimeTypes.push('image/apng', 'image/png');
      }
    });
    
    const isLikelyAPNG = file.type === 'image/png' && 
                        (file.name.toLowerCase().includes('.apng') || 
                         file.name.toLowerCase().endsWith('.apng'));
    
    if (!validMimeTypes.includes(file.type) && !isLikelyAPNG) {
      return 'Invalid file type';
    }
    
    return null;
  };
  
  const handleFile = useCallback((file) => {
    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }
    
    setError(null);
    onImageChange({
      file,
      url: URL.createObjectURL(file),
      alt: `Uploaded ${type} image`
    });
  }, [onImageChange, type, maxFileSize, accept]);
  
  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFile(files[0]);
    }
  }, [handleFile]);
  
  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);
  
  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);
  
  const handleFileInput = useCallback((e) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFile(file);
    }
  }, [handleFile]);
  
  const handleClick = useCallback(() => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = accept;
    input.style.display = 'none';
    input.addEventListener('change', (e) => {
      const file = e.target.files?.[0];
      if (file) {
        handleFile(file);
      }
      document.body.removeChild(input);
    });
    document.body.appendChild(input);
    input.click();
  }, [accept, handleFile]);
  
  return (
    <div style={{ display: 'flex', flexDirection: 'column'}}>
      {/* Image Preview Section - Full width with inline styles */}
      {currentImage && (
        <div 
          style={{
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '8px',
            borderTopLeftRadius: '8px',
            borderTopRightRadius: '8px',
            borderBottomLeftRadius: '0',
            borderBottomRightRadius: '0',
            position: 'relative',
            background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.04) 100%)',
          }}
        >
          <img
            src={currentImage.url}
            alt={currentImage.alt}
            style={{
              width: '100%',
              height: '48px',
              objectFit: 'contain',
              borderRadius: '4px'
            }}
          />
        </div>
      )}

      {/* Upload Zone - Always available */}
      <div 
        style={{
          position: 'relative',
          overflow: 'hidden',
          transition: 'all 0.3s ease',
          cursor: 'pointer',
          background: isDragOver 
            ? 'linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%)'
            : 'linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.04) 100%)',
          border: isDragOver 
            ? '2px dashed rgba(102, 126, 234, 0.5)'
            : error 
            ? '2px dashed rgba(239, 68, 68, 0.5)'
            : '2px dashed rgba(255, 255, 255, 0.2)',
          minHeight: '100px',
          borderTopLeftRadius: '0',
          borderTopRightRadius: '0', 
          borderBottomLeftRadius: '12px',
          borderBottomRightRadius: '12px',
          transform: isDragOver ? 'scale(1.02)' : 'scale(1)'
        }}
        onMouseEnter={(e) => {
          if (!isDragOver) {
            e.currentTarget.style.transform = 'scale(1.01)';
          }
        }}
        onMouseLeave={(e) => {
          if (!isDragOver) {
            e.currentTarget.style.transform = 'scale(1)';
          }
        }}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={handleClick}
      >
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100%',
          padding: '16px',
          gap: '8px'
        }}>
          <div 
            style={{
              padding: '8px',
              borderRadius: '50%',
              transition: 'all 0.3s ease',
              background: isDragOver 
                ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                : 'linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%)',
              border: '1px solid rgba(255, 255, 255, 0.2)'
            }}
          >
            {isDragOver ? (
              <Upload style={{
                height: '20px',
                width: '20px',
                color: 'white',
                animation: 'bounce 1s infinite'
              }} />
            ) : (
              <Plus style={{
                height: '20px',
                width: '20px',
                color: 'rgba(255, 255, 255, 0.7)'
              }}/>
            )}
          </div>
          
          <div style={{ textAlign: 'center' }}>
            <p style={{
              fontWeight: '600',
              fontSize: '14px',
              color: 'rgba(255, 255, 255, 0.9)',
              fontFamily: "'Plus Jakarta Sans', sans-serif",
              margin: '0'
            }}>
              {isDragOver ? 'Drop to upload' : currentImage ? 'Replace texture' : 'Upload texture'}
            </p>
            <p style={{
              fontSize: '12px',
              color: 'rgba(255, 255, 255, 0.5)'
            }}>
              Drag and drop or click
            </p>
          </div>
        </div>

        {/* Animated border effect on drag */}
        {isDragOver && (
          <div 
            style={{
              position: 'absolute',
              top: '0',
              left: '0',
              right: '0',
              bottom: '0',
              borderRadius: '8px',
              animation: 'pulse 2s infinite',
              pointerEvents: 'none',
              background: 'linear-gradient(45deg, transparent 30%, rgba(102, 126, 234, 0.1) 50%, transparent 70%)',
              backgroundSize: '200% 200%'
            }}
          />
        )}
      </div>
      
      {error && (
        <div 
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px',
            borderRadius: '8px',
            fontSize: '14px',
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            color: 'rgba(239, 68, 68, 0.9)'
          }}
        >
          <X style={{ height: '12px', width: '12px' }} />
          {error}
        </div>
      )}
    </div>
  );
}