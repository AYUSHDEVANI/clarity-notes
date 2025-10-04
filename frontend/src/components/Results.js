import React, { useEffect } from "react";
import ReactMarkdown from "react-markdown";

function Results({ results }) {
  // Always call hooks first
  useEffect(() => {
    console.log("Results.js: Results received:", results);
  }, [results]);

  if (!results) {
    return (
      <div className="card p-4 text-center" style={{ borderRadius: 16 }}>
        No results available
      </div>
    );
  }

  // Clean Markdown-like symbols
  const cleanText = (text) => (text ? text.trim() : "");

  // Parse action items
  const parseActionItems = (actionsText) => {
    if (!actionsText) return [];
    let regex =
      /\* \*\*Description:\*\* (.*?)\s*\* \*\*Assignee:\*\* (.*?)\s*\* \*\*Deadline:\*\* (.*?)\s*\* \*\*Priority:\*\* (.*?)(?=\s*\* \*\*Description:\*\*|$)/gs;
    let matches = [...actionsText.matchAll(regex)];
    if (matches.length === 0) {
      regex =
        /Description:?\s*(.*?)\nAssignee:?\s*(.*?)\nDeadline:?\s*(.*?)\nPriority:?\s*(.*?)(?=\nDescription:|$)/gs;
      matches = [...actionsText.matchAll(regex)];
    }
    return matches.map((match) => ({
      description: cleanText(match[1]),
      assignee: cleanText(match[2]),
      deadline: cleanText(match[3]),
      priority: cleanText(match[4]),
    }));
  };

  let actionItems = [];
  if (results.actions) actionItems = parseActionItems(results.actions);
  else if (results.content) actionItems = parseActionItems(results.content);
  else if (results.summary && typeof results.summary === "string")
    actionItems = parseActionItems(results.summary);
  else if (results.summary?.summary)
    actionItems = parseActionItems(results.summary.summary);

  return (
    <div
      className="card p-4"
      style={{
        borderRadius: 20,
        background: "#f9faff",
        boxShadow: "0 8px 20px rgba(0,0,0,0.08)",
        fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
        color: "#2c3e50",
        maxWidth: "900px",
        margin: "20px auto",
      }}
    >
      <h2 style={{ marginBottom: 20, color: "#34495e" }}>Meeting Results</h2>

      {/* Summary */}
      <section style={{ marginBottom: 20 }}>
        <h3 style={{ color: "#2980b9" }}>Summary</h3>
        <div
          style={{
            background: "#eaf6ff",
            padding: "12px 16px",
            borderRadius: 12,
            lineHeight: 1.6,
            boxShadow: "inset 0 2px 6px rgba(0,0,0,0.05)",
          }}
        >
          <ReactMarkdown>
            {results.summary?.summary || results.summary || "No summary available"}
          </ReactMarkdown>
        </div>
      </section>

      {/* Sentiment */}
      {results.summary?.sentiment && (
        <section style={{ marginBottom: 20 }}>
          <h3 style={{ color: "#27ae60" }}>Sentiment</h3>
          <p
            style={{
              display: "inline-block",
              padding: "6px 12px",
              borderRadius: 12,
              background: "#e2f7e1",
              color: "#27ae60",
              fontWeight: 600,
            }}
          >
            {results.summary.sentiment || "Not determined"}
          </p>
        </section>
      )}

      {/* Action Items */}
      <section style={{ marginBottom: 20 }}>
        <h3 style={{ color: "#e67e22" }}>Action Items</h3>
        {actionItems.length > 0 ? (
          <div style={{ overflowX: "auto" }}>
            <table
              className="table"
              style={{
                minWidth: "650px",
                borderRadius: 12,
                overflow: "hidden",
                boxShadow: "0 4px 12px rgba(0,0,0,0.05)",
              }}
            >
              <thead style={{ background: "#f1f7ff" }}>
                <tr>
                  <th>Description</th>
                  <th>Assignee</th>
                  <th>Deadline</th>
                  <th>Priority</th>
                </tr>
              </thead>
              <tbody>
                {actionItems.map((item, index) => (
                  <tr
                    key={index}
                    style={{ transition: "all 0.2s", cursor: "pointer" }}
                    onMouseEnter={(e) => (e.currentTarget.style.background = "#f0f8ff")}
                    onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
                  >
                    <td>{item.description}</td>
                    <td>{item.assignee}</td>
                    <td>{item.deadline}</td>
                    <td>{item.priority}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p>No action items identified</p>
        )}
      </section>

      {/* Diarized Transcript */}
      <section>
        <h3 style={{ color: "#9b59b6" }}>Diarized Transcript</h3>
        <pre
          style={{
            background: "#faf7ff",
            borderRadius: 12,
            padding: 16,
            maxHeight: "300px",
            overflowY: "auto",
            boxShadow: "inset 0 2px 6px rgba(0,0,0,0.05)",
            whiteSpace: "pre-wrap",
          }}
        >
          <ReactMarkdown>
            {results.transcript?.diarized || results.transcript || "No transcript available"}
          </ReactMarkdown>
        </pre>
      </section>
    </div>
  );
}

export default Results;
