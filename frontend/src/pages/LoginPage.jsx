import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { loginUser } from "../api/apiClient";
import { saveSession } from "../utils/session";
import MessageBanner from "../components/MessageBanner";

function LoginPage() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("error");
  const [loading, setLoading] = useState(false);

  function handleChange(event) {
    const { name, value } = event.target;

    setFormData((currentData) => ({
      ...currentData,
      [name]: value,
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();

    setMessage("");

    if (!formData.email.trim() || !formData.password.trim()) {
      setMessageType("error");
      setMessage("email or password is invalid");
      return;
    }

    try {
      setLoading(true);

      const response = await loginUser(
        formData.email.trim(),
        formData.password.trim(),
      );

      saveSession(response.data);
      navigate("/main");
    } catch (error) {
      setMessageType("error");
      setMessage(error.message || "email or password is invalid");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card">
        <div className="auth-card__header">
          <span className="app-logo app-logo--large">♪</span>
          <h1>Cloud Music Subscription App</h1>
          <p>Log in to search, subscribe, and manage your music library.</p>
        </div>

        <MessageBanner
          message={message}
          type={messageType}
          onClose={() => setMessage("")}
        />

        <form className="auth-form" onSubmit={handleSubmit}>
          <label className="field">
            <span>Email</span>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="s40978850@student.rmit.edu.au"
              autoComplete="email"
            />
          </label>

          <label className="field">
            <span>Password</span>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="012345"
              autoComplete="current-password"
            />
          </label>

          <button
            type="submit"
            className="button button--primary button--full"
            disabled={loading}
          >
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>

        <p className="auth-card__footer">
          New user? <Link to="/register">Create an account</Link>
        </p>
      </section>
    </main>
  );
}

export default LoginPage;
