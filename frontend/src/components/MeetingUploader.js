import React, { useState } from 'react';
import axios from 'axios';

function MeetingUploader({ setResults }) {
  const [file, setFile] = useState(null);
  const [language, setLanguage] = useState('en');
  const [notifySlack, setNotifySlack] = useState(false);
  const [channel, setChannel] = useState('');
  const [industry, setIndustry] = useState('General');
  const [userId, setUserId] = useState('anonymous');
  const [meetingTitle, setMeetingTitle] = useState('Untitled Meeting');
  const [customPromptDescription, setCustomPromptDescription] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const formData = new FormData();
    const inputData = {
      language,
      notify_slack: notifySlack,
      channel: notifySlack ? channel : '',
      industry,
      user_id: userId,
      meeting_title: meetingTitle,
      custom_prompt_description: customPromptDescription
    };
    formData.append('input', JSON.stringify(inputData));
    if (file) formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/process_meeting', formData);
      setResults(response.data.result);
    } catch (err) {
      setError('Error processing meeting: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="uploader-card"
      style={{
        maxWidth: 700,
        margin: '20px auto',
        padding: 24,
        borderRadius: 20,
        background: '#f0f4f9',
        boxShadow: '0 8px 24px rgba(0,0,0,0.08)',
        border: '1px solid #e0e4eb',
        fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
      }}
    >
      <h2 style={{ textAlign: 'center', marginBottom: 20, color: '#2c3e50' }}>Upload Meeting Audio</h2>
      <form onSubmit={handleSubmit}>
        {/* File Input */}
        <div className="mb-3">
          <label className="form-label" style={{ fontWeight: 500 }}>Audio File (max 25MB)</label>
          <input
            type="file"
            accept="audio/*"
            onChange={(e) => setFile(e.target.files[0])}
            className="form-control"
            style={{ borderRadius: 12, padding: '10px' }}
          />
          {file && <small style={{ color: '#2c3e50', fontStyle: 'italic' }}>Selected file: {file.name}</small>}
        </div>

        {/* Language & Industry */}
        <div className="row g-3 mb-3">
          <div className="col-md-6">
            <label className="form-label" style={{ fontWeight: 500 }}>Language</label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="form-select"
              style={{ borderRadius: 12, padding: '8px' }}
            >
              <option value="en">English</option>
              <option value="es">Spanish</option>
              <option value="fr">French</option>
              <option value="hi">Hindi</option>
              <option value="gu">Gujarati</option>
            </select>
          </div>
          <div className="col-md-6">
            <label className="form-label" style={{ fontWeight: 500 }}>Industry</label>
            <select
              value={industry}
              onChange={(e) => setIndustry(e.target.value)}
              className="form-select"
              style={{ borderRadius: 12, padding: '8px' }}
            >
              <option value="General">General</option>
              <option value="Finance">Finance</option>
              <option value="Healthcare">Healthcare</option>
              <option value="Marketing">Marketing</option>
              <option value="Education">Education</option>
            </select>
          </div>
        </div>

        {/* User ID & Meeting Title */}
        <div className="row g-3 mb-3">
          <div className="col-md-6">
            <label className="form-label" style={{ fontWeight: 500 }}>User ID</label>
            <input
              type="text"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              className="form-control"
              placeholder="Enter user ID"
              style={{ borderRadius: 12, padding: '8px' }}
            />
          </div>
          <div className="col-md-6">
            <label className="form-label" style={{ fontWeight: 500 }}>Meeting Title</label>
            <input
              type="text"
              value={meetingTitle}
              onChange={(e) => setMeetingTitle(e.target.value)}
              className="form-control"
              placeholder="Enter meeting title"
              style={{ borderRadius: 12, padding: '8px' }}
            />
          </div>
        </div>

        {/* Custom Prompt Description */}
        <div className="mb-3">
          <label className="form-label" style={{ fontWeight: 500 }}>Custom Prompt Description (optional)</label>
          <textarea
            value={customPromptDescription}
            onChange={(e) => setCustomPromptDescription(e.target.value)}
            className="form-control"
            placeholder="Describe how you want the AI to customize prompts"
            style={{ borderRadius: 12, padding: '8px' }}
          />
        </div>

        {/* Slack Notification */}
        <div className="form-check form-switch mb-3">
          <input
            type="checkbox"
            checked={notifySlack}
            onChange={(e) => setNotifySlack(e.target.checked)}
            className="form-check-input"
            id="notifySlackSwitch"
          />
          <label className="form-check-label" htmlFor="notifySlackSwitch">
            Notify via Slack
          </label>
        </div>
        {notifySlack && (
          <div className="mb-3">
            <label className="form-label" style={{ fontWeight: 500 }}>Slack Channel</label>
            <input
              type="text"
              value={channel}
              onChange={(e) => setChannel(e.target.value)}
              className="form-control"
              placeholder="Enter Slack channel"
              style={{ borderRadius: 12, padding: '8px', transition: 'all 0.3s ease' }}
            />
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          className="btn btn-primary w-100"
          disabled={loading || !file}
          style={{
            padding: '10px 20px',
            borderRadius: 12,
            fontWeight: 600,
            background: '#4caf50',
            border: 'none',
            transition: '0.2s all',
            cursor: loading || !file ? 'not-allowed' : 'pointer'
          }}
          onMouseEnter={(e) => e.target.style.background = '#45a049'}
          onMouseLeave={(e) => e.target.style.background = '#4caf50'}
        >
          {loading ? 'Processing...' : 'Process Meeting'}
        </button>

        {error && (
          <div
            className="alert alert-danger mt-3"
            style={{ borderRadius: 12, padding: '10px' }}
          >
            {error}
          </div>
        )}
      </form>
    </div>
  );
}

export default MeetingUploader;
