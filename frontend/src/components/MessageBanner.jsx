function MessageBanner({ message, type = "info", onClose }) {
  if (!message) {
    return null;
  }

  const bannerClass = `message-banner message-banner--${type}`;

  return (
    <div className={bannerClass} role="alert">
      <span>{message}</span>

      {onClose && (
        <button
          type="button"
          className="message-banner__close"
          onClick={onClose}
          aria-label="Close message"
        >
          ×
        </button>
      )}
    </div>
  );
}

export default MessageBanner;
