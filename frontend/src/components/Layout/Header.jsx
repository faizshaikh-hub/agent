import React from 'react';
import './Header.css';
import { FiRefreshCw } from 'react-icons/fi';

export default function Header({ onReset }) {
  return (
    <header className="app-header">
      <div className="header-left">
        <div className="header-logo">
          <div className="logo-icon">
            <svg width="28" height="28" viewBox="0 0 32 32" fill="none">
              <rect width="32" height="32" rx="8" fill="url(#logo-grad)" />
              <path d="M8 22L16 10L24 22H8Z" fill="white" opacity="0.9" />
              <circle cx="16" cy="18" r="3" fill="white" />
              <defs>
                <linearGradient id="logo-grad" x1="0" y1="0" x2="32" y2="32">
                  <stop stopColor="#6366f1" />
                  <stop offset="1" stopColor="#8b5cf6" />
                </linearGradient>
              </defs>
            </svg>
          </div>
          <div className="header-title-group">
            <h1 className="header-title">AIVOA<span className="header-title-dot">.</span>QMS</h1>
            <span className="header-subtitle">Customer Complaint Module</span>
          </div>
        </div>
      </div>
      <div className="header-right">
        <button className="header-btn" onClick={onReset} title="New Complaint">
          <FiRefreshCw size={16} />
          <span>New Complaint</span>
        </button>
      </div>
    </header>
  );
}
