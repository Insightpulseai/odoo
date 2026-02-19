import { useState, useCallback, useRef, useEffect } from 'react';
import { loadImageTexture, disposeTexture } from '../utils/textureUtils';
import { defaultImages } from '../data/defaultImages';

export function useTextureManager() {
  const [state, setState] = useState({
    display: {
      image: defaultImages.display,
      texture: null,
      dimensions: null,
      isLoading: true,
      error: null
    },
    marquee: {
      image: defaultImages.marquee,
      texture: null,
      dimensions: null,
      isLoading: true,
      error: null
    }
  });
  
  const [animationSpeeds, setAnimationSpeeds] = useState({
    display: 0.01,
    marquee: 1/30
  });
  
  const loadTexture = useCallback(async (type, image) => {
    setState(prev => ({
      ...prev,
      [type]: { ...prev[type], isLoading: true, error: null }
    }));
    
    try {
      const result = await loadImageTexture({ image });
      
      setState(prev => {
        // Dispose old texture
        if (prev[type].texture) {
          disposeTexture(prev[type].texture);
        }
        
        return {
          ...prev,
          [type]: {
            ...prev[type],
            image,
            texture: result.texture,
            dimensions: result.dimensions,
            isLoading: false,
            error: null
          }
        };
      });
    } catch (error) {
      console.error(`Error loading ${type} texture:`, error);
      setState(prev => ({
        ...prev,
        [type]: { ...prev[type], isLoading: false, error: error.message }
      }));
    }
  }, []);
  
  const updateDisplayImage = useCallback((image) => {
    if (image) {
      loadTexture('display', image);
    } else {
      loadTexture('display', defaultImages.display);
    }
  }, [loadTexture]);
  
  const updateMarqueeImage = useCallback((image) => {
    if (image) {
      loadTexture('marquee', image);
    } else {
      loadTexture('marquee', defaultImages.marquee);
    }
  }, [loadTexture]);
  
  const resetToDefaults = useCallback((type) => {
    if (type === 'all') {
      loadTexture('display', defaultImages.display);
      loadTexture('marquee', defaultImages.marquee);
      setAnimationSpeeds({
        display: 0.001,
        marquee: 1/30
      });
    } else if (type === 'display') {
      loadTexture('display', defaultImages.display);
    } else if (type === 'marquee') {
      loadTexture('marquee', defaultImages.marquee);
    }
  }, [loadTexture]);
  
  const updateAnimationSpeed = useCallback((type, speed) => {
    setAnimationSpeeds(prev => ({
      ...prev,
      [type]: speed
    }));
  }, []);
  
  // Load default textures on mount
  useEffect(() => {
    loadTexture('display', defaultImages.display);
    loadTexture('marquee', defaultImages.marquee);
  }, [loadTexture]);
  
  // Cleanup textures on unmount
  useEffect(() => {
    return () => {
      if (state.display.texture) disposeTexture(state.display.texture);
      if (state.marquee.texture) disposeTexture(state.marquee.texture);
    };
  }, []);
  
  return {
    displayState: state.display,
    marqueeState: state.marquee,
    animationSpeeds,
    updateDisplayImage,
    updateMarqueeImage,
    resetToDefaults,
    updateAnimationSpeed
  };
}