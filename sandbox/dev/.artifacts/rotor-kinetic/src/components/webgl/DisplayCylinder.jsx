import React, { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { MeshDisplayMaterial } from '../../webgl/materials/MeshDisplayMaterial';

// Texture mapping function (same as tutorial)
function setupCylinderTextureMapping(texture, dimensions, radius, height) {
  const cylinderCircumference = 2 * Math.PI * radius;
  const cylinderHeight = height;
  const cylinderAspectRatio = cylinderCircumference / cylinderHeight;

  if (dimensions.aspectRatio > cylinderAspectRatio) {
    // Canvas is wider than cylinder proportionally
    texture.repeat.x = cylinderAspectRatio / dimensions.aspectRatio;
    texture.repeat.y = 1;
    texture.offset.x = (1 - texture.repeat.x) / 2;
  } else {
    // Canvas is taller than cylinder proportionally
    texture.repeat.x = 1;
    texture.repeat.y = dimensions.aspectRatio / cylinderAspectRatio;
  }

  // Center the texture
  texture.offset.y = (1 - texture.repeat.y) / 2;
}

// Function to apply Gaussian blur to canvas
function applyBlur(ctx, canvas, radius = 3) {
  // Create a temporary canvas for blur processing
  const tempCanvas = document.createElement('canvas');
  const tempCtx = tempCanvas.getContext('2d');
  tempCanvas.width = canvas.width;
  tempCanvas.height = canvas.height;
  
  // Copy original to temp canvas
  tempCtx.drawImage(canvas, 0, 0);
  
  // Clear original canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  
  // Apply box blur (approximates Gaussian blur)
  const passes = 3; // Number of blur passes for better quality
  
  for (let pass = 0; pass < passes; pass++) {
    const imageData = tempCtx.getImageData(0, 0, canvas.width, canvas.height);
    const data = imageData.data;
    const width = canvas.width;
    const height = canvas.height;
    const blurredData = new Uint8ClampedArray(data);
    
    // Horizontal blur
    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        let r = 0, g = 0, b = 0, a = 0;
        let count = 0;
        
        for (let i = -radius; i <= radius; i++) {
          const pixelX = Math.max(0, Math.min(width - 1, x + i));
          const index = (y * width + pixelX) * 4;
          
          r += data[index];
          g += data[index + 1];
          b += data[index + 2];
          a += data[index + 3];
          count++;
        }
        
        const currentIndex = (y * width + x) * 4;
        blurredData[currentIndex] = r / count;
        blurredData[currentIndex + 1] = g / count;
        blurredData[currentIndex + 2] = b / count;
        blurredData[currentIndex + 3] = a / count;
      }
    }
    
    // Vertical blur
    for (let x = 0; x < width; x++) {
      for (let y = 0; y < height; y++) {
        let r = 0, g = 0, b = 0, a = 0;
        let count = 0;
        
        for (let i = -radius; i <= radius; i++) {
          const pixelY = Math.max(0, Math.min(height - 1, y + i));
          const index = (pixelY * width + x) * 4;
          
          r += blurredData[index];
          g += blurredData[index + 1];
          b += blurredData[index + 2];
          a += blurredData[index + 3];
          count++;
        }
        
        const currentIndex = (y * width + x) * 4;
        data[currentIndex] = r / count;
        data[currentIndex + 1] = g / count;
        data[currentIndex + 2] = b / count;
        data[currentIndex + 3] = a / count;
      }
    }
    
    // Update temp canvas with blurred data
    tempCtx.putImageData(new ImageData(data, width, height), 0, 0);
  }
  
  // Draw final blurred result back to original canvas
  ctx.drawImage(tempCanvas, 0, 0);
}

export function DisplayCylinder({ 
  position, 
  texture, 
  dimensions, 
  radius = 5, 
  height = 2,
  animationSpeed = 0.001,
  index = 0,
  ...props
}) {
  const meshRef = useRef();
  
  // Create unique texture clone for this cylinder
  const uniqueTexture = useMemo(() => {
    if (!texture) return null; // FIX: Prevent null texture processing
    
    const clonedTexture = texture.clone();
    clonedTexture.needsUpdate = true;
    clonedTexture.wrapS = THREE.RepeatWrapping;
    clonedTexture.wrapT = THREE.ClampToEdgeWrapping;
    
    // Setup texture mapping for this unique instance
    if (dimensions) { // FIX: Check dimensions exist
      setupCylinderTextureMapping(clonedTexture, dimensions, radius, height);
      
      // Add unique offset for each cylinder based on index
      clonedTexture.offset.x += index * 0.3;
    }
    
    return clonedTexture;
  }, [texture, dimensions, radius, height, index]);

  // Create darkened and blurred texture for backface
  const darkenedBlurredTexture = useMemo(() => {
    if (!uniqueTexture) return null; // FIX: Early return if no texture
    
    // Create a darkened and blurred version by creating a canvas
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    // Set canvas size to match texture
    canvas.width = uniqueTexture.image?.width || 512;
    canvas.height = uniqueTexture.image?.height || 512;
    
    if (uniqueTexture.image) { // FIX: Check if image exists
      // Clear canvas to transparent
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Draw original image first
      ctx.drawImage(uniqueTexture.image, 0, 0);
      
      // Apply blur effect first
      applyBlur(ctx, canvas, 2); // Blur radius of 4 pixels
      
      // Get image data to manipulate pixels for darkening
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const data = imageData.data;
      
      // Darken each pixel while preserving alpha
      for (let i = 0; i < data.length; i += 4) {
        // Darken RGB values (multiply by 0.2)
        data[i] = data[i] * 0.2;     // Red
        data[i + 1] = data[i + 1] * 0.2; // Green
        data[i + 2] = data[i + 2] * 0.2; // Blue
        // Keep alpha unchanged: data[i + 3] = data[i + 3];
      }
      
      // Put the modified image data back
      ctx.putImageData(imageData, 0, 0);
    }
    
    // Create texture from darkened and blurred canvas
    const processedTex = new THREE.CanvasTexture(canvas);
    processedTex.wrapS = uniqueTexture.wrapS;
    processedTex.wrapT = uniqueTexture.wrapT;
    processedTex.repeat.copy(uniqueTexture.repeat);
    processedTex.offset.copy(uniqueTexture.offset);
    
    return processedTex;
  }, [uniqueTexture]);
  
  useFrame((state, delta) => {
    // Move both textures X offset for rotation effect
    if (uniqueTexture) {
      uniqueTexture.offset.x += delta * animationSpeed;
      uniqueTexture.needsUpdate = true;
    }
    if (darkenedBlurredTexture) {
      darkenedBlurredTexture.offset.x += delta * animationSpeed;
      darkenedBlurredTexture.needsUpdate = true;
    }
  });
  
  // FIX: Don't render if no texture is available
  if (!uniqueTexture) {
    return null;
  }
  
  return (
    <group position={position} {...props}>
      {/* Front face */}
      <mesh ref={meshRef}>
        <cylinderGeometry args={[radius, radius, height, 100, 1, true]} />
        <meshBasicMaterial 
          map={uniqueTexture} 
          side={THREE.FrontSide}
          transparent={true}
          alphaTest={0.1}
          toneMapped={false}
        />
      </mesh>
      
      {/* Back face with darkened and blurred texture */}
      <mesh>
        <cylinderGeometry args={[radius, radius, height, 100, 1, true]} />
        <meshBasicMaterial 
          map={darkenedBlurredTexture} 
          side={THREE.BackSide}
          transparent={true}
          alphaTest={0.1}
          toneMapped={false}
        />
      </mesh>
    </group>
  );
}