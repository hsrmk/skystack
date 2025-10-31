import React from "react";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import {
	Tooltip,
	TooltipTrigger,
	TooltipContent,
} from "@/components/ui/tooltip";
import { ArrowUpRight } from "lucide-react";

interface ImageWithTooltipProps {
	src: string;
	height: number;
	width: number;
	name: string;
	substackUrl: string;
	skystackUrl: string;
	className?: string;
}

export default function ImageWithTooltip({
	src,
	height,
	width,
	name,
	substackUrl,
	skystackUrl,
	className,
}: ImageWithTooltipProps) {
	return (
		<Tooltip>
			<TooltipTrigger asChild>
				<span className="inline-block cursor-pointer">
					<Image
						src={src}
						alt={name}
						height={height}
						width={width}
						className="rounded-[20px] object-cover"
					/>
				</span>
			</TooltipTrigger>
			<TooltipContent
				sideOffset={8}
				className={`flex flex-col items-center gap-2 min-w-[200px] bg-black/20 border text-white backdrop-blur ${className}`}
				arrowClassName="bg-black/20 fill-black/20 border-r border-b backdrop-blur"
			>
				<span className="text-sm font-medium mb-1">{name}</span>
				<div className="flex gap-2">
					<Button
						asChild
						variant="ghost"
						size="sm"
						className="flex items-center gap-1 border"
					>
						<a
							href={substackUrl}
							target="_blank"
							rel="noopener noreferrer"
						>
							<Image
								src="/substack.svg"
								alt="Substack"
								width={16}
								height={16}
							/>
							<span>Substack</span>
							<ArrowUpRight size={14} />
						</a>
					</Button>
					<Button
						asChild
						size="sm"
						className="flex items-center gap-1"
					>
						<a
							href={skystackUrl}
							target="_blank"
							rel="noopener noreferrer"
						>
							<Image
								src="/bluesky.svg"
								alt="Bluesky"
								width={16}
								height={16}
							/>
							<span>Bluesky</span>
							<ArrowUpRight size={14} />
						</a>
					</Button>
				</div>
			</TooltipContent>
		</Tooltip>
	);
}
