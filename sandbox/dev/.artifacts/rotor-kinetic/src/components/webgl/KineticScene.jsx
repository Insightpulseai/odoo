import React, { Suspense, useRef, useState, useEffect } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import * as THREE from 'three';
import { DisplayCylinder } from './DisplayCylinder';
import { MarqueeStrip } from './MarqueeStrip';
import { sceneConfig } from '../../data/defaultImages';

function LoadingFallback() {
  return (
    <mesh>
      <boxGeometry args={[2, 2, 2]} />
      <meshBasicMaterial color="#666666" wireframe />
    </mesh>
  );
}

function SceneBackground() {
  const { scene } = useThree();
  
  useEffect(() => {
    scene.background = new THREE.Color('#2B2B2B');
  }, [scene]);
  
  return null;
}

function GridBackground() {
  const gridRef = useRef();
  
  useEffect(() => {
    if (!gridRef.current) return;
    
    // Create a simple, clean grid
    const size = 100; // Grid size
    const step = 0.5; // Grid spacing
    const divisions = size / step;
    
    // Create geometry for the grid
    const geometry = new THREE.BufferGeometry();
    const material = new THREE.LineBasicMaterial({ 
      color: '#555555',
      opacity: 0.5,
      transparent: true
    });
    
    const points = [];
    
    // Create horizontal lines
    for (let i = 0; i <= divisions; i++) {
      const y = (i * step) - (size / 2);
      points.push(-size / 2, y, 0, size / 2, y, 0);
    }
    
    // Create vertical lines
    for (let i = 0; i <= divisions; i++) {
      const x = (i * step) - (size / 2);
      points.push(x, -size / 2, 0, x, size / 2, 0);
    }
    
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(points, 3));
    
    const grid = new THREE.LineSegments(geometry, material);
    
    // Position grid behind the objects
    grid.position.set(0, 0, -80);
    
    gridRef.current.add(grid);
    
    return () => {
      if (gridRef.current && grid) {
        gridRef.current.remove(grid);
        geometry.dispose();
        material.dispose();
      }
    };
  }, []);
  
  return <group ref={gridRef} />;
}

function CameraDebugger({ onCameraUpdate, controlsRef }) {
  const { camera } = useThree();
  
  useFrame(() => {
    if (onCameraUpdate) {
      const target = controlsRef.current?.target || { x: 0, y: 0, z: 0 };
      onCameraUpdate({
        position: camera.position,
        rotation: camera.rotation,
        fov: camera.fov,
        zoom: camera.zoom,
        target: target // Pan position from OrbitControls
      });
    }
  });
  
  return null;
}

// Loading indicator component
function LoadingIndicator() {
  return (
    <group>
      <mesh position={[0, 0, 0]}>
        <sphereGeometry args={[0.5, 16, 16]} />
        <meshBasicMaterial color="#888888" transparent opacity={0.8} />
      </mesh>
      <mesh position={[0, 2, 0]}>
        <boxGeometry args={[3, 0.5, 0.1]} />
        <meshBasicMaterial color="#666666" />
      </mesh>
    </group>
  );
}

export function KineticScene({ 
  displayTexture, 
  displayDimensions, 
  marqueeTexture,
  isDisplayLoading = false,
  isMarqueeLoading = false,
  animationSpeed = { display: 0.001, marquee: 1/30 },
  onCameraUpdate
}) {
  const { 
    itemCount, 
    verticalGap, 
    groupRotation, 
    cylinderRadius,
    cameraFOV,
    cameraPosition,
    cameraTarget,
    cameraControls
  } = sceneConfig;
  
  const controlsRef = useRef();
  
  // Generate positions for display cylinders and marquee strips
  const displayPositions = [];
  const marqueePositions = [];
  
  for (let i = 0; i < itemCount; i++) {
    const y = (i - itemCount / 2) * verticalGap;
    displayPositions.push([0, y, 0]);
    
    if (i < itemCount - 1) {
      // Fixed positioning for marquee strips with increased spacing
      marqueePositions.push([0, y + verticalGap / 2, 0]);
    }
  }
  
  return (
    <Canvas
      camera={{ 
        fov: cameraFOV, 
        position: cameraPosition,
        far: 1000
      }}
      style={{ 
        height: '100vh', 
        width: '100vw' 
      }}
      gl={{ 
        antialias: true, 
        alpha: false,
        outputColorSpace: 'srgb',
        toneMapping: 'none' // Preserve original colors
      }}
    >
      <Suspense fallback={<LoadingFallback />}>
        <SceneBackground />
        <GridBackground />
        <CameraDebugger onCameraUpdate={onCameraUpdate} controlsRef={controlsRef} />
        <group rotation={groupRotation}>
          {/* Display Cylinders - only render when texture is loaded */}
          {!isDisplayLoading && displayTexture && displayDimensions ? (
            displayPositions.map((position, index) => (
              <DisplayCylinder
                key={`display-${index}`}
                index={index}
                position={position}
                texture={displayTexture}
                dimensions={displayDimensions}
                radius={cylinderRadius}
                height={2.2}
                animationSpeed={animationSpeed.display}
              />
            ))
          ) : (
            // Show loading indicator for display cylinders
            displayPositions.map((position, index) => (
              <group key={`loading-display-${index}`} position={position}>
                <LoadingIndicator />
              </group>
            ))
          )}
          
          {/* Marquee Strips - only render when texture is loaded */}
          {!isMarqueeLoading && marqueeTexture ? (
            marqueePositions.map((position, index) => (
              <MarqueeStrip
                key={`marquee-${index}`}
                position={position}
                texture={marqueeTexture}
                rotation={[0, 0, 0.300]} // Tilts the marquee strip
                radius={cylinderRadius + 0.7} // Your existing radius calculation
                animationSpeed={animationSpeed.marquee}
                textureRepeat={[8, 1]}
                backfaceRepeatX={5}
              />
            ))
          ) : (
            // Show loading indicator for marquee strips
            marqueePositions.map((position, index) => (
              <group key={`loading-marquee-${index}`} position={position}>
                <mesh position={[0, 0, 0]}>
                  <cylinderGeometry args={[cylinderRadius + 0.7, cylinderRadius + 0.7, 0.1, 32]} />
                  <meshBasicMaterial color="#555555" transparent opacity={0.5} />
                </mesh>
              </group>
            ))
          )}
        </group>
        
        <OrbitControls 
          ref={controlsRef}
          target={cameraTarget}
          enablePan={cameraControls.enablePan}
          enableZoom={cameraControls.enableZoom}
          enableRotate={cameraControls.enableRotate}
          maxDistance={cameraControls.maxDistance}
          minDistance={cameraControls.minDistance}
          panSpeed={cameraControls.panSpeed}
          rotateSpeed={cameraControls.rotateSpeed}
          zoomSpeed={cameraControls.zoomSpeed}
        />
      </Suspense>
    </Canvas>
  );
}
