"""
Dataset analysis script for Cloud Music Subscription App.

This script analyses the original 2026a2_songs.json dataset before
DynamoDB table creation. The purpose is to understand dataset structure,
cardinality, duplicates, key-design risks, and query patterns that affect
DynamoDB schema design.

Run from project root:

    python -m database.analyse_dataset
"""

import json
from collections import Counter, defaultdict
from statistics import mean, median
from urllib.parse import urlparse

from database.db_config import SONGS_JSON_PATH, build_song_id

REQUIRED_FIELDS = ["title", "artist", "year", "album", "img_url"]


def load_songs():
    """
    Loads the original assignment JSON file and returns the songs list.
    """
    if not SONGS_JSON_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {SONGS_JSON_PATH}")

    with open(SONGS_JSON_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    if "songs" not in data:
        raise KeyError("The JSON file does not contain a 'songs' key.")

    if not isinstance(data["songs"], list):
        raise TypeError("'songs' must be a list.")

    return data["songs"]


def normalise_text(value):
    """
    Converts a value to a trimmed string.
    This keeps the original spelling but removes leading/trailing spaces.
    """
    if value is None:
        return ""
    return str(value).strip()


def get_song_fields(song):
    """
    Extracts and normalises the required song fields.
    """
    return {
        "title": normalise_text(song.get("title")),
        "artist": normalise_text(song.get("artist")),
        "year": normalise_text(song.get("year")),
        "album": normalise_text(song.get("album")),
        "img_url": normalise_text(song.get("img_url")),
    }


def get_decade(year):
    """
    Converts a year string into a decade label.
    Example: 2012 -> 2010s
    """
    try:
        year_int = int(year)
        return f"{year_int // 10 * 10}s"
    except ValueError:
        return "Unknown"


def get_image_filename(img_url):
    """
    Extracts the image filename from an image URL.
    """
    if not img_url:
        return ""
    return urlparse(img_url).path.split("/")[-1]


def safe_percent(part, total):
    """
    Calculates a percentage safely.
    """
    if total == 0:
        return 0
    return round((part / total) * 100, 2)


def analyse_dataset(songs):
    """
    Performs detailed descriptive and assignment-specific analysis.
    """
    total_songs = len(songs)

    title_counter = Counter()
    artist_counter = Counter()
    album_counter = Counter()
    year_counter = Counter()
    decade_counter = Counter()
    image_url_counter = Counter()
    image_filename_counter = Counter()

    missing_values = defaultdict(int)
    field_type_counter = defaultdict(Counter)

    natural_key_counter = Counter()
    song_id_counter = Counter()
    artist_title_counter = Counter()
    artist_year_counter = Counter()
    artist_album_counter = Counter()
    title_artist_counter = Counter()

    songs_per_artist = defaultdict(list)
    albums_per_artist = defaultdict(set)
    years_per_artist = defaultdict(set)
    titles_per_artist = defaultdict(set)

    songs_per_album = defaultdict(list)
    songs_per_year = defaultdict(list)
    songs_per_decade = defaultdict(list)

    repeated_title_records = defaultdict(list)
    same_artist_repeated_title_records = defaultdict(list)
    image_to_artists = defaultdict(set)
    artist_to_images = defaultdict(set)

    year_values = []
    title_lengths = []
    artist_lengths = []
    album_lengths = []

    records = []

    for index, song in enumerate(songs, start=1):
        for field in REQUIRED_FIELDS:
            value = song.get(field)
            field_type_counter[field][type(value).__name__] += 1
            if value is None or str(value).strip() == "":
                missing_values[field] += 1

        fields = get_song_fields(song)

        title = fields["title"]
        artist = fields["artist"]
        year = fields["year"]
        album = fields["album"]
        img_url = fields["img_url"]

        song_id = build_song_id(title, artist, year, album)
        music_sort_key = f"{title}#{year}#{album}"
        title_index_sort_key = f"{artist}#{year}#{album}"
        year_album_lsi_sort_key = f"{year}#{album}#{title}"

        record = {
            "record_number": index,
            "song_id": song_id,
            "title": title,
            "artist": artist,
            "year": year,
            "album": album,
            "img_url": img_url,
            "music_sort_key": music_sort_key,
            "title_index_sort_key": title_index_sort_key,
            "year_album_lsi_sort_key": year_album_lsi_sort_key,
        }
        records.append(record)

        title_counter[title] += 1
        artist_counter[artist] += 1
        album_counter[album] += 1
        year_counter[year] += 1
        decade_counter[get_decade(year)] += 1
        image_url_counter[img_url] += 1
        image_filename_counter[get_image_filename(img_url)] += 1

        natural_key = (title, artist, year, album)
        natural_key_counter[natural_key] += 1
        song_id_counter[song_id] += 1

        artist_title_counter[(artist, title)] += 1
        artist_year_counter[(artist, year)] += 1
        artist_album_counter[(artist, album)] += 1
        title_artist_counter[(title, artist)] += 1

        songs_per_artist[artist].append(record)
        albums_per_artist[artist].add(album)
        years_per_artist[artist].add(year)
        titles_per_artist[artist].add(title)

        songs_per_album[album].append(record)
        songs_per_year[year].append(record)
        songs_per_decade[get_decade(year)].append(record)

        repeated_title_records[title].append(record)
        same_artist_repeated_title_records[(artist, title)].append(record)

        image_to_artists[img_url].add(artist)
        artist_to_images[artist].add(img_url)

        try:
            year_values.append(int(year))
        except ValueError:
            pass

        title_lengths.append(len(title))
        artist_lengths.append(len(artist))
        album_lengths.append(len(album))

    repeated_titles = {
        title: count for title, count in title_counter.items() if count > 1
    }

    repeated_title_details = {
        title: repeated_title_records[title] for title in repeated_titles
    }

    duplicate_natural_keys = {
        key: count for key, count in natural_key_counter.items() if count > 1
    }

    duplicate_song_ids = {
        song_id: count for song_id, count in song_id_counter.items() if count > 1
    }

    same_artist_repeated_titles = {
        key: records_for_key
        for key, records_for_key in same_artist_repeated_title_records.items()
        if len(records_for_key) > 1
    }

    multi_artist_titles = {}
    for title, title_records in repeated_title_records.items():
        artists = sorted({record["artist"] for record in title_records})
        if len(artists) > 1:
            multi_artist_titles[title] = {
                "artists": artists,
                "records": title_records,
            }

    same_artist_different_versions = {}
    for (artist, title), title_records in same_artist_repeated_titles.items():
        years = sorted({record["year"] for record in title_records})
        albums = sorted({record["album"] for record in title_records})
        if len(years) > 1 or len(albums) > 1:
            same_artist_different_versions[(artist, title)] = {
                "years": years,
                "albums": albums,
                "records": title_records,
            }

    image_urls_used_by_multiple_artists = {
        img_url: sorted(artists)
        for img_url, artists in image_to_artists.items()
        if len(artists) > 1
    }

    artists_with_multiple_images = {
        artist: sorted(images)
        for artist, images in artist_to_images.items()
        if len(images) > 1
    }

    top_artists = artist_counter.most_common(10)
    top_albums = album_counter.most_common(10)
    top_years = year_counter.most_common(10)
    top_decades = decade_counter.most_common()

    artist_diversity = []
    for artist in sorted(artist_counter.keys()):
        artist_diversity.append(
            {
                "artist": artist,
                "song_count": artist_counter[artist],
                "unique_albums": len(albums_per_artist[artist]),
                "unique_years": len(years_per_artist[artist]),
                "unique_titles": len(titles_per_artist[artist]),
            }
        )

    artist_diversity_sorted = sorted(
        artist_diversity,
        key=lambda item: (
            item["song_count"],
            item["unique_albums"],
            item["unique_years"],
        ),
        reverse=True,
    )

    query_pattern_examples = {
        "artist_only": [
            {
                "artist": artist,
                "matching_records": count,
            }
            for artist, count in artist_counter.most_common(5)
        ],
        "artist_and_year": [
            {
                "artist": artist,
                "year": year,
                "matching_records": count,
            }
            for (artist, year), count in artist_year_counter.most_common(10)
            if count > 1
        ],
        "artist_and_album": [
            {
                "artist": artist,
                "album": album,
                "matching_records": count,
            }
            for (artist, album), count in artist_album_counter.most_common(10)
            if count > 1
        ],
        "title_only": [
            {
                "title": title,
                "matching_records": count,
            }
            for title, count in sorted(repeated_titles.items())
        ],
    }

    if year_values:
        year_summary = {
            "min_year": min(year_values),
            "max_year": max(year_values),
            "range_years": max(year_values) - min(year_values),
            "mean_year": round(mean(year_values), 2),
            "median_year": median(year_values),
        }
    else:
        year_summary = {
            "min_year": None,
            "max_year": None,
            "range_years": None,
            "mean_year": None,
            "median_year": None,
        }

    text_length_summary = {
        "title_length": {
            "min": min(title_lengths) if title_lengths else 0,
            "max": max(title_lengths) if title_lengths else 0,
            "mean": round(mean(title_lengths), 2) if title_lengths else 0,
            "median": median(title_lengths) if title_lengths else 0,
        },
        "artist_length": {
            "min": min(artist_lengths) if artist_lengths else 0,
            "max": max(artist_lengths) if artist_lengths else 0,
            "mean": round(mean(artist_lengths), 2) if artist_lengths else 0,
            "median": median(artist_lengths) if artist_lengths else 0,
        },
        "album_length": {
            "min": min(album_lengths) if album_lengths else 0,
            "max": max(album_lengths) if album_lengths else 0,
            "mean": round(mean(album_lengths), 2) if album_lengths else 0,
            "median": median(album_lengths) if album_lengths else 0,
        },
    }

    return {
        "total_songs": total_songs,
        "records": records,
        "unique_titles": len(title_counter),
        "unique_artists": len(artist_counter),
        "unique_albums": len(album_counter),
        "unique_years": len(year_counter),
        "unique_decades": len(decade_counter),
        "unique_image_urls": len(image_url_counter),
        "unique_image_filenames": len(image_filename_counter),
        "missing_values": dict(missing_values),
        "field_type_counter": field_type_counter,
        "repeated_titles": repeated_titles,
        "repeated_title_details": repeated_title_details,
        "duplicate_natural_keys": duplicate_natural_keys,
        "duplicate_song_ids": duplicate_song_ids,
        "same_artist_different_versions": same_artist_different_versions,
        "multi_artist_titles": multi_artist_titles,
        "image_urls_used_by_multiple_artists": image_urls_used_by_multiple_artists,
        "artists_with_multiple_images": artists_with_multiple_images,
        "top_artists": top_artists,
        "top_albums": top_albums,
        "top_years": top_years,
        "top_decades": top_decades,
        "artist_diversity": artist_diversity_sorted,
        "query_pattern_examples": query_pattern_examples,
        "year_summary": year_summary,
        "text_length_summary": text_length_summary,
    }


def print_heading(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def print_subheading(title):
    print("\n" + "-" * 80)
    print(title)
    print("-" * 80)


def print_counter_list(items, limit=None):
    shown_items = items[:limit] if limit else items
    for key, count in shown_items:
        print(f"  - {key}: {count}")


def print_record_brief(record):
    print(
        f"    • {record['title']} | {record['artist']} | "
        f"{record['year']} | {record['album']} | song_id={record['song_id']}"
    )


def print_analysis(results):
    """
    Prints the analysis clearly for terminal review and report evidence.
    """
    total = results["total_songs"]

    print_heading("DATASET ANALYSIS: 2026a2_songs.json")

    print_subheading("1. Basic Dataset Structure")
    print(f"Total song records: {results['total_songs']}")
    print(f"Unique song titles: {results['unique_titles']}")
    print(f"Unique artists: {results['unique_artists']}")
    print(f"Unique albums: {results['unique_albums']}")
    print(f"Unique years: {results['unique_years']}")
    print(f"Unique decades: {results['unique_decades']}")
    print(f"Unique image URLs: {results['unique_image_urls']}")
    print(f"Unique image filenames: {results['unique_image_filenames']}")

    print_subheading("2. Field Completeness and Data Types")
    print("Missing values:")
    if results["missing_values"]:
        for field in REQUIRED_FIELDS:
            count = results["missing_values"].get(field, 0)
            print(f"  - {field}: {count}")
    else:
        print("  - None")

    print("\nDetected field types:")
    for field in REQUIRED_FIELDS:
        type_counts = results["field_type_counter"][field]
        print(f"  - {field}: {dict(type_counts)}")

    print_subheading("3. Year Distribution")
    ys = results["year_summary"]
    print(f"Earliest year: {ys['min_year']}")
    print(f"Latest year: {ys['max_year']}")
    print(f"Year range: {ys['range_years']} years")
    print(f"Mean release year: {ys['mean_year']}")
    print(f"Median release year: {ys['median_year']}")

    print("\nTop years:")
    print_counter_list(results["top_years"], limit=10)

    print("\nDecade distribution:")
    for decade, count in sorted(results["top_decades"]):
        print(f"  - {decade}: {count} songs ({safe_percent(count, total)}%)")

    print_subheading("4. Text Length Summary")
    for field_name, summary in results["text_length_summary"].items():
        print(f"{field_name}:")
        print(f"  - Min: {summary['min']}")
        print(f"  - Max: {summary['max']}")
        print(f"  - Mean: {summary['mean']}")
        print(f"  - Median: {summary['median']}")

    print_subheading("5. Artist, Album, and Catalogue Concentration")
    print("Top artists by number of songs:")
    print_counter_list(results["top_artists"], limit=10)

    print("\nTop albums by number of songs:")
    print_counter_list(results["top_albums"], limit=10)

    print("\nArtists with broadest representation:")
    for item in results["artist_diversity"][:10]:
        print(
            f"  - {item['artist']}: "
            f"{item['song_count']} songs, "
            f"{item['unique_albums']} albums, "
            f"{item['unique_years']} years"
        )

    print_subheading("6. Duplicate and Key-Risk Analysis")
    print(f"Repeated song titles: {len(results['repeated_titles'])}")

    if results["repeated_titles"]:
        for title, count in sorted(results["repeated_titles"].items()):
            print(f"\n  - {title}: {count} records")
            for record in results["repeated_title_details"][title]:
                print_record_brief(record)
    else:
        print("  - None")

    print("\nDuplicate natural keys: title + artist + year + album")
    if results["duplicate_natural_keys"]:
        for key, count in results["duplicate_natural_keys"].items():
            print(f"  - {key}: {count}")
    else:
        print("  - None")

    print("\nDuplicate generated song IDs:")
    if results["duplicate_song_ids"]:
        for song_id, count in results["duplicate_song_ids"].items():
            print(f"  - {song_id}: {count}")
    else:
        print("  - None")

    print_subheading("7. Assignment-Specific Music Identity Analysis")
    print("Titles used by multiple artists:")
    if results["multi_artist_titles"]:
        for title, details in results["multi_artist_titles"].items():
            print(f"\n  - {title}: {', '.join(details['artists'])}")
            for record in details["records"]:
                print_record_brief(record)
    else:
        print("  - None")

    print("\nSame artist with multiple versions of the same title:")
    if results["same_artist_different_versions"]:
        for (artist, title), details in results[
            "same_artist_different_versions"
        ].items():
            print(
                f"\n  - {artist} / {title}: "
                f"years={details['years']}, albums={details['albums']}"
            )
            for record in details["records"]:
                print_record_brief(record)
    else:
        print("  - None")

    print_subheading("8. Image URL and S3 Planning Analysis")
    print(
        "Unique image URLs compared with artists: "
        f"{results['unique_image_urls']} image URLs for {results['unique_artists']} artists"
    )

    print("\nImage URLs used by multiple artists:")
    if results["image_urls_used_by_multiple_artists"]:
        for img_url, artists in results["image_urls_used_by_multiple_artists"].items():
            print(f"  - {img_url}: {', '.join(artists)}")
    else:
        print("  - None")

    print("\nArtists with multiple image URLs:")
    if results["artists_with_multiple_images"]:
        for artist, images in results["artists_with_multiple_images"].items():
            print(f"  - {artist}:")
            for image in images:
                print(f"      {image}")
    else:
        print("  - None")

    print_subheading("9. Query Pattern Evidence for DynamoDB Design")
    print("Common artist-only query examples:")
    for item in results["query_pattern_examples"]["artist_only"]:
        print(f"  - artist={item['artist']} -> {item['matching_records']} records")

    print("\nCommon artist + year query examples:")
    for item in results["query_pattern_examples"]["artist_and_year"]:
        print(
            f"  - artist={item['artist']}, year={item['year']} "
            f"-> {item['matching_records']} records"
        )

    print("\nCommon artist + album query examples:")
    for item in results["query_pattern_examples"]["artist_and_album"]:
        print(
            f"  - artist={item['artist']}, album={item['album']} "
            f"-> {item['matching_records']} records"
        )

    print("\nTitle-only query risks:")
    for item in results["query_pattern_examples"]["title_only"]:
        print(f"  - title={item['title']} -> {item['matching_records']} records")

    print_subheading("10. DynamoDB Key Design Conclusion")
    print(
        "1. Title alone is not safe as a partition key because multiple titles repeat."
    )
    print(
        "2. The natural combination of title + artist + year + album uniquely identifies records."
    )
    print(
        "3. A generated song_id from title + artist + year + album is safe for subscriptions."
    )
    print(
        "4. Using artist as the music table partition key supports likely marker queries such as "
        "'Taylor Swift in Fearless' and 'Jimmy Buffett in 1974'."
    )
    print(
        "5. A title-based GSI is justified because title-only searches can return multiple versions."
    )
    print(
        "6. An artist-based LSI using year + album + title is justified for efficient filtering "
        "within an artist partition."
    )
    print(
        "7. The S3 upload process should store one image object per unique artist/image URL, "
        "then save the S3 key against each music record."
    )

    print_heading("END OF DATASET ANALYSIS")


def main():
    songs = load_songs()
    results = analyse_dataset(songs)
    print_analysis(results)


if __name__ == "__main__":
    main()
