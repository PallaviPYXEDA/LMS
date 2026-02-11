import { Badge } from "./badge"

interface MultiMediaBadgeProps {
    variant?: "default" | "secondary" | "destructive" | "outline"
    badgeName: string
}

export default function MultiMediaBadge({ badgeName, variant }: MultiMediaBadgeProps) {
    return (
        <Badge variant={variant} className="text-md mb-2">{badgeName}</Badge>
    )
}