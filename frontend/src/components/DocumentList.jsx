import { useState } from 'react';
import './DocumentList.css';

export default function DocumentList({ documents, onUpload, isLoading }) {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Check size (10MB max)
    if (file.size > 10 * 1024 * 1024) {
      setError('File must be smaller than 10MB');
      return;
    }

    setIsUploading(true);
    setError(null);
    try {
      await onUpload(file);
    } catch (err) {
      setError(err.message || 'Failed to upload document');
    } finally {
      setIsUploading(false);
      e.target.value = ''; // Reset input
    }
  };

  const formatSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    else return (bytes / 1048576).toFixed(1) + ' MB';
  };

  return (
    <div className="document-list-container">
      <div className="document-header">
        <h3>Documents</h3>
        <label className="upload-btn">
          {isUploading ? 'Uploading...' : 'Upload File'}
          <input 
            type="file" 
            onChange={handleFileChange} 
            disabled={isUploading || isLoading}
            style={{ display: 'none' }}
          />
        </label>
      </div>

      {error && <div className="error-message">{error}</div>}

      {documents.length === 0 ? (
        <p className="no-documents">No documents attached.</p>
      ) : (
        <ul className="document-list">
          {documents.map(doc => (
            <li key={doc.id} className="document-item">
              <div className="doc-info">
                <span className="doc-name">{doc.filename}</span>
                <span className="doc-size">{formatSize(doc.file_size)}</span>
              </div>
              {doc.is_valid !== null && (
                <span className={`doc-validation ${doc.is_valid ? 'valid' : 'invalid'}`}>
                  {doc.is_valid ? 'Valid' : 'Invalid'}
                </span>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
