import React, { useState } from 'react';
import axios from 'axios';

function Feedback() {
  const [meetingId, setMeetingId] = useState('');
  const [rating, setRating] = useState(0);
  const [comments, setComments] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async () => {
    if (!meetingId || !rating) {
      setError('Meeting ID and rating are required');
      return;
    }
    try {
      const res = await axios.post('http://localhost:8000/feedback', {
        meeting_id: meetingId,
        rating,
        comments,
      });
      setMessage(res.data.status);
      setError('');
      setMeetingId('');
      setRating(0);
      setComments('');
    } catch (err) {
      setError('Error submitting feedback: ' + err.message);
      setMessage('');
    }
  };

  return (
    <div className="card p-4 mb-4">
      <h2>Submit Feedback</h2>
      <div className="mb-3">
        <input
          type="text"
          placeholder="Meeting ID"
          value={meetingId}
          onChange={(e) => setMeetingId(e.target.value)}
          className="form-control"
        />
      </div>
      <div className="mb-3">
        <label className="form-label">Rating (1-5)</label>
        <input
          type="number"
          min="1"
          max="5"
          value={rating}
          onChange={(e) => setRating(Number(e.target.value))}
          className="form-control"
        />
      </div>
      <div className="mb-3">
        <textarea
          placeholder="Comments"
          value={comments}
          onChange={(e) => setComments(e.target.value)}
          className="form-control"
        />
      </div>
      <button onClick={handleSubmit} className="btn btn-primary">
        Submit Feedback
      </button>
      {message && <div className="alert alert-success mt-3">{message}</div>}
      {error && <div className="alert alert-danger mt-3">{error}</div>}
    </div>
  );
}

export default Feedback;