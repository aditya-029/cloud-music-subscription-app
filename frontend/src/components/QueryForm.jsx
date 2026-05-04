import { useState } from "react";

const initialFormState = {
  title: "",
  artist: "",
  year: "",
  album: "",
};

function QueryForm({ onSearch, loading = false }) {
  const [formData, setFormData] = useState(initialFormState);
  const [localError, setLocalError] = useState("");

  function handleChange(event) {
    const { name, value } = event.target;

    setLocalError("");

    setFormData((currentData) => ({
      ...currentData,
      [name]: value,
    }));
  }

  function hasAtLeastOneField() {
    return Object.values(formData).some((value) => value.trim() !== "");
  }

  function handleSubmit(event) {
    event.preventDefault();

    if (!hasAtLeastOneField()) {
      const message = "At least one query field must be provided";
      setLocalError(message);
      onSearch?.(formData, message);
      return;
    }

    setLocalError("");
    onSearch?.(formData);
  }

  function handleClear() {
    setFormData(initialFormState);
    setLocalError("");
  }

  return (
    <section className="panel query-panel">
      <div className="section-heading">
        <p className="section-kicker">Search music</p>
      </div>

      <form className="query-form" onSubmit={handleSubmit}>
        <div className="query-required-note">
          <span className="required-dot" aria-hidden="true"></span>
          At least one field is required.
        </div>

        <div className="form-grid">
          <label className="field">
            <span>Title</span>
            <input
              type="text"
              name="title"
              value={formData.title}
              onChange={handleChange}
              placeholder="e.g. Bad Blood"
            />
          </label>

          <label className="field">
            <span>Artist</span>
            <input
              type="text"
              name="artist"
              value={formData.artist}
              onChange={handleChange}
              placeholder="e.g. Taylor Swift"
            />
          </label>

          <label className="field">
            <span>Year</span>
            <input
              type="text"
              name="year"
              value={formData.year}
              onChange={handleChange}
              placeholder="e.g. 1974"
            />
          </label>

          <label className="field">
            <span>Album</span>
            <input
              type="text"
              name="album"
              value={formData.album}
              onChange={handleChange}
              placeholder="e.g. Fearless"
            />
          </label>
        </div>

        {localError && <p className="inline-form-error">{localError}</p>}

        <div className="form-actions">
          <button
            type="submit"
            className="button button--primary"
            disabled={loading}
          >
            {loading ? "Searching..." : "Query"}
          </button>

          <button
            type="button"
            className="button button--secondary"
            onClick={handleClear}
            disabled={loading}
          >
            Clear
          </button>
        </div>
      </form>
    </section>
  );
}

export default QueryForm;
