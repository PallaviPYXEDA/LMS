"use client"

import MultiMediaBadge from "./multi-media-badge";

import DOCS_IMAGE from "@/images/docs.png";

interface TeachersGuideProps {
    docsUrl: string,
    maxHeight: number,
    maxWidth: number,
}

const IMAGE_MAX_HEIGHT = 200;
const IMAGE_MAX_WIDTH = 250;

export function TeachersGuide({ docsUrl, maxHeight, maxWidth }: TeachersGuideProps) {
    let validUrl = true;
    if (!docsUrl.startsWith('https://')) {
        validUrl = false;
    }
    return (
        <div className="w-full rounded-lg max-w-full">
            {validUrl ? (
                <>
                <MultiMediaBadge variant="default" badgeName="Teacher's Guide"/>
                <a 
                href={docsUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="block group"
                style={{height: maxHeight, maxWidth: maxWidth}}
            >
                <div className="rounded-lg flex flex-column justify-center items-center border border-gray-200 hover:border-blue-300 transition-colors" style={{height: maxHeight, maxWidth: maxWidth}}>
                    <img 
                        src={DOCS_IMAGE.src}
                        alt={"Teachers Guide"}
                        className="w-full object-cover group-hover:scale-105 transition-transform duration-200"
                        style={{maxHeight: IMAGE_MAX_HEIGHT, maxWidth: IMAGE_MAX_WIDTH}}
                    />
                </div>
            </a>
                </>
            ) : (
                <MultiMediaBadge variant="destructive" badgeName="Invalid URL for Teacher's Guide"/>
            )}
        </div>
    )
}