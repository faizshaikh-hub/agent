import React, { useState, useRef, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { addUserMessage, sendMessage, uploadFile } from '../../store/copilotSlice';
import { updateFormFields, setRiskAssessment, setStatus, setLoading } from '../../store/complaintSlice';
import LoadingDots from '../common/LoadingDots';
import './CopilotPanel.css';

export default function CopilotPanel() {
  const dispatch = useDispatch();
  const { messages, isProcessing, isConnected } = useSelector((state) => state.copilot);
  const formData = useSelector((state) => state.complaint.formData);
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isProcessing]);

  const handleSend = async () => {
    const text = inputValue.trim();
    if (!text || isProcessing) return;

    setInputValue('');
    dispatch(addUserMessage(text));
    dispatch(setLoading(true));

    try {
      const result = await dispatch(
        sendMessage({ message: text, currentFormState: formData })
      ).unwrap();

      // Apply form updates
      if (result.form_updates) {
        dispatch(updateFormFields(result.form_updates));
      }

      // Apply risk assessment
      if (result.risk_assessment) {
        dispatch(setRiskAssessment(result.risk_assessment));
      }

      // Update status
      if (result.status) {
        dispatch(setStatus(result.status));
      }
    } catch (error) {
      console.error('Send error:', error);
    } finally {
      dispatch(setLoading(false));
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    dispatch(addUserMessage(`📎 Uploaded: ${file.name}`));
    dispatch(setLoading(true));

    try {
      const result = await dispatch(uploadFile(file)).unwrap();

      if (result.form_updates) {
        dispatch(updateFormFields(result.form_updates));
      }
      if (result.risk_assessment) {
        dispatch(setRiskAssessment(result.risk_assessment));
      }
      if (result.status) {
        dispatch(setStatus(result.status));
      }
    } catch (error) {
      console.error('Upload error:', error);
    } finally {
      dispatch(setLoading(false));
      fileInputRef.current.value = '';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="copilot-panel">
      {/* Header */}
      <div className="copilot-header">
        <div className="copilot-header-left">
          <div className="copilot-avatar">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="11" width="18" height="11" rx="2" />
              <path d="M7 11V7a5 5 0 0110 0v4" />
              <circle cx="12" cy="16" r="1" />
            </svg>
          </div>
          <div>
            <h3 className="copilot-title">AIVOA Copilot</h3>
            <p className="copilot-subtitle">Drop complaint files or paste text below.</p>
          </div>
        </div>
        <div className={`copilot-status-dot ${isConnected ? 'connected' : ''}`}></div>
      </div>

      {/* Messages */}
      <div className="copilot-messages">
        {messages.map((msg) => (
          <div key={msg.id} className={`message message-${msg.role} ${msg.isError ? 'message-error' : ''}`}>
            {msg.role === 'assistant' && (
              <div className="message-icon">
                {msg.isError ? (
                  <span className="icon-error">⚠</span>
                ) : (
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6366f1" strokeWidth="2.5">
                    <path d="M22 11.08V12a10 10 0 11-5.93-9.14" />
                    <path d="M22 4L12 14.01l-3-3" />
                  </svg>
                )}
              </div>
            )}
            <div className="message-content">
              <p>{msg.content}</p>
            </div>
            {msg.role === 'user' && (
              <div className="message-user-icon">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
                  <circle cx="12" cy="7" r="4" />
                </svg>
              </div>
            )}
          </div>
        ))}

        {isProcessing && (
          <div className="message message-assistant">
            <div className="message-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6366f1" strokeWidth="2.5" className="icon-spin">
                <path d="M21 12a9 9 0 11-6.219-8.56" />
              </svg>
            </div>
            <LoadingDots />
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="copilot-input-area">
        <div className="copilot-input-container">
          <button
            className="input-attach-btn"
            onClick={() => fileInputRef.current?.click()}
            title="Upload complaint file"
            disabled={isProcessing}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48" />
            </svg>
          </button>
          <input
            ref={inputRef}
            type="text"
            className="copilot-input"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a message or paste a complaint..."
            disabled={isProcessing}
          />
          <button
            className="input-send-btn"
            onClick={handleSend}
            disabled={!inputValue.trim() || isProcessing}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path d="M5 12h14M12 5l7 7-7 7" />
            </svg>
          </button>
        </div>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.txt,.eml,.text,.html"
          style={{ display: 'none' }}
          onChange={handleFileUpload}
        />
        <div className="copilot-footer">
          <span>POWERED BY LANGGRAPH</span>
        </div>
      </div>
    </div>
  );
}
