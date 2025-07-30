import React from "react";
import { ArrowUpRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import Image from "next/image";
import Box from "@/components/Box";

interface AccountCardProps {
	profilePicImage: string;
	name: string;
	username: string;
	description: string;
	substackUrl: string;
	skystackUrl: string;
	className?: string;
}

export function AccountCard({
	profilePicImage,
	name,
	username,
	description,
	substackUrl,
	skystackUrl,
	className,
}: AccountCardProps) {
	return (
		<Box className={`w-full p-5 ${className}`}>
			{/* Profile section */}
			<div className="flex items-start gap-2">
				{/* Circular profile image */}
				<div className="flex-shrink-0">
					<Image
						src={profilePicImage}
						alt={`${name}'s profile picture`}
						width={40}
						height={40}
						className="rounded-full object-cover"
					/>
				</div>

				{/* Name and username */}
				<div className="flex-1 min-w-0">
					<p className="text-sm font-semibold truncate">{name}</p>
					<p className="text-sm text-font-secondary truncate">
						@{username}
					</p>
				</div>
			</div>

			{/* Description */}
			<p className="text-sm font-medium text-font-secondary leading-relaxed pt-4 pb-8">
				{description}
				<br />
				<br />
				<span>
					Writes at{" "}
					<a
						href={substackUrl}
						className="underline text-font-secondary hover:text-white transition-colors"
						target="_blank"
						rel="noopener noreferrer"
					>
						{substackUrl}
					</a>
				</span>
			</p>

			{/* Action buttons */}
			<div className="flex flex-col sm:flex-row gap-2">
				{/* Substack button */}
				<a
					href={substackUrl}
					target="_blank"
					rel="noopener noreferrer"
					// className="flex-shrink-0"
				>
					<Button
						variant="secondary"
						size="sm"
						className="w-full flex items-center gap-2 bg-black border"
					>
						<Image
							src="/substack.svg"
							alt="Substack"
							width={15}
							height={15}
						/>
						<span className="truncate">Substack</span>
						<ArrowUpRight size={4} />
					</Button>
				</a>

				{/* Bluesky button */}
				<a href={skystackUrl} target="_blank" rel="noopener noreferrer">
					<Button
						variant="default"
						size="sm"
						className="w-full flex items-center gap-2"
					>
						<Image
							src="/bluesky.svg"
							alt="Bluesky"
							width={15}
							height={15}
						/>
						<span>Follow on Bluesky</span>
					</Button>
				</a>
			</div>
		</Box>
	);
}
