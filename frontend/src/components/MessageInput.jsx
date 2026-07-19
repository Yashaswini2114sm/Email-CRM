import { useState } from 'react';
import './MessageInput.css';

export default function MessageInput({ onSend, isLoading }) {
  const [message, setMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!message.trim() || isLoading) return;
    
    onSend(message);
    setMessage('');
  };

  return (
    <form className="message-input-form" onSubmit={handleSubmit}>
      <textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Type your reply here..."
        rows={3}
        disabled={isLoading}
      />
      <div className="input-actions">
        <button type="submit" className="primary" disabled={!message.trim() || isLoading}>
          {isLoading ? 'Sending...' : 'Send Reply'}
        </button>
      </div>
    </form>
  );
}
