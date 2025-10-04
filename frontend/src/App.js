import React, { useState, useEffect } from "react";
import MeetingUploader from "./components/MeetingUploader";
import Dashboard from "./components/Dashborad";
import RealTime from "./components/RealTime";
import Feedback from "./components/Feedback";
import Results from "./components/Results";
import ChatApp from "./components/Chat"; // Floating chat robot
// import Dashboard from "./components/Dashboard";
import "bootstrap/dist/css/bootstrap.min.css";
import * as bootstrap from "bootstrap";

function App() {
  const [results, setResults] = useState(null);
  const [activeTab, setActiveTab] = useState("upload");

  useEffect(() => {
    if (results) {
      setActiveTab("results");
      const resultsTab = document.querySelector("#results-tab");
      if (resultsTab) {
        const tab = new bootstrap.Tab(resultsTab);
        tab.show();
      }
    }
  }, [results]);

  return (
    <div
      className="container mt-5"
      style={{ fontFamily: "'Inter', sans-serif" }}
    >
      {/* Header */}
      <div className="d-flex align-items-center mb-4">
        <img
          src="https://tse2.mm.bing.net/th/id/OIP.uY3lHR2Bt_8SGSuDaVMnXAHaHa?cb=12&pid=Api" // New meeting notes logo
          alt="Project Logo"
          style={{ width: 56, height: 56, marginRight: 16, borderRadius: 12 }}
        />
        <h1
          className="fw-bold text-primary mb-0"
          style={{ fontSize: "2.2rem" }}
        >
          Clarity Notes
        </h1>
      </div>

      {/* Tabs */}
      <ul className="nav nav-tabs mb-4 bg-light rounded shadow-sm px-3 py-2">
        {[
          { id: "upload", icon: "bi-upload", label: "Upload" },
          { id: "real-time", icon: "bi-clock-history", label: "Real-Time" },
          { id: "feedback", icon: "bi-star", label: "Feedback" },
          { id: "results", icon: "bi-file-earmark-text", label: "Results" },
          { id: "dashboard", icon: "bi-bar-chart", label: "Dashboard" },
        ].map((tab) => (
          <li className="nav-item" key={tab.id}>
            <a
              className={`nav-link ${activeTab === tab.id ? "active" : ""}`}
              id={`${tab.id}-tab`}
              data-bs-toggle="tab"
              href={`#${tab.id}`}
              onClick={() => setActiveTab(tab.id)}
              style={{ fontWeight: 600, transition: "0.3s" }}
            >
              <i className={`bi ${tab.icon} me-1`}></i> {tab.label}
            </a>
          </li>
        ))}
      </ul>

      {/* Tab Content */}
      <div className="tab-content">
        <div
          className={`tab-pane fade ${
            activeTab === "upload" ? "active show" : ""
          }`}
          id="upload"
        >
          <MeetingUploader setResults={setResults} />
        </div>
        <div
          className={`tab-pane fade ${
            activeTab === "real-time" ? "active show" : ""
          }`}
          id="real-time"
        >
          <RealTime setResults={setResults} />
        </div>
        <div
          className={`tab-pane fade ${
            activeTab === "feedback" ? "active show" : ""
          }`}
          id="feedback"
        >
          <Feedback />
        </div>
        <div
          className={`tab-pane fade ${
            activeTab === "results" ? "active show" : ""
          }`}
          id="results"
        >
          <Results results={results} />
        </div>
        <div
          className={`tab-pane fade ${
            activeTab === "dashboard" ? "active show" : ""
          }`}
          id="dashboard"
        >
          <Dashboard />
        </div>
      </div>

      {/* Floating ChatApp */}
      <ChatApp />

      {/* Footer */}
      <footer
        className="text-center mt-5 py-3"
        style={{
          color: "#777",
          fontSize: "0.9rem",
          borderTop: "1px solid #e3e7ed",
        }}
      >
        &copy; {new Date().getFullYear()} Meeting Notes App. All rights
        reserved.
      </footer>

      {/* Global Styles */}
      <style>{`
        .tab-pane {
          background: #ffffff;
          border-radius: 16px;
          padding: 24px;
          box-shadow: 0 6px 20px rgba(0,0,0,0.08);
          transition: all 0.3s ease-in-out;
        }
        .nav-tabs .nav-link.active {
          background: #e0f0ff;
          border-radius: 12px;
          color: #0d6efd !important;
        }
        .nav-tabs .nav-link:hover {
          background: #f1f7ff;
          color: #0d6efd !important;
        }
      `}</style>
    </div>
  );
}

export default App;
