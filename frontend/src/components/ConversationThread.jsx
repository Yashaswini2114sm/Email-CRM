import './ConversationThread.css';

export default function ConversationThread({ messages }) {
  if (!messages || messages.length === 0) {
    return <div className="no-messages">No messages yet.</div>;
  }

  const formatTime = (dateString) => {
    return new Date(dateString).toLocaleTimeString(undefined, {
      hour: '2-digit', minute: '2-digit'
    });
  };

  return (
    <div className="conversation-thread">
      {messages.map((msg, index) => {
        const isCustomer = msg.sender_type === 'customer';
        const isAgent = msg.sender_type === 'agent';
        const isAi = msg.sender_type === 'ai';
        
        let wrapperClass = 'message-wrapper';
        if (isCustomer) wrapperClass += ' customer-msg';
        else wrapperClass += ' staff-msg';

        return (
          <div key={msg.id || index} className={wrapperClass}>
            <div className={`message-bubble ${msg.sender_type}`}>
              <div className="message-header">
                <span className="sender-name">
                  {isCustomer ? (msg.sender_email || 'Customer') : isAi ? 'AI Assistant' : 'Support Agent'}
                </span>
                <span className="message-time">{formatTime(msg.created_at)}</span>
              </div>
              <div className="message-content">
                {msg.content}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
