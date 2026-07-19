import { Link } from 'react-router-dom';
import StatusBadge from './StatusBadge';
import './TicketCard.css';

export default function TicketCard({ ticket }) {
  const date = new Date(ticket.created_at).toLocaleDateString(undefined, {
    month: 'short', day: 'numeric', year: 'numeric'
  });

  return (
    <Link to={`/tickets/${ticket.id}`} className="ticket-card card">
      <div className="ticket-card-header">
        <h3 className="ticket-subject">{ticket.subject}</h3>
        <div className="ticket-badges">
          <StatusBadge status={ticket.priority} type="priority" />
          <StatusBadge status={ticket.status} type="status" />
        </div>
      </div>
      
      <div className="ticket-card-body">
        <div className="ticket-info">
          <span className="info-label">Customer:</span>
          <span className="info-value">{ticket.customer_name || ticket.customer_email}</span>
        </div>
        
        {ticket.intent && (
          <div className="ticket-info">
            <span className="info-label">Intent:</span>
            <span className="info-value badge-intent">{ticket.intent}</span>
          </div>
        )}
      </div>
      
      <div className="ticket-card-footer">
        <span className="ticket-date">Created on {date}</span>
      </div>
    </Link>
  );
}
