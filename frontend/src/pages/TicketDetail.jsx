import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../api/client';
import StatusBadge from '../components/StatusBadge';
import ConversationThread from '../components/ConversationThread';
import MessageInput from '../components/MessageInput';
import DocumentList from '../components/DocumentList';
import './TicketDetail.css';

export default function TicketDetail() {
  const { id } = useParams();
  const [ticket, setTicket] = useState(null);
  const [messages, setMessages] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isSending, setIsSending] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  useEffect(() => {
    fetchTicketData();
  }, [id]);

  const fetchTicketData = async () => {
    setLoading(true);
    try {
      const [tData, mData, dData] = await Promise.all([
        api.get(`/tickets/${id}`),
        api.get(`/tickets/${id}/messages`),
        api.get(`/tickets/${id}/documents`)
      ]);
      setTicket(tData);
      setMessages(mData);
      setDocuments(dData);
    } catch (err) {
      setError(err.message || 'Failed to load ticket details');
    } finally {
      setLoading(false);
    }
  };

  const handleSendReply = async (content) => {
    setIsSending(true);
    try {
      const newMsg = await api.post(`/tickets/${id}/messages`, {
        content,
        sender_type: 'agent'
      });
      setMessages(prev => [...prev, newMsg]);
    } catch (err) {
      alert(err.message || 'Failed to send reply');
    } finally {
      setIsSending(false);
    }
  };

  const handleDocumentUpload = async (file) => {
    const newDoc = await api.upload(`/tickets/${id}/documents`, file);
    setDocuments(prev => [...prev, newDoc]);
  };

  const handleGenerateAiReply = async () => {
    setIsAnalyzing(true);
    try {
      await api.post('/ai/generate-reply', { ticket_id: id });
      // Refresh messages to show the AI reply
      const mData = await api.get(`/tickets/${id}/messages`);
      setMessages(mData);
    } catch (err) {
      alert(err.message || 'Failed to generate AI reply');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleUpdateStatus = async (status) => {
    try {
      const updated = await api.patch(`/tickets/${id}`, { status });
      setTicket(updated);
    } catch (err) {
      alert(err.message || 'Failed to update status');
    }
  };

  if (loading) return <div className="loading">Loading ticket...</div>;
  if (error) return <div className="error-message">{error}</div>;
  if (!ticket) return <div className="error-message">Ticket not found</div>;

  return (
    <div className="ticket-detail-container">
      <div className="back-link">
        <Link to="/">← Back to Dashboard</Link>
      </div>

      <div className="ticket-header card">
        <div className="header-main">
          <h2>{ticket.subject}</h2>
          <div className="header-badges">
            <StatusBadge status={ticket.priority} type="priority" />
            <StatusBadge status={ticket.status} type="status" />
          </div>
        </div>
        
        <div className="ticket-meta">
          <div className="meta-item">
            <span className="meta-label">Customer:</span>
            <span>{ticket.customer_name || ticket.customer_email}</span>
          </div>
          <div className="meta-item">
            <span className="meta-label">Intent:</span>
            <span className="intent-tag">{ticket.intent || 'Unanalyzed'}</span>
          </div>
          <div className="meta-item">
            <span className="meta-label">Change Status:</span>
            <select 
              value={ticket.status} 
              onChange={e => handleUpdateStatus(e.target.value)}
              className="status-select"
            >
              <option value="open">Open</option>
              <option value="in_progress">In Progress</option>
              <option value="resolved">Resolved</option>
              <option value="closed">Closed</option>
            </select>
          </div>
        </div>
      </div>

      <div className="ticket-content">
        <div className="main-column">
          <div className="conversation-section">
            <div className="section-header">
              <h3>Conversation</h3>
              <button 
                className="secondary small-btn" 
                onClick={handleGenerateAiReply}
                disabled={isAnalyzing}
              >
                {isAnalyzing ? 'Generating...' : '✨ Suggest AI Reply'}
              </button>
            </div>
            <ConversationThread messages={messages} />
            <MessageInput onSend={handleSendReply} isLoading={isSending} />
          </div>
        </div>
        
        <div className="sidebar-column">
          <DocumentList 
            documents={documents} 
            onUpload={handleDocumentUpload} 
            isLoading={loading}
          />
        </div>
      </div>
    </div>
  );
}
