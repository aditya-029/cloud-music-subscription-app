function SongCard({
  song,
  actionLabel,
  onAction,
  actionVariant = "primary",
  disabled = false,
}) {
  if (!song) {
    return null;
  }

  const imageUrl = song.image_url || song.img_url;

  return (
    <article className="song-card">
      <div className="song-card__image-wrap">
        {imageUrl ? (
          <img
            src={imageUrl}
            alt={`${song.artist} artist image`}
            className="song-card__image"
            loading="lazy"
          />
        ) : (
          <div className="song-card__image-placeholder">No Image</div>
        )}
      </div>

      <div className="song-card__content">
        <h3 className="song-card__title">{song.title}</h3>

        <dl className="song-card__details">
          <div>
            <dt>Artist</dt>
            <dd>{song.artist}</dd>
          </div>

          <div>
            <dt>Year</dt>
            <dd>{song.year}</dd>
          </div>

          <div>
            <dt>Album</dt>
            <dd>{song.album}</dd>
          </div>
        </dl>

        {actionLabel && (
          <button
            type="button"
            className={`button button--${actionVariant}`}
            onClick={() => onAction?.(song)}
            disabled={disabled}
          >
            {disabled ? "Please wait..." : actionLabel}
          </button>
        )}
      </div>
    </article>
  );
}

export default SongCard;
