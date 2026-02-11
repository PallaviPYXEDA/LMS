"use client"

import MultiMediaBadge from "./multi-media-badge"

import { generateYoutubeEmbedUrl } from "@/utils/youtube"

interface YoutubeRenderProps {
    videoUrl: string,
    maxHeight: number,
    maxWidth: number,
}

export function YoutubeRender({ videoUrl, maxHeight, maxWidth }: YoutubeRenderProps) {
    const embedUrl = generateYoutubeEmbedUrl(videoUrl);
    return (
        <div className="w-full aspect-video max-w-full" style={{ height: maxHeight, width: maxWidth }}>
            <MultiMediaBadge variant="default" badgeName="Video"/>
            {embedUrl ? (
                <iframe 
                    className="w-full h-[calc(100%-40px)] rounded-lg"
                    src={embedUrl}
                    title="YouTube video player"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                ></iframe>
            ) : (
                <div className="w-full h-[calc(100%-40px)] rounded-lg bg-gray-200 flex items-center justify-center">
                    <p className="text-gray-500">Invalid YouTube URL</p>
                </div>
            )}
        </div>
    )
}