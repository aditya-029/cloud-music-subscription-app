import SongCard from "./SongCard";

function ResultsPanel({
  results = [],
  hasSearched = false,
  loading = false,
  onSubscribe,
  actionLoadingId = "",
}) {
  return (
    <section className="panel results-panel">
      <div className="section-heading">
        <p className="section-kicker">Search Results</p>
      </div>

      {loading && <div className="empty-state">Searching music records...</div>}

      {!loading && !hasSearched && (
        <div className="empty-state">
          Enter at least one search field and click Query.
        </div>
      )}

      {!loading && hasSearched && results.length === 0 && (
        <div className="empty-state">
          No result is retrieved. Please query again
        </div>
      )}

      {!loading && results.length > 0 && (
        <div className="song-grid">
          {results.map((song) => (
            <SongCard
              key={song.song_id}
              song={song}
              actionLabel="Subscribe"
              actionVariant="primary"
              onAction={onSubscribe}
              disabled={actionLoadingId === song.song_id}
            />
          ))}
        </div>
      )}
    </section>
  );
}

export default ResultsPanel;
