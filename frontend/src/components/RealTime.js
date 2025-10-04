import React, { useState, useEffect } from 'react';
import axios from 'axios';

function RealTime({ setResults }) {
  const [recording, setRecording] = useState(false);
  const [language, setLanguage] = useState('en');
  const [industry, setIndustry] = useState('General');
  const [userId, setUserId] = useState('anonymous');
  const [meetingTitle, setMeetingTitle] = useState('Real-Time Meeting');
  const [customPromptDescription, setCustomPromptDescription] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchResults = async () => {
    setLoading(true);
    try {
      const resultRes = await axios.get('http://localhost:8000/get_transcription_results');
      setResults(resultRes.data);
      setError('');
    } catch (err) {
      const errorMessage = err.response?.status === 404
        ? 'Transcription results not available. Please try recording again.'
        : 'Error fetching transcription results: ' + (err.response?.data?.detail || err.message);
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleStartRecording = async () => {
    setError('');
    setRecording(true);
    try {
      const res = await axios.post('http://localhost:8000/real_time_transcribe', {
        language,
        industry,
        user_id: userId,
        meeting_title: meetingTitle,
        custom_prompt_description: customPromptDescription
      });
      if (res.data.status === 'Recording started') {
        setTimeout(fetchResults, 35000);
      }
    } catch (err) {
      const errorMessage = 'Error starting real-time transcription: ' + (err.response?.data?.detail || err.message);
      setError(errorMessage);
      setRecording(false);
    }
  };

  const handleStopRecording = async () => {
    try {
      const res = await axios.post('http://localhost:8000/stop_recording');
      setRecording(false);
      if (res.data.status === 'Recording stopped') {
        await fetchResults();
      }
    } catch (err) {
      const errorMessage = 'Error stopping recording: ' + (err.response?.data?.detail || err.message);
      setError(errorMessage);
      setRecording(false);
    }
  };

  return (
    <div className="card p-4 mb-4">
      <h2>Real-Time Transcription</h2>
      <div className="mb-3">
        <label className="form-label">Language</label>
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          className="form-select"
          disabled={recording}
        >
          <option value="en">English</option>
          <option value="es">Spanish</option>
          <option value="fr">French</option>
          <option value="hi">Hindi</option>
          <option value="gu">Gujarati</option>
        </select>
      </div>
      <div className="mb-3">
        <label className="form-label">Industry</label>
        <select
          value={industry}
          onChange={(e) => setIndustry(e.target.value)}
          className="form-select"
          disabled={recording}
        >
          <option value="General">General</option>
          <option value="Finance">Finance</option>
          <option value="Healthcare">Healthcare</option>
          <option value="Marketing">Marketing</option>
          <option value="Education">Education</option>
        </select>
      </div>
      <div className="mb-3">
        <label className="form-label">User ID</label>
        <input
          type="text"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          className="form-control"
          placeholder="Enter user ID"
          disabled={recording}
        />
      </div>
      <div className="mb-3">
        <label className="form-label">Meeting Title</label>
        <input
          type="text"
          value={meetingTitle}
          onChange={(e) => setMeetingTitle(e.target.value)}
          className="form-control"
          placeholder="Enter meeting title"
          disabled={recording}
        />
      </div>
      <div className="mb-3">
        <label className="form-label">Custom Prompt Description (for dynamic AI prompt)</label>
        <textarea
          value={customPromptDescription}
          onChange={(e) => setCustomPromptDescription(e.target.value)}
          className="form-control"
          placeholder="Describe how you want the AI to customize the prompts (optional)"
          disabled={recording}
        />
      </div>
      <div className="mb-3">
        <button
          onClick={handleStartRecording}
          className="btn btn-success me-2"
          disabled={recording || loading}
        >
          Start Recording
        </button>
        <button
          onClick={handleStopRecording}
          className="btn btn-danger"
          disabled={!recording || loading}
        >
          Stop Recording
        </button>
      </div>
      {loading && <div className="alert alert-info mt-3">Fetching results...</div>}
      {error && <div className="alert alert-danger mt-3">{error}</div>}
      <p className="mt-3">Records up to 30 seconds of audio. Results will appear below.</p>
    </div>
  );
}

export default RealTime;