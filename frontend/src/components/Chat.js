import React, { useState, useEffect } from "react";
import io from "socket.io-client";
import axios from "axios";

const socket = io("http://localhost:8000", {
  transports: ["websocket", "polling"],
  reconnection: true,
  reconnectionAttempts: 5,
});

function ChatApp() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [isConnected, setIsConnected] = useState(socket.connected);
  const [meetings, setMeetings] = useState([]);
  const [selectedMeeting, setSelectedMeeting] = useState("");
  const [open, setOpen] = useState(false);

  useEffect(() => {
    // Fetch meetings initially
    const fetchMeetings = async () => {
      try {
        const response = await axios.get("http://localhost:8000/get_meetings");
        setMeetings(response.data.meetings);
        if (!selectedMeeting && response.data.meetings.length > 0) {
          setSelectedMeeting(response.data.meetings[0].meeting_id);
        }
      } catch (error) {
        console.error("Error fetching meetings:", error);
      }
    };
    fetchMeetings();

    // Socket events
    socket.on("connect", () => {
      setIsConnected(true);
      setMessages((prev) => [
        ...prev,
        { type: "status", content: "Connected to chat", timestamp: new Date().toLocaleString() },
      ]);
    });

    socket.on("disconnect", () => {
      setIsConnected(false);
      setMessages((prev) => [
        ...prev,
        { type: "status", content: "Disconnected from chat", timestamp: new Date().toLocaleString() },
      ]);
    });

    socket.on("message", (msg) => {
      setMessages((prev) => [
        ...prev,
        { ...msg, timestamp: msg.timestamp || new Date().toLocaleString() },
      ]);
    });

    // Listen for new meetings
    socket.on("new_meeting", (meeting) => {
      setMeetings((prev) => [meeting, ...prev]);
      setSelectedMeeting(meeting.meeting_id);
    });

    return () => {
      socket.off("connect");
      socket.off("disconnect");
      socket.off("message");
      socket.off("new_meeting");
    };
  }, [selectedMeeting]);

  const sendMessage = () => {
    if (!message.trim() || !selectedMeeting) return;

    socket.emit("message", {
      message,
      meeting_id: selectedMeeting,
      timestamp: new Date().toLocaleString(),
    });

    setMessages((prev) => [
      ...prev,
      { type: "message", content: `You: ${message}`, timestamp: new Date().toLocaleString() },
    ]);

    setMessage("");
  };

  return (
    <div>
      {/* Floating Robot Button */}
      <button
        onClick={() => setOpen(!open)}
        style={{
          position: "fixed",
          bottom: "20px",
          right: "20px",
          background: "#007bff",
          border: "none",
          borderRadius: "50%",
          width: "60px",
          height: "60px",
          boxShadow: "0 4px 12px rgba(0,0,0,0.2)",
          cursor: "pointer",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 2000,
        }}
      >
        <img
          src="https://img.icons8.com/color/40/000000/robot-2.png"
          alt="bot"
          style={{ width: 36, height: 36, objectFit: "cover", borderRadius: "50%" }}
        />
      </button>

      {/* Chat Window */}
      {open && (
        <div
          className="chat-ui card p-4"
          style={{
            position: "fixed",
            bottom: "70px",
            right: "70px",
            width: "380px",
            height: "520px",
            background: "#fff",
            borderRadius: "20px",
            boxShadow: "0 6px 18px rgba(0,0,0,0.25)",
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
            zIndex: 1999,
          }}
        >
          {/* Header */}
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 12 }}>
            <img src="https://img.icons8.com/color/40/000000/chat.png" alt="chat" style={{ marginRight: 10 }} />
            <h3 style={{ textAlign: "center", color: "#2c3e50", fontWeight: 700, margin: 0 }}>
              Live Chat Q&amp;A
            </h3>
          </div>

          {/* Status + Meeting Dropdown */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
            <span style={{ fontWeight: 500, color: isConnected ? "#27ae60" : "#c0392b" }}>
              {isConnected ? "🟢 Connected" : "🔴 Disconnected"}
            </span>
            <div style={{ minWidth: 200 }}>
              <select
                value={selectedMeeting}
                onChange={(e) => setSelectedMeeting(e.target.value)}
                className="form-select"
                disabled={!isConnected || meetings.length === 0}
                style={{ borderRadius: 10, fontWeight: 500, padding: 6 }}
              >
                {meetings.length === 0 ? (
                  <option value="">No meetings available</option>
                ) : (
                  meetings.map((m) => (
                    <option key={m.meeting_id} value={m.meeting_id}>
                      {m.meeting_title} ({new Date(m.timestamp).toLocaleString()})
                    </option>
                  ))
                )}
              </select>
            </div>
          </div>

          {/* Messages */}
          <div
            className="chat-messages"
            style={{
              background: "#f7faff",
              borderRadius: 16,
              padding: 14,
              flex: 1,
              overflowY: "auto",
              boxShadow: "inset 0 2px 6px rgba(0,0,0,0.05)",
              marginBottom: 8,
            }}
          >
            {messages.length === 0 && (
              <div style={{ textAlign: "center", color: "#888" }}>
                <img src="https://img.icons8.com/ios/40/888888/chat-message.png" alt="chat" style={{ marginBottom: 8 }} />
                <div>No messages yet. Start chatting to see Q&amp;A here.</div>
              </div>
            )}

            {messages.map((msg, i) => {
              const isUser = msg.content.startsWith("You:");
              return (
                <div
                  key={i}
                  style={{
                    display: "flex",
                    justifyContent: isUser ? "flex-end" : "flex-start",
                    alignItems: "flex-end",
                    marginBottom: 14,
                    gap: 8,
                  }}
                >
                  {!isUser && (
                    <img
                      src="https://img.icons8.com/color/40/000000/robot-2.png"
                      alt="bot"
                      style={{ width: 36, height: 36, objectFit: "cover", borderRadius: "50%" }}
                    />
                  )}

                  <div
                    style={{
                      background: isUser ? "#d1eaff" : "#eaf6ff",
                      borderRadius: 18,
                      padding: "10px 14px",
                      maxWidth: "70%",
                      boxShadow: "0 2px 6px rgba(0,0,0,0.08)",
                      wordBreak: "break-word",
                    }}
                  >
                    <span style={{ fontWeight: 500 }}>{msg.content}</span>
                    <div style={{ fontSize: "0.75em", color: "#888", marginTop: 4, textAlign: isUser ? "right" : "left" }}>
                      {msg.timestamp}
                    </div>
                  </div>

                  {isUser && (
                    <img
                      src="https://img.icons8.com/color/32/000000/user-male-circle.png"
                      alt="me"
                      style={{ width: 36, height: 36, objectFit: "cover", borderRadius: "50%" }}
                    />
                  )}
                </div>
              );
            })}
          </div>

          {/* Input */}
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              className="form-control"
              placeholder="Ask a question..."
              disabled={!isConnected || !selectedMeeting}
              style={{ borderRadius: 12, fontSize: "1em", padding: "10px 12px" }}
            />
            <button
              onClick={sendMessage}
              className="btn btn-primary"
              disabled={!isConnected || !selectedMeeting}
              style={{ fontWeight: 600, borderRadius: 12, minWidth: 80 }}
            >
              Send
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default ChatApp;
