import * as THREE from 'three';

export class MeshDisplayMaterial extends THREE.MeshBasicMaterial {
  constructor(parameters = {}) {
    // Enhanced parameters for better color reproduction
    const enhancedParams = {
      ...parameters,
      toneMapped: false, // Prevent tone mapping for true colors
      transparent: true, // Enable transparency
      alphaTest: 0.1, // Discard pixels with alpha < 0.1
    };
    
    super(enhancedParams);
    
    this.onBeforeCompile = (shader) => {
      // Enhanced shader for better color handling and darkened backface
      shader.fragmentShader = shader.fragmentShader.replace(
        '#include <color_fragment>',
        `
        #include <color_fragment>
        
        // Apply backface darkening BEFORE output processing
        if (!gl_FrontFacing) {
          vec3 blackCol = vec3(0.0);
          diffuseColor.rgb = mix(diffuseColor.rgb, blackCol, 0.8);
        }
        `
      ).replace(
        '#include <output_fragment>',
        `
        #include <output_fragment>
        
        // Enhance color saturation and contrast for front faces only
        if (gl_FrontFacing) {
          // Increase saturation slightly
          vec3 gray = vec3(dot(gl_FragColor.rgb, vec3(0.299, 0.587, 0.114)));
          gl_FragColor.rgb = mix(gray, gl_FragColor.rgb, 1.1);
          
          // Slight contrast boost
          gl_FragColor.rgb = pow(gl_FragColor.rgb, vec3(0.9));
        }
        `
      );
    };
  }
}