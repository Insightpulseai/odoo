import * as THREE from 'three';

// Check if image is animated (GIF or APNG)
function isAnimatedImage(file) {
  if (!file || !file.type) return false;
  return file.type === 'image/gif' || 
         file.type === 'image/apng' || 
         (file.type === 'image/png' && file.name && file.name.toLowerCase().includes('.apng'));
}

// Create animated texture from GIF or APNG
async function createAnimatedTexture(imageUrl, file) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    
    img.onload = () => {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      
      canvas.width = img.width || img.naturalWidth;
      canvas.height = img.height || img.naturalHeight;
      
      // Create texture from canvas
      const texture = new THREE.CanvasTexture(canvas);
      texture.wrapS = THREE.RepeatWrapping;
      texture.wrapT = THREE.RepeatWrapping;
      texture.flipY = true;
      texture.colorSpace = THREE.SRGBColorSpace;
      texture.magFilter = THREE.LinearFilter;
      texture.minFilter = THREE.LinearMipmapLinearFilter;
      texture.generateMipmaps = true;
      
      const dimensions = {
        width: canvas.width,
        height: canvas.height,
        aspectRatio: canvas.width / canvas.height
      };
      
      // Start animation loop
      let animationId;
      const animate = () => {
        // Clear and redraw the image (this triggers the next frame for GIFs)
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        texture.needsUpdate = true;
        
        animationId = requestAnimationFrame(animate);
      };
      
      // Store animation ID for cleanup
      texture.userData = { animationId, canvas, ctx, img };
      
      animate();
      resolve({ texture, dimensions, isAnimated: true });
    };
    
    img.onerror = (error) => {
      console.error('Error loading animated image:', error);
      reject(error);
    };
    
    img.src = imageUrl;
  });
}

export async function loadImageTexture({ image }) {
  const imageUrl = image.url || URL.createObjectURL(image.file);
  
  // Check if this is an animated image
  if (image.file && isAnimatedImage(image.file)) {
    return createAnimatedTexture(imageUrl, image.file);
  }
  
  // Standard static image loading
  return new Promise((resolve, reject) => {
    const loader = new THREE.TextureLoader();
    
    loader.load(
      imageUrl,
      (texture) => {
        // Get image dimensions
        const img = texture.image;
        const dimensions = {
          width: img.width,
          height: img.height,
          aspectRatio: img.width / img.height
        };
        
        // Configure texture for better color reproduction
        texture.wrapS = THREE.RepeatWrapping;
        texture.wrapT = THREE.RepeatWrapping;
        texture.flipY = true; // Fix upside-down textures
        texture.colorSpace = THREE.SRGBColorSpace; // Ensure proper color space
        texture.magFilter = THREE.LinearFilter; // Better scaling
        texture.minFilter = THREE.LinearMipmapLinearFilter;
        texture.generateMipmaps = true;
        texture.needsUpdate = true;
        
        resolve({ texture, dimensions, isAnimated: false });
      },
      undefined,
      (error) => {
        console.error('Error loading texture:', error);
        reject(error);
      }
    );
  });
}

export function setupCylinderTextureMapping(texture, dimensions, radius, height) {
  const circumference = 2 * Math.PI * radius;
  const cylinderAspectRatio = circumference / height;
  
  // Improved texture mapping to prevent cutoff and maintain aspect ratio
  const imageAspect = dimensions.aspectRatio;
  const cylinderAspect = cylinderAspectRatio;
  
  if (imageAspect > cylinderAspect) {
    // Image is wider than cylinder - fit height and allow horizontal repetition
    texture.repeat.y = 1.0;
    texture.repeat.x = cylinderAspect / imageAspect;
    texture.offset.x = 0; // Start from left edge
    texture.offset.y = 0;
  } else {
    // Image is taller than cylinder - fit width and center vertically
    texture.repeat.x = 1.0;
    texture.repeat.y = imageAspect / cylinderAspect;
    texture.offset.x = 0;
    texture.offset.y = (1 - texture.repeat.y) / 2; // Center vertically
  }
  
  return texture;
}

export function disposeTexture(texture) {
  if (texture && texture.dispose) {
    // Stop animation if it's an animated texture
    if (texture.userData && texture.userData.animationId) {
      cancelAnimationFrame(texture.userData.animationId);
    }
    texture.dispose();
  }
}