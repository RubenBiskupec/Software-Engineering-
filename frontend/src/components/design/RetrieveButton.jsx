import React from 'react';
import PropTypes from 'prop-types';

const RetrieveButton = (props) => {
  const { retrieve, handleRetrieveButton } = props;
  return (
    <button
      type="button"
      className={`btn btn-secondary mt-2 mb-2 btn-block ${
        retrieve ? 'disabled' : ''}`}
      onClick={handleRetrieveButton}
    >
      {retrieve ? (
        <div className="spinner-border" role="status">
          <span className="sr-only">Loading...</span>
        </div>
      ) : 'retrieve'}
    </button>
  );
};

RetrieveButton.propTypes = { retrieve: PropTypes.bool.isRequired };
RetrieveButton.propTypes = { handleRetrieveButton: PropTypes.func.isRequired };
export default RetrieveButton;
