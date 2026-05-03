import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Main() {
  const navigate = useNavigate();

  const [user, setUser] = useState(null);
  const [subscriptions, setSubscriptions] = useState([]);
  const [results, setResults] = useState([]);

  // query fields
  const [title, setTitle] = useState("");
  const [year, setYear] = useState("");
  const [artist, setArtist] = useState("");
  const [album, setAlbum] = useState("");

  useEffect(() => {
    const session = JSON.parse(localStorage.getItem("session"));
    if (!session) navigate("/");
    setUser(session);

    const subs = JSON.parse(localStorage.getItem("subs")) || [];
    setSubscriptions(subs);
  }, []);

  const logout = () => {
    localStorage.removeItem("session");
    navigate("/");
  };

  // mock DB songs
  const songDB = [
    { title: "Love Story", artist: "Taylor Swift", year: "2008", album: "Fearless" },
    { title: "Blank Space", artist: "Taylor Swift", year: "2014", album: "1989" },
    { title: "Margaritaville", artist: "Jimmy Buffett", year: "1977", album: "Changes in Latitudes" }
  ];

  const handleQuery = () => {
    if (!title && !year && !artist && !album) {
      alert("At least one field must be completed");
      return;
    }

    const filtered = songDB.filter((song) => {
      return (
        (!title || song.title.includes(title)) &&
        (!year || song.year === year) &&
        (!artist || song.artist.includes(artist)) &&
        (!album || song.album.includes(album))
      );
    });

    setResults(filtered);
  };

  const subscribe = (song) => {
    const updated = [...subscriptions, song];
    setSubscriptions(updated);
    localStorage.setItem("subs", JSON.stringify(updated));
  };

  const remove = (index) => {
    const updated = subscriptions.filter((_, i) => i !== index);
    setSubscriptions(updated);
    localStorage.setItem("subs", JSON.stringify(updated));
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-white p-6">

      {/* HEADER */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-xl">
          Welcome, <span className="text-purple-400">{user?.username}</span>
        </h1>

        <button onClick={logout} className="text-red-400">
          Logout
        </button>
      </div>

      {/* SUBSCRIPTION AREA */}
      <div className="mb-8">
        <h2 className="text-lg mb-3">Subscriptions</h2>

        {subscriptions.length === 0 ? (
          <p className="text-gray-500">No subscriptions yet</p>
        ) : (
          subscriptions.map((s, i) => (
            <div key={i} className="bg-zinc-900 p-3 mb-2 rounded flex justify-between">
              <div>
                {s.title} - {s.artist}
              </div>
              <button
                onClick={() => remove(i)}
                className="text-red-400"
              >
                Remove
              </button>
            </div>
          ))
        )}
      </div>

      {/* QUERY AREA */}
      <div className="bg-zinc-900 p-4 rounded mb-6">
        <h2 className="mb-3">Query Music</h2>

        <div className="grid grid-cols-2 gap-3">
          <input className="p-2 bg-zinc-800 rounded" placeholder="Title" onChange={(e) => setTitle(e.target.value)} />
          <input className="p-2 bg-zinc-800 rounded" placeholder="Year" onChange={(e) => setYear(e.target.value)} />
          <input className="p-2 bg-zinc-800 rounded" placeholder="Artist" onChange={(e) => setArtist(e.target.value)} />
          <input className="p-2 bg-zinc-800 rounded" placeholder="Album" onChange={(e) => setAlbum(e.target.value)} />
        </div>

        <button
          onClick={handleQuery}
          className="mt-3 bg-purple-600 px-4 py-2 rounded"
        >
          Query
        </button>
      </div>

      {/* RESULTS */}
      <div>
        {results.length === 0 ? (
          <p className="text-gray-500">
            No result is retrieved. Please query again
          </p>
        ) : (
          results.map((s, i) => (
            <div key={i} className="bg-zinc-900 p-3 mb-2 rounded flex justify-between">
              <div>
                {s.title} - {s.artist}
              </div>
              <button
                onClick={() => subscribe(s)}
                className="text-purple-400"
              >
                Subscribe
              </button>
            </div>
          ))
        )}
      </div>

    </div>
  );
}