import React from 'react';
import './StatusBadge.css';

export default function StatusBadge({ status }) {
  const getConfig = () => {
    switch (status) {
      case 'ready_to_commit':
        return { label: 'Ready to Commit', className: 'badge-ready' };
      case 'committed':
        return { label: 'Committed', className: 'badge-committed' };
      case 'pending_triage':
      default:
        return { label: 'Pending Triage', className: 'badge-pending' };
    }
  };

  const config = getConfig();

  return (
    <span className={`status-badge ${config.className}`}>
      <span className="badge-dot"></span>
      {config.label}
    </span>
  );
}
