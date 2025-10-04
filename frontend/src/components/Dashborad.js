import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";

function Dashboard() {
  const [meetings, setMeetings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchInsights = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get("http://localhost:8000/get_meetings");
      setMeetings(res.data.meetings || []);
    } catch (err) {
      console.error("Error fetching insights:", err);
      setError("Failed to load data. Please check backend.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInsights();
  }, []);

  if (loading) return <p className="text-center mt-5">⏳ Loading insights...</p>;

  if (error)
    return (
      <div className="text-center mt-5">
        <p className="text-danger">{error}</p>
        <button className="btn btn-primary mt-3" onClick={fetchInsights}>
          Retry
        </button>
      </div>
    );

  if (!meetings.length)
    return (
      <div className="text-center mt-5">
        <p>No meeting data found. Upload or record a meeting first.</p>
        <button className="btn btn-primary mt-3" onClick={fetchInsights}>
          Refresh
        </button>
      </div>
    );

  // Format meeting data for charts
  const meetingTrend = meetings.map((m, i) => ({
    name: m.meeting_title || `Meeting ${i + 1}`,
    date: new Date(m.timestamp).toLocaleDateString(),
    index: i + 1,
  }));

  const industryCounts = meetings.reduce((acc, m) => {
    const industry = m.industry || "General";
    acc[industry] = (acc[industry] || 0) + 1;
    return acc;
  }, {});

  const industryData = Object.keys(industryCounts).map((key) => ({
    name: key,
    value: industryCounts[key],
  }));

  const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#845EC2"];

  return (
    <div className="dashboard container mt-4">
      <h2 className="fw-bold mb-4">📊 Meeting Insights Dashboard</h2>

      {/* Line Chart: Meeting Trends */}
      <div className="card p-4 mb-4 shadow-sm">
        <h5 className="mb-3">Meetings Over Time</h5>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={meetingTrend}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="index" stroke="#0d6efd" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Pie Chart: Industry Distribution */}
      <div className="card p-4 shadow-sm">
        <h5 className="mb-3">Meetings by Industry</h5>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={industryData}
              cx="50%"
              cy="50%"
              outerRadius={100}
              fill="#8884d8"
              dataKey="value"
              label
            >
              {industryData.map((_, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={COLORS[index % COLORS.length]}
                />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default Dashboard;
