import SongCard from "./SongCard";

function SubscriptionPanel({
  subscriptions = [],
  loading = false,
  onRemove,
  actionLoadingId = "",
}) {
  return (
    <section className="panel subscription-panel">
      <div className="section-heading">
        <p className="section-kicker">Your Subscriptions</p>
      </div>

      {loading && <div className="empty-state">Loading subscriptions...</div>}

      {!loading && subscriptions.length === 0 && (
        <div className="empty-state">No subscriptions yet.</div>
      )}

      {!loading && subscriptions.length > 0 && (
        <div className="song-list song-list--compact">
          {subscriptions.map((song) => (
            <SongCard
              key={song.song_id}
              song={song}
              actionLabel="Remove"
              actionVariant="danger"
              onAction={onRemove}
              disabled={actionLoadingId === song.song_id}
            />
          ))}
        </div>
      )}
    </section>
  );
}

export default SubscriptionPanel;
