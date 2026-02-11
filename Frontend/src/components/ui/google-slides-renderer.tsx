"use client"

import MultiMediaBadge from "./multi-media-badge";

import SLIDES_IMAGE from "@/images/slides.png";

interface GoogleSlidesRendererProps {
    slidesUrl: string,
    maxHeight: number,
    maxWidth: number,
}

const IMAGE_MAX_HEIGHT = 200;
const IMAGE_MAX_WIDTH = 250;

export function GoogleSlidesRenderer({ slidesUrl, maxHeight, maxWidth }: GoogleSlidesRendererProps) {
    // validate the hhtps of the url
    let validUrl = true
    if (!slidesUrl.startsWith('https://')) {
        validUrl = false;
    }
    return (
        <div className="w-full rounded-lg max-w-full">
            {validUrl ? (
                <>
                <MultiMediaBadge variant="default" badgeName="Google Slides"/>
                <a 
                href={slidesUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="block group"
                style={{height: maxHeight, maxWidth: maxWidth}}
            >
                <div className="rounded-lg flex flex-column justify-center items-center border border-gray-200 hover:border-blue-300 transition-colors" style={{height: maxHeight, maxWidth: maxWidth}}>
                    <img 
                        src={SLIDES_IMAGE.src}
                        alt={"Google Slides presentation"}
                        className="w-full object-cover group-hover:scale-105 transition-transform duration-200"
                        style={{maxHeight: IMAGE_MAX_HEIGHT, maxWidth: IMAGE_MAX_WIDTH}}
                    />
                </div>
            </a>
                </>
            ) : (
                <MultiMediaBadge variant="destructive" badgeName="Invalid URL for Google Slides"/>
            )}
        </div>
    )
}