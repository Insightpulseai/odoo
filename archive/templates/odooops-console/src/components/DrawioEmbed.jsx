import React, { useEffect, useRef } from 'react';

/**
 * DrawioEmbed component for bidirectional integration with diagrams.net.
 * Uses the postMessage API to load and save diagram data.
 */
const DrawioEmbed = ({ xml, onSave, onExit }) => {
  const iframeRef = useRef(null);

  useEffect(() => {
    const handleMessage = (event) => {
      if (event.origin !== 'https://embed.diagrams.net') return;

      const data = JSON.parse(event.data);

      if (data.event === 'init') {
        // Load the initial XML into the editor
        iframeRef.current.contentWindow.postMessage(
          JSON.stringify({ action: 'load', xml: xml }),
          '*'
        );
      } else if (data.event === 'save') {
        // User clicked Save - transmit the updated XML back to the parent
        onSave(data.xml);
        // Acknowledge the save to the editor
        iframeRef.current.contentWindow.postMessage(
          JSON.stringify({ action: 'status', message: 'Saved successfully', modified: false }),
          '*'
        );
      } else if (data.event === 'exit') {
        onExit();
      }
    };

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [xml, onSave, onExit]);

  // URL parameters for the embed mode
  const embedParams = new URLSearchParams({
    embed: '1',
    ui: 'atlas', // Premium UI theme
    spin: '1',
    proto: 'json',
    configure: '1' // Allows for custom color injection
  });

  return (
    <div style={{ width: '100%', height: '800px', border: '1px solid #ddd' }}>
      <iframe
        ref={iframeRef}
        src={`https://embed.diagrams.net/?${embedParams.toString()}`}
        width="100%"
        height="100%"
        frameBorder="0"
      />
    </div>
  );
};

export default DrawioEmbed;
