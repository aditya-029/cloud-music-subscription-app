import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { registerUser } from "../api/apiClient";
import MessageBanner from "../components/MessageBanner";

function RegisterPage() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    email: "",
    userName: "",
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

  function validateForm() {
    const email = formData.email.trim();
    const userName = formData.userName.trim();
    const password = formData.password.trim();

    if (!email || !userName || !password) {
      return "All fields are required";
    }

    if (!email.includes("@")) {
      return "Invalid email format";
    }

    if (userName.length < 3) {
      return "Username must be at least 3 characters";
    }

    if (password.length < 6) {
      return "Password must be at least 6 characters";
    }

    return "";
  }

  async function handleSubmit(event) {
    event.preventDefault();

    setMessage("");

    const validationError = validateForm();
    if (validationError) {
      setMessageType("error");
      setMessage(validationError);
      return;
    }

    try {
      setLoading(true);

      await registerUser(
        formData.email.trim(),
        formData.userName.trim(),
        formData.password.trim(),
      );

      setMessageType("success");
      setMessage("Registration successful. Redirecting to login...");

      setTimeout(() => {
        navigate("/");
      }, 900);
    } catch (error) {
      setMessageType("error");
      setMessage(error.message || "The email already exists");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card">
        <div className="auth-card__header">
          <span className="app-logo app-logo--large">♪</span>
          <h1>Create Account</h1>
          <p>Register with a unique email address to access the music app.</p>
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
              placeholder="new.user@student.rmit.edu.au"
              autoComplete="email"
            />
          </label>

          <label className="field">
            <span>Username</span>
            <input
              type="text"
              name="userName"
              value={formData.userName}
              onChange={handleChange}
              placeholder="NewUser"
              autoComplete="username"
            />
          </label>

          <label className="field">
            <span>Password</span>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Minimum 6 characters"
              autoComplete="new-password"
            />
          </label>

          <button
            type="submit"
            className="button button--primary button--full"
            disabled={loading}
          >
            {loading ? "Registering..." : "Register"}
          </button>
        </form>

        <p className="auth-card__footer">
          Already have an account? <Link to="/">Login</Link>
        </p>
      </section>
    </main>
  );
}

export default RegisterPage;
