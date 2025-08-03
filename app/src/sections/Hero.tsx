"use client";

import React from "react";
import Image from "next/image";

import HeroGrid from "@/components/HeroGrid";
import CreateField from "@/components/CreateField";

interface AccountData {
	profilePicImage: string;
	name: string;
	username: string;
	description: string;
	substackUrl: string;
	skystackUrl: string;
}

interface HeroProps {
	data: AccountData[];
}

export default function Hero({ data }: HeroProps) {
	return (
		<section className="h-screen w-screen overflow-hidden p-4 text-center relative">
			{/* Gradient Overlays */}
			<div className="pointer-events-none absolute right-0 top-0 h-full lg:w-[200px] w-25 bg-gradient-to-l from-black via-black/80 to-transparent z-10" />
			<div className="pointer-events-none absolute left-0 top-0 h-full lg:w-[200px] w-25 bg-gradient-to-r from-black via-black/80 to-transparent z-10" />
			<div className="pointer-events-none absolute left-0 bottom-0 w-full lg:h-[200px] h-50 bg-gradient-to-t from-black via-black/50 to-transparent z-10" />

			<HeroGrid />

			{/* Centered Hero Text */}
			<div className="pointer-events-none absolute inset-0 z-20 flex flex-col items-center gap-8 justify-center translate-y-[-5%]">
				{/* Logo and Text Section */}
				<div className="flex items-center gap-4">
					<Image
						src="/skystack-logo.png"
						alt="Skystack Logo"
						width={50}
						height={50}
					/>
					<div className="flex flex-col items-start">
						<p className="font-bold text-white">Skystack</p>
						<p className="text-xs text-font-secondary">
							Follow Substack Newsletters on Bluesky
						</p>
					</div>
				</div>

				<CreateField />
			</div>
		</section>
	);
}
