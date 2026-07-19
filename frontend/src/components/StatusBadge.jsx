import './StatusBadge.css';

export default function StatusBadge({ status, type = 'status' }) {
  const getBadgeClass = () => {
    if (type === 'status') {
      switch (status) {
        case 'open': return 'badge-status-open';
        case 'in_progress': return 'badge-status-progress';
        case 'resolved': return 'badge-status-resolved';
        case 'closed': return 'badge-status-closed';
        default: return '';
      }
    } else if (type === 'priority') {
      switch (status) {
        case 'low': return 'badge-priority-low';
        case 'medium': return 'badge-priority-medium';
        case 'high': return 'badge-priority-high';
        case 'urgent': return 'badge-priority-urgent';
        default: return '';
      }
    }
    return '';
  };

  const formatText = (text) => {
    if (!text) return '';
    return text.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
  };

  return (
    <span className={`badge ${getBadgeClass()}`}>
      {formatText(status)}
    </span>
  );
}
