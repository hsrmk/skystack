import React from "react";
import ImageWithTooltip from "@/components/ImageWithTooltip";

// Hardcoded data for images and their grid positions
const heroGridData = [
	// row, col, image props
	{
		row: 0,
		col: 0,
		src: "/skystack-logo.png",
		name: "Bluesky 1",
		substackUrl: "#",
		skystackUrl: "#",
	},
	{
		row: 0,
		col: 10,
		src: "/skystack-logo.png",
		name: "Substack 1",
		substackUrl: "#",
		skystackUrl: "#",
	},
	{
		row: 1,
		col: 0,
		src: "/skystack-logo.png",
		name: "Bluesky 2",
		substackUrl: "#",
		skystackUrl: "#",
	},
	{
		row: 1,
		col: 6,
		src: "/skystack-logo.png",
		name: "Substack 2",
		substackUrl: "#",
		skystackUrl: "#",
	},
	{
		row: 2,
		col: 0,
		src: "/skystack-logo.png",
		name: "Bluesky 3",
		substackUrl: "#",
		skystackUrl: "#",
	},
	{
		row: 2,
		col: 1,
		src: "/skystack-logo.png",
		name: "Substack 3",
		substackUrl: "#",
		skystackUrl: "#",
	},
	{
		row: 2,
		col: 5,
		src: "/skystack-logo.png",
		name: "Bluesky 4",
		substackUrl: "#",
		skystackUrl: "#",
	},
	{
		row: 2,
		col: 6,
		src: "/skystack-logo.png",
		name: "Substack 4",
		substackUrl: "#",
		skystackUrl: "#",
	},
	{
		row: 3,
		col: 0,
		src: "/skystack-logo.png",
		name: "Bluesky 5",
		substackUrl: "#",
		skystackUrl: "#",
	},
	{
		row: 3,
		col: 5,
		src: "/skystack-logo.png",
		name: "Substack 5",
		substackUrl: "#",
		skystackUrl: "#",
	},
	{
		row: 3,
		col: 6,
		src: "/skystack-logo.png",
		name: "Bluesky 6",
		substackUrl: "#",
		skystackUrl: "#",
	},
	{
		row: 4,
		col: 0,
		src: "/skystack-logo.png",
		name: "Bluesky 7",
		substackUrl: "#",
		skystackUrl: "#",
	},
	{
		row: 4,
		col: 1,
		src: "/skystack-logo.png",
		name: "Substack 6",
		substackUrl: "#",
		skystackUrl: "#",
	},
	{
		row: 4,
		col: 5,
		src: "/skystack-logo.png",
		name: "Bluesky 8",
		substackUrl: "#",
		skystackUrl: "#",
	},
	{
		row: 4,
		col: 6,
		src: "/skystack-logo.png",
		name: "Substack 7",
		substackUrl: "#",
		skystackUrl: "#",
	},
	{
		row: 5,
		col: 0,
		src: "/skystack-logo.png",
		name: "Bluesky 9",
		substackUrl: "#",
		skystackUrl: "#",
	},
	{
		row: 5,
		col: 1,
		src: "/skystack-logo.png",
		name: "Substack 8",
		substackUrl: "#",
		skystackUrl: "#",
	},
	{
		row: 5,
		col: 2,
		src: "/skystack-logo.png",
		name: "Bluesky 10",
		substackUrl: "#",
		skystackUrl: "#",
	},
	{
		row: 5,
		col: 5,
		src: "/skystack-logo.png",
		name: "Substack 9",
		substackUrl: "#",
		skystackUrl: "#",
	},
	{
		row: 5,
		col: 6,
		src: "/skystack-logo.png",
		name: "Bluesky 11",
		substackUrl: "#",
		skystackUrl: "#",
	},
	// 7th row: all columns
	...Array.from({ length: 11 }, (_, i) => ({
		row: 6,
		col: i,
		src: i % 2 === 0 ? "/skystack-logo.png" : "/skystack-logo.png",
		name: `Row 7 Col ${i + 1}`,
		substackUrl: "#",
		skystackUrl: "#",
	})),
];

const Hero = () => {
	return (
		<section className="w-screen h-screen min-h-screen min-w-full flex items-center justify-center bg-gradient-to-br overflow-hidden">
			{/* Desktop grid layout */}
			<div
				className="hidden sm:grid w-full h-full grid-rows-7 grid-cols-11 relative"
				// style={{ minHeight: "100vh", minWidth: "100vw" }}
			>
				{heroGridData.map((item, idx) => (
					<div
						key={idx}
						className="absolute border"
						style={{
							gridRowStart: item.row + 1,
							gridColumnStart: item.col + 1,
							// Optionally, tweak translate for overlap/spacing
						}}
					>
						<ImageWithTooltip
							src={item.src}
							height={54}
							width={54}
							name={item.name}
							substackUrl={item.substackUrl}
							skystackUrl={item.skystackUrl}
							// className=""
						/>
					</div>
				))}
			</div>
			{/* Mobile layout: simple vertical stack */}
			<div className="flex flex-col sm:hidden w-full h-full items-center justify-center gap-4 py-8 overflow-y-auto">
				{heroGridData.slice(0, 7).map((item, idx) => (
					<ImageWithTooltip
						key={idx}
						src={item.src}
						height={56}
						width={56}
						name={item.name}
						substackUrl={item.substackUrl}
						skystackUrl={item.skystackUrl}
					/>
				))}
			</div>
		</section>
	);
};

export default Hero;
