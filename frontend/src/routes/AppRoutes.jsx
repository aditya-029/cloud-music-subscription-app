import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import LoginPage from "../pages/LoginPage";
import RegisterPage from "../pages/RegisterPage";
import MainPage from "../pages/MainPage";

function App() {
  const isLoggedIn = localStorage.getItem("session");

  return (
    <BrowserRouter>
      <Routes>

        {/* Default route → Login */}
        <Route path="/" element={<LoginPage />} />

        {/* Register page */}
        <Route path="/register" element={<RegisterPage />} />

        {/* Protected Dashboard */}
        <Route
          path="/dashboard"
          element={
            isLoggedIn ? <MainPage /> : <Navigate to="/" />
          }
        />

        {/* fallback route */}
        <Route path="*" element={<Navigate to="/" />} />

      </Routes>
    </BrowserRouter>
  );
}

export default App;