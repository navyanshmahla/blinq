import '../styles/chat.css';

function CSVStatus({ csvStatus, csvFilename, csvExpiry }) {
  const calculateDaysRemaining = (expiryDate) => {
    const now = new Date();
    const expiry = new Date(expiryDate);
    const diffTime = expiry - now;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  if (!csvStatus || csvStatus === 'none') {
    return (
      <div className="csv-status csv-status-none">
        <div className="csv-status-content">
          <span className="csv-status-icon">📄</span>
          <span className="csv-status-text">No CSV uploaded</span>
        </div>
        <button className="csv-upload-btn">Upload CSV</button>
      </div>
    );
  }

  if (csvStatus === 'expired') {
    return (
      <div className="csv-status csv-status-expired">
        <div className="csv-status-content">
          <span className="csv-status-icon">⚠️</span>
          <span className="csv-status-text">CSV expired - Re-upload to continue</span>
        </div>
        <button className="csv-upload-btn">Upload CSV</button>
      </div>
    );
  }

  if (csvStatus === 'active') {
    const daysRemaining = calculateDaysRemaining(csvExpiry);
    return (
      <div className="csv-status csv-status-active">
        <div className="csv-status-content">
          <span className="csv-status-icon">✓</span>
          <div className="csv-status-info">
            <span className="csv-status-filename">{csvFilename}</span>
            <span className="csv-status-expiry">
              Expires in {daysRemaining} {daysRemaining === 1 ? 'day' : 'days'}
            </span>
          </div>
        </div>
        <button className="csv-replace-btn">Replace</button>
      </div>
    );
  }

  return null;
}

export default CSVStatus;
