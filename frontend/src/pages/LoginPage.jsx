import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    email: "",
    password: ""
  });

  const [error, setError] = useState("");

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  // ✅ VALIDATION FUNCTION
  const validate = () => {
    const email = form.email.trim();
    const password = form.password;

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!email || !password) {
      return "All fields are required";
    }

    if (!emailRegex.test(email)) {
      return "Invalid email format";
    }

    if (password.length < 6) {
      return "Password must be at least 6 characters";
    }

    return null;
  };

  const handleLogin = () => {
    setError("");

    // 1. run validation
    const validationError = validate();
    if (validationError) {
      setError(validationError);
      return;
    }

    const users = JSON.parse(localStorage.getItem("users")) || [];

    const email = form.email.trim();
    const password = form.password;

    // 2. authentication check
    const user = users.find(
      (u) => u.email === email && u.password === password
    );

    if (!user) {
      setError("email or password is invalid");
      return;
    }

    // 3. create session
    localStorage.setItem("session", JSON.stringify(user));

    // 4. redirect
    navigate("/dashboard");
  };

  return (
    <div className="h-screen flex items-center justify-center bg-zinc-950 text-white">

      <div className="w-96 bg-zinc-900 p-8 rounded-xl border border-zinc-800">

        <h2 className="text-2xl font-bold mb-6 text-center">
          Login
        </h2>

        {/* EMAIL */}
        <input
          name="email"
          value={form.email}
          onChange={handleChange}
          className="w-full mb-3 p-2 bg-zinc-800 rounded outline-none focus:ring-2 focus:ring-purple-600"
          placeholder="Email"
        />

        {/* PASSWORD */}
        <input
          name="password"
          type="password"
          value={form.password}
          onChange={handleChange}
          className="w-full mb-3 p-2 bg-zinc-800 rounded outline-none focus:ring-2 focus:ring-purple-600"
          placeholder="Password"
        />

        {/* ERROR */}
        {error && (
          <p className="text-red-400 text-sm mb-3">{error}</p>
        )}

        {/* BUTTON */}
        <button
          onClick={handleLogin}
          className="w-full bg-purple-600 p-2 rounded hover:bg-purple-700 transition"
        >
          Login
        </button>

        {/* LINK */}
        <p className="text-sm text-gray-400 mt-4 text-center">
          New user?{" "}
          <span
            onClick={() => navigate("/register")}
            className="text-purple-400 cursor-pointer"
          >
            Register
          </span>
        </p>

      </div>
    </div>
  );
}