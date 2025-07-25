"use client";

import React from "react";
import HeroGrid from "@/components/HeroGrid";

export default function Hero() {
	return (
		<section className="h-screen w-screen overflow-hidden p-4 text-center relative">
			{/* Gradient Overlays */}
			<div className="pointer-events-none absolute right-0 top-0 h-full lg:w-[200px] w-25 bg-gradient-to-l from-black via-black/80 to-transparent z-10" />
			<div className="pointer-events-none absolute left-0 top-0 h-full lg:w-[200px] w-25 bg-gradient-to-r from-black via-black/80 to-transparent z-10" />
			<div className="pointer-events-none absolute left-0 bottom-0 w-full lg:h-[200px] h-50 bg-gradient-to-t from-black via-black/80 to-transparent z-10" />

			<HeroGrid />
		</section>
	);
}
