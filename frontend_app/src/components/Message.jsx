import '../styles/chat.css';

function Message({ message }) {
  return (
    <div className={`message ${message.role}`}>
      <div className="message-content">
        <div className="message-text">{message.content}</div>
        {message.hasPlot && (
          <div className="message-plot-placeholder">
            [Plot visualization would appear here]
          </div>
        )}
        {message.cost && (
          <div className="message-meta">Cost: ${message.cost.toFixed(4)}</div>
        )}
      </div>
    </div>
  );
}

export default Message;
