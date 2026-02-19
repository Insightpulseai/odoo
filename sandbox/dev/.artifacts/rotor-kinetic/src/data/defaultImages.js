export const defaultImages = {
  display: {
    url: 'https://i.ibb.co/Q77JknP4/Display.png',
    alt: 'Default display texture'
  },
  marquee: {
    url: '/marquee.jpg',
    alt: 'Default marquee texture'
  }
};

export const sceneConfig = {
  cameraFOV: 5,
  cameraPosition: [0, 0, 100],
  cameraTarget: [-2.90, -0.04, 0], // Default pan/target position for OrbitControls
  itemCount: 6,
  verticalGap: 3.0,
  groupRotation: [-0.4, 0, 0],
  cylinderRadius: 4.0,
  // Camera control settings
  cameraControls: {
    enablePan: true,
    enableZoom: true,
    enableRotate: true,
    maxDistance: 100,
    minDistance: 20,
    panSpeed: 1.0,
    rotateSpeed: 1.0,
    zoomSpeed: 1.0
  }
};