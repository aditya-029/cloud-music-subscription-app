const SESSION_KEY = "cloudMusicUser";

export function saveSession(user) {
  if (!user || !user.email || !user.user_name) {
    throw new Error("Invalid user session data.");
  }

  const sessionData = {
    email: user.email,
    user_name: user.user_name,
  };

  localStorage.setItem(SESSION_KEY, JSON.stringify(sessionData));
  return sessionData;
}

export function getSession() {
  const storedSession = localStorage.getItem(SESSION_KEY);

  if (!storedSession) {
    return null;
  }

  try {
    const sessionData = JSON.parse(storedSession);

    if (!sessionData.email || !sessionData.user_name) {
      clearSession();
      return null;
    }

    return sessionData;
  } catch {
    clearSession();
    return null;
  }
}

export function clearSession() {
  localStorage.removeItem(SESSION_KEY);
}

export function isLoggedIn() {
  return Boolean(getSession());
}
