import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

// Custom material with gradient backface (matches MeshBannerMaterial from tutorial)
export class MeshMarqueeMaterial extends THREE.MeshBasicMaterial {
  constructor(parameters = {}) {
    super(parameters);
    this.setValues(parameters);
    this.backfaceRepeatX = 1.0;
    if (parameters.backfaceRepeatX !== undefined)
      this.backfaceRepeatX = parameters.backfaceRepeatX;
  }

  onBeforeCompile = (shader) => {
    shader.uniforms.repeatX = { value: this.backfaceRepeatX * 0.1 };
    shader.fragmentShader = shader.fragmentShader
      .replace(
        '#include <common>',
        /* glsl */ `#include <common>
        uniform float repeatX;
        vec3 pal( in float t, in vec3 a, in vec3 b, in vec3 c, in vec3 d ) {
          return a + b*cos( 6.28318*(c*t+d) );
        }
        `
      )
      .replace(
        '#include <color_fragment>',
        /* glsl */ `#include <color_fragment>
        if (!gl_FrontFacing) {
          diffuseColor.rgb = pal(vMapUv.x * repeatX, vec3(0.5,0.5,0.5),vec3(0.5,0.5,0.5),vec3(1.0,1.0,1.0),vec3(0.0,0.10,0.20) );
        }
        `
      );
  };
}

export function MarqueeStrip({ 
  position, 
  texture, 
  radius = 1.6, 
  animationSpeed = 0.001,
  textureRepeat = [15, 1], // How many times the texture repeats
  backfaceRepeatX = 3, // Controls gradient density on backface
  ...props 
}) {
  const ref = useRef();
  
  // Setup texture directly (like in tutorial)
  if (texture) {
    texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
    texture.repeat.set(textureRepeat[0], textureRepeat[1]);
  }
  
  useFrame((state, delta) => {
    // Animation exactly like the tutorial
    if (!ref.current) return;
    const material = ref.current.material;
    if (material.map) {
      material.map.offset.x += delta * animationSpeed;
    }
  });
  
  return (
    <mesh ref={ref} position={position} {...props}>
      <cylinderGeometry
        args={[radius, radius, radius * 0.07, radius * 80, radius * 10, true]}
      />
      <primitive object={new MeshMarqueeMaterial({
        map: texture,
        side: THREE.DoubleSide,
        toneMapped: false,
        backfaceRepeatX: backfaceRepeatX
      })} />
    </mesh>
  );
}