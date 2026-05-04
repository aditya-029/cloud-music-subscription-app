import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  getSubscriptions,
  removeSubscription,
  searchSongs,
  subscribeToSong,
} from "../api/apiClient";
import Header from "../components/Header";
import MessageBanner from "../components/MessageBanner";
import QueryForm from "../components/QueryForm";
import ResultsPanel from "../components/ResultsPanel";
import SubscriptionPanel from "../components/SubscriptionPanel";
import { clearSession, getSession } from "../utils/session";

function MainPage() {
  const navigate = useNavigate();

  const [user, setUser] = useState(null);
  const [subscriptions, setSubscriptions] = useState([]);
  const [results, setResults] = useState([]);

  const [hasSearched, setHasSearched] = useState(false);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("info");

  const [subscriptionsLoading, setSubscriptionsLoading] = useState(false);
  const [searchLoading, setSearchLoading] = useState(false);
  const [actionLoadingId, setActionLoadingId] = useState("");

  useEffect(() => {
    const activeSession = getSession();

    if (!activeSession) {
      navigate("/");
      return;
    }

    setUser(activeSession);
    loadSubscriptions(activeSession.email);
  }, [navigate]);

  async function loadSubscriptions(email) {
    try {
      setSubscriptionsLoading(true);

      const response = await getSubscriptions(email);
      setSubscriptions(response.data || []);
    } catch (error) {
      setMessageType("error");
      setMessage(error.message || "Unable to load subscriptions.");
    } finally {
      setSubscriptionsLoading(false);
    }
  }

  function handleLogout() {
    clearSession();
    navigate("/");
  }

  async function handleSearch(formData, validationMessage = "") {
    setMessage("");

    if (validationMessage) {
      setMessageType("error");
      setMessage(validationMessage);
      return;
    }

    try {
      setSearchLoading(true);
      setHasSearched(true);

      const response = await searchSongs(formData);
      const songs = response.data || [];

      setResults(songs);

      if (songs.length === 0) {
        setMessageType("info");
        setMessage("No result is retrieved. Please query again");
      }
    } catch (error) {
      setResults([]);
      setMessageType("error");
      setMessage(error.message || "Unable to retrieve songs.");
    } finally {
      setSearchLoading(false);
    }
  }

  async function handleSubscribe(song) {
    if (!user?.email || !song?.song_id) {
      setMessageType("error");
      setMessage("Unable to subscribe. Missing user or song details.");
      return;
    }

    try {
      setActionLoadingId(song.song_id);
      setMessage("");

      await subscribeToSong(user.email, song);
      await loadSubscriptions(user.email);

      setMessageType("success");
      setMessage("Song subscribed successfully");
    } catch (error) {
      setMessageType("error");
      setMessage(error.message || "Unable to subscribe to song.");
    } finally {
      setActionLoadingId("");
    }
  }

  async function handleRemove(song) {
    if (!user?.email || !song?.song_id) {
      setMessageType("error");
      setMessage("Unable to remove. Missing user or song details.");
      return;
    }

    try {
      setActionLoadingId(song.song_id);
      setMessage("");

      await removeSubscription(user.email, song.song_id);
      await loadSubscriptions(user.email);

      setMessageType("success");
      setMessage("Song removed successfully");
    } catch (error) {
      setMessageType("error");
      setMessage(error.message || "Unable to remove subscription.");
    } finally {
      setActionLoadingId("");
    }
  }

  return (
    <main className="dashboard-page">
      <Header user={user} onLogout={handleLogout} />

      <div className="dashboard-shell">
        <MessageBanner
          message={message}
          type={messageType}
          onClose={() => setMessage("")}
        />

        <div className="dashboard-grid">
          <QueryForm onSearch={handleSearch} loading={searchLoading} />

          <SubscriptionPanel
            subscriptions={subscriptions}
            loading={subscriptionsLoading}
            onRemove={handleRemove}
            actionLoadingId={actionLoadingId}
          />
        </div>

        <ResultsPanel
          results={results}
          hasSearched={hasSearched}
          loading={searchLoading}
          onSubscribe={handleSubscribe}
          actionLoadingId={actionLoadingId}
        />
      </div>
    </main>
  );
}

export default MainPage;
