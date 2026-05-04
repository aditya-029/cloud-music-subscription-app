import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5050";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 15000,
});

function getErrorMessage(error) {
  if (error.response?.data?.message) {
    return error.response.data.message;
  }

  if (error.message) {
    return error.message;
  }

  return "Something went wrong. Please try again.";
}

async function request(apiCall) {
  try {
    const response = await apiCall();
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
}

// -----------------------------
// Health
// -----------------------------
export async function healthCheck() {
  return request(() => apiClient.get("/health"));
}

// -----------------------------
// Authentication
// -----------------------------
export async function loginUser(email, password) {
  return request(() =>
    apiClient.post("/login", {
      email,
      password,
    }),
  );
}

export async function registerUser(email, userName, password) {
  return request(() =>
    apiClient.post("/register", {
      email,
      user_name: userName,
      password,
    }),
  );
}

// -----------------------------
// Music Search
// -----------------------------
export async function searchSongs({
  title = "",
  artist = "",
  year = "",
  album = "",
}) {
  return request(() =>
    apiClient.get("/songs", {
      params: {
        title,
        artist,
        year,
        album,
      },
    }),
  );
}

// -----------------------------
// Subscriptions
// -----------------------------
export async function getSubscriptions(email) {
  return request(() =>
    apiClient.get("/subscriptions", {
      params: {
        email,
      },
    }),
  );
}

export async function subscribeToSong(email, song) {
  return request(() =>
    apiClient.post("/subscriptions", {
      email,
      song,
    }),
  );
}

export async function removeSubscription(email, songId) {
  return request(() =>
    apiClient.delete(`/subscriptions/${encodeURIComponent(email)}/${songId}`),
  );
}

export default apiClient;
