import * as THREE from 'three';

export class MeshMarqueeMaterial extends THREE.MeshBasicMaterial {
  constructor(parameters = {}) {
    // Enhanced parameters for better color reproduction
    const enhancedParams = {
      ...parameters,
      toneMapped: false, // Prevent tone mapping for true colors
    };
    
    super(enhancedParams);
    
    this.uniforms = {
      repeatX: { value: 1.0 },
      time: { value: 0.0 }
    };
    
    this.onBeforeCompile = (shader) => {
      // Add uniforms
      shader.uniforms.repeatX = this.uniforms.repeatX;
      shader.uniforms.time = this.uniforms.time;
      
      // Add palette function for gradient
      shader.fragmentShader = `
        uniform float repeatX;
        uniform float time;
        
        vec3 pal(float t, vec3 a, vec3 b, vec3 c, vec3 d) {
          return a + b * cos(6.28318 * (c * t + d));
        }
        
        ${shader.fragmentShader}
      `;
      
      // Enhanced shader for better color handling and animated gradient backface
      shader.fragmentShader = shader.fragmentShader.replace(
        '#include <output_fragment>',
        `
        #include <output_fragment>
        
        if (gl_FrontFacing) {
          // Enhance color saturation for front faces
          vec3 gray = vec3(dot(gl_FragColor.rgb, vec3(0.299, 0.587, 0.114)));
          gl_FragColor.rgb = mix(gray, gl_FragColor.rgb, 1.1);
          
          // Slight contrast boost
          gl_FragColor.rgb = pow(gl_FragColor.rgb, vec3(0.9));
        } else {
          // Animated gradient backface
          #ifdef USE_MAP
            vec2 mapUv = vMapUv;
          #else
            vec2 mapUv = vUv;
          #endif
          
          float t = mapUv.x * repeatX + time * 0.1;
          vec3 gradientColor = pal(t, 
            vec3(0.5,0.5,0.5), 
            vec3(0.4,0.3,0.5), 
            vec3(1.0,1.0,0.5), 
            vec3(0.8,0.9,0.3));
          gl_FragColor.rgb = gradientColor;
        }
        `
      );
    };
  }
  
  setRepeatX(value) {
    this.uniforms.repeatX.value = value;
  }
  
  updateTime(time) {
    this.uniforms.time.value = time;
  }
}