import React from 'react';
import { useDispatch } from 'react-redux';
import Header from './components/Layout/Header';
import ComplaintForm from './components/ComplaintForm/ComplaintForm';
import CopilotPanel from './components/Copilot/CopilotPanel';
import { resetForm } from './store/complaintSlice';
import { resetChat } from './store/copilotSlice';
import './App.css';

function App() {
  const dispatch = useDispatch();

  const handleReset = () => {
    dispatch(resetForm());
    dispatch(resetChat());
  };

  const handleCommit = (data) => {
    console.log('Complaint committed:', data);
  };

  return (
    <div className="app">
      <Header onReset={handleReset} />
      <main className="app-main">
        <ComplaintForm onCommit={handleCommit} />
        <CopilotPanel />
      </main>
    </div>
  );
}

export default App;
