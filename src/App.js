import React, { useRef, useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import './App.css';  // Ensure this file exists for styles
import { endpoints } from './config';

  // Define your API base URL here

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
  const [isPaused, setIsPaused] = useState(false);

  const handleDetectFall = useCallback(async (frame, retries = 3) => {
    try {
      const response = await axios.post(endpoints.detectFall, { frame });
      return response;
    } catch (error) {
      if (retries > 0) {
        console.warn(`Retrying... (${retries} attempts left)`);
        return handleDetectFall(frame, retries - 1);
      }
      throw error;
    }
  }, []);

  const handlePause = useCallback(async () => {
    try {
      const response = await axios.post(endpoints.togglePause);
      setIsPaused(response.data.paused);
      
      if (response.data.paused) {
        const { data: { frames } } = await axios.get(endpoints.getPreviousFrames);
        if (canvasRef.current && frames?.length) {
          for (const frame of frames) {
            const img = new Image();
            await new Promise((resolve, reject) => {
              img.onload = resolve;
              img.onerror = reject;
              img.src = frame.frame;
            });
            const context = canvasRef.current.getContext('2d');
            context.drawImage(img, 0, 0, canvasRef.current.width, canvasRef.current.height);
            await new Promise(resolve => setTimeout(resolve, 1000/30));
          }
        }
      }
    } catch (error) {
      console.error("Error toggling pause:", error);
      setError("Failed to toggle pause. Please try again.");
    }
  }, [canvasRef]); 
  
  useEffect(() => {
    const detectFall = async () => {
      if (videoRef.current && canvasRef.current && !isPaused) {
        const startTime = performance.now();
        const video = videoRef.current;
        const canvas = canvasRef.current;
        const context = canvas.getContext('2d');

        context.drawImage(video, 0, 0, canvas.width / 2, canvas.height / 2);
        const frame = canvas.toDataURL('image/jpeg', 0.7);

        try {
          const response = await handleDetectFall(frame);
          setFallDetected(response.data.fall_detected);
      
          if (response.data.annotated_frame) {
            const img = new Image();
            img.onload = () => {
              const context = canvasRef.current.getContext('2d');
              context.drawImage(img, 0, 0, canvas.width, canvas.height);
            };
            img.src = response.data.annotated_frame;
          }
      
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
  }, [isPaused, handleDetectFall]); // Added handleDetectFall to dependencies

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