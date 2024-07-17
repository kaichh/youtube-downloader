import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [url, setUrl] = useState("");
  const [videoInfo, setVideoInfo] = useState(null);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setVideoInfo(null);

    try {
      const response = await axios.post(
        "http://localhost:8000/api/video-info/",
        { url }
      );
      setVideoInfo(response.data);
    } catch (err) {
      setError(
        "Error fetching video info. Please check the URL and try again."
      );
    }
  };

  const handleDownload = async (format, info) => {
    try {
      const response = await axios.post(
        "http://localhost:8000/api/download/",
        { url, format },
        { responseType: "blob" }
      );
      const blob = new Blob([response.data]);
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.download = `${info.title}.${format}`;
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      setError("Error downloading video. Please try again.");
    }
  };

  return (
    <div className="App">
      <h1>YouTube Video Downloader</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Enter YouTube URL"
          required
        />
        <button type="submit">Get Video Info</button>
      </form>
      {error && <p className="error">{error}</p>}
      {videoInfo && (
        <div className="video-info">
          <h2>{videoInfo.title}</h2>
          <p>Author: {videoInfo.author}</p>
          <p>
            Duration: {Math.floor(videoInfo.duration / 60)}:
            {videoInfo.duration % 60}
          </p>
          <img src={videoInfo.thumbnail} alt="Video thumbnail" />
          <p>{videoInfo.description}</p>
          <div className="download-buttons">
            <button onClick={() => handleDownload("mp4", videoInfo)}>
              Download Video (MP4)
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
