import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Register() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    email: "",
    username: "",
    password: ""
  });

  const [error, setError] = useState("");

  // handle input change
  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  // validation logic
  const validate = () => {
    const { email, username, password } = form;

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!email || !username || !password) {
      return "All fields are required";
    }

    if (!emailRegex.test(email)) {
      return "Invalid email format";
    }

    if (username.trim().length < 3) {
      return "Username must be at least 3 characters";
    }

    if (password.length < 6) {
      return "Password must be at least 6 characters";
    }

    return null;
  };

  // submit handler
  const handleRegister = () => {
    setError("");

    const validationError = validate();
    if (validationError) {
      setError(validationError);
      return;
    }

    let users = JSON.parse(localStorage.getItem("users")) || [];

    const exists = users.find((u) => u.email === form.email);

    if (exists) {
      setError("The email already exists");
      return;
    }

    const newUser = {
      email: form.email.trim(),
      username: form.username.trim(),
      password: form.password
    };

    users.push(newUser);
    localStorage.setItem("users", JSON.stringify(users));

    navigate("/");
  };

  return (
    <div className="h-screen flex items-center justify-center bg-zinc-950 text-white">

      <div className="w-96 bg-zinc-900 p-8 rounded-xl border border-zinc-800 shadow-lg">

        {/* Title */}
        <h2 className="text-2xl font-bold mb-6 text-center">
          Create Account
        </h2>

        {/* Email */}
        <input
          name="email"
          value={form.email}
          onChange={handleChange}
          className="w-full mb-3 p-2 bg-zinc-800 rounded outline-none focus:ring-2 focus:ring-purple-600"
          placeholder="Email"
        />

        {/* Username */}
        <input
          name="username"
          value={form.username}
          onChange={handleChange}
          className="w-full mb-3 p-2 bg-zinc-800 rounded outline-none focus:ring-2 focus:ring-purple-600"
          placeholder="Username"
        />

        {/* Password */}
        <input
          name="password"
          type="password"
          value={form.password}
          onChange={handleChange}
          className="w-full mb-3 p-2 bg-zinc-800 rounded outline-none focus:ring-2 focus:ring-purple-600"
          placeholder="Password"
        />

        {/* Error message */}
        {error && (
          <p className="text-red-400 text-sm mb-3">{error}</p>
        )}

        {/* Button */}
        <button
          onClick={handleRegister}
          className="w-full bg-purple-600 p-2 rounded hover:bg-purple-700 transition"
        >
          Register
        </button>

        {/* Login link */}
        <p className="text-sm text-gray-400 mt-4 text-center">
          Already have an account?{" "}
          <span
            onClick={() => navigate("/")}
            className="text-purple-400 cursor-pointer"
          >
            Login
          </span>
        </p>

      </div>
    </div>
  );
}