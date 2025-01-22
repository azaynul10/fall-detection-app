// src/App.js
import React, { useRef, useEffect, useState } from 'react';
import axios from 'axios';
import './App.css';  // Create this file for styles

function App() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [fallDetected, setFallDetected] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({
    fps: 0,
    detectionTime: 0
  });
  const [previousFrames, setPreviousFrames] = useState([]);
  const [isPaused, setIsPaused] = useState(false); // Added isPaused state

  const handlePause = async () => {
    try {
      const response = await axios.post('http://localhost:5000/toggle_pause');
      setIsPaused(response.data.paused);
      
      if (response.data.paused) {
        // Create a separate container for previous frames
        const playbackContainer = document.createElement('div');
        playbackContainer.className = 'playback-overlay';
        document.querySelector('.video-container').appendChild(playbackContainer);
  
        const framesResponse = await axios.get('http://localhost:5000/get_previous_frames');
        setPreviousFrames(framesResponse.data.frames);
        
        for (let frame of framesResponse.data.frames) {
          if (canvasRef.current) {
            const img = new Image();
            await new Promise((resolve) => {
              img.onload = () => {
                const context = canvasRef.current.getContext('2d');
                context.drawImage(img, 0, 0, canvasRef.current.width, canvasRef.current.height);
                resolve();
              };
              img.src = frame.frame;
            });
            await new Promise(resolve => setTimeout(resolve, 1000/30));
          }
        }
        
        // Remove playback container after playback
        playbackContainer.remove();
      }
    } catch (error) {
      console.error("Error toggling pause:", error);
    }
  };

  // Add keyboard event listener
  useEffect(() => {
    const handleKeyPress = async (event) => {
      if (event.key === 'p' || event.key === 'P') {
        try {
          const response = await axios.post('http://localhost:5000/toggle_pause');
          setIsPaused(response.data.paused);
        } catch (error) {
          console.error("Error toggling pause:", error);
        }
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, []);

  useEffect(() => {
    const detectFall = async () => {
      if (videoRef.current && canvasRef.current) {
        const startTime = performance.now();
        const video = videoRef.current;
        const canvas = canvasRef.current;
        const context = canvas.getContext('2d');

        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        const frame = canvas.toDataURL('image/jpeg');

        try {
          const response = await axios.post('http://localhost:5000/detect_fall', { frame });
          setFallDetected(response.data.fall_detected);
      
          // Display the annotated frame with pose landmarks
          if (response.data.annotated_frame) {
            const img = new Image();
            img.onload = () => {
              const context = canvasRef.current.getContext('2d');
              context.drawImage(img, 0, 0, canvas.width, canvas.height);
            };
            img.src = response.data.annotated_frame;
          }
      
          // Update stats
          const endTime = performance.now();
          setStats({
            fps: Math.round(1000 / (endTime - startTime)),
            detectionTime: Math.round(endTime - startTime)
          });
        } catch (error) {
          console.error("Error detecting fall:", error);
          setError("Detection service unavailable");
        }
      }
    };
  
    const interval = setInterval(detectFall, 1000);
    return () => clearInterval(interval);
  }, []);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          width: 640,
          height: 480,
          facingMode: 'user'
        } 
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setIsLoading(false);
      }
    } catch (err) {
      console.error("Error accessing the camera:", err);
      setError("Camera access denied. Please check permissions.");
      setIsLoading(false);
    }
  };

  useEffect(() => {
    startCamera();
  }, []);

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Fall Detection System</h1>
        <div className="stats-container">
          <div className="stat-item">
            <span>FPS:</span>
            <span>{stats.fps}</span>
          </div>
          <div className="stat-item">
            <span>Detection Time:</span>
            <span>{stats.detectionTime}ms</span>
          </div>
        </div>
      </header>

      <main className="main-content">
        <div className="video-container">
          {isLoading && (
            <div className="loading-overlay">
              <div className="spinner"></div>
              <p>Initializing Camera...</p>
            </div>
          )}
          
          <video 
            ref={videoRef} 
            autoPlay 
            playsInline
            className="video-feed" 
          />
          <canvas 
            ref={canvasRef} 
            width={640} 
            height={480} 
            className="detection-overlay"
          />
          
          <div className="controls">
            <button onClick={handlePause} className="control-button">
              {isPaused ? 'Resume' : 'Pause'}
            </button>
          </div>
          
          {fallDetected && (
            <div className="alert-overlay">
              <div className="alert-content">
                <span className="alert-icon">⚠️</span>
                <h2>Fall Detected!</h2>
                <p>Emergency services notified</p>
              </div>
            </div>
          )}
        </div>
        
        {error && (
          <div className="error-message">
            <p>{error}</p>
            <button onClick={() => window.location.reload()}>
              Retry
            </button>
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>Real-time Fall Detection System v1.0 by Zaynul Abedin Miah</p>
      </footer>
    </div>
  );
}

export default App;