export const extractYoutubeVideoId = (url: string) => {
    if (!url) {
        return null;
    }
    let fetchedUrl: URL;
    try {
        fetchedUrl = new URL(url);
    } catch {
        // Invalid URL string
        return null;
    }
    const hostname = fetchedUrl.hostname.toLowerCase();
    const isYoutubeHost =
        hostname === 'www.youtube.com' ||
        hostname === 'youtube.com' ||
        hostname === 'youtu.be' ||
        hostname.endsWith('.youtube.com');
    if (!isYoutubeHost) {
        // Not a YouTube URL
        return null;
    }
    const params = fetchedUrl.searchParams;
    let videoId = params.get('v');
    if (!videoId) {
        // Fall back to last non-empty path segment, e.g. youtu.be/<id> or /embed/<id>
        const pathSegments = fetchedUrl.pathname.split('/').filter(Boolean);
        videoId = pathSegments[pathSegments.length - 1] || null;
    }
    return videoId;
}


export const generateYoutubeEmbedUrl = (youtubeUrl: string) => {
    const videoId = extractYoutubeVideoId(youtubeUrl);
    if (!videoId) {
        // Could not extract a valid YouTube video ID
        return null;
    }

    return `https://www.youtube.com/embed/${videoId}`;
}
