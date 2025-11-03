export async function fetchAppleMetadata(title, artist) {
  const q = encodeURIComponent(`${title} ${artist}`);

  const url = `https://itunes.apple.com/search?term=${q}&limit=1`;

  const res = await fetch(url);
  const data = await res.json();

  if (!data.results?.length) return null;

  const song = data.results[0];

  return {
    cover: song.artworkUrl100?.replace("100x100", "300x300"),
    appleUrl: song.trackViewUrl,
    preview: song.previewUrl
  };
}
