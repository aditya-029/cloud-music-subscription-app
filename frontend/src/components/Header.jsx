function Header({ user, onLogout }) {
  return (
    <header className="app-header">
      <div className="app-header__brand">
        <span className="app-logo">♪</span>
        <div>
          <h1>Cloud Music Subscription App</h1>
          <p>AWS-powered music search and subscription dashboard</p>
        </div>
      </div>

      <div className="app-header__user">
        <div className="user-summary">
          <span>Welcome,</span>
          <strong>{user?.user_name || "User"}</strong>
          <small>{user?.email}</small>
        </div>

        <button
          type="button"
          className="button button--ghost"
          onClick={onLogout}
        >
          Logout
        </button>
      </div>
    </header>
  );
}

export default Header;
