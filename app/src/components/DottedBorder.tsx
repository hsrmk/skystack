import React from "react";

// Define the types for the component's props
interface DottedBorderProps {
	orientation?: "horizontal" | "vertical";
	width?: number;
	height?: number;
}

const DottedBorder: React.FC<DottedBorderProps> = ({
	orientation = "horizontal",
	width = 50,
	height = 200,
}) => {
	// --- Constants for a Fixed Appearance ---
	const DOT_SIZE = 1.5; // Each dot will be 1.5x1,5 pixels.
	const DOT_SPACING = 2; // The space between each dot will be 2px.
	const WAVE_DURATION = 2.0; // The animation "wave" takes 2 second to cross the line.

	// Determine the primary axis length based on orientation
	const effectiveLength = orientation === "horizontal" ? width : height;

	// --- Dynamic Calculation Logic ---

	// 1. Calculate how many dots (with their spacing) can fit in the given length.
	const numberOfDots = Math.floor(effectiveLength / (DOT_SIZE + DOT_SPACING));

	// --- Style Objects ---
	const containerStyle: React.CSSProperties = {
		// The container's cross-axis size is determined by the fixed dot size.
		width: orientation === "horizontal" ? `${width}px` : `${DOT_SIZE}px`,
		height: orientation === "vertical" ? `${height}px` : `${DOT_SIZE}px`,
	};

	const dotsContainerStyle: React.CSSProperties = {
		display: "flex",
		flexDirection: orientation === "horizontal" ? "row" : "column",
		gap: `${DOT_SPACING}px`, // Use the fixed spacing value
	};

	const dotStyle: React.CSSProperties = {
		width: `${DOT_SIZE}px`, // Use the fixed dot size
		height: `${DOT_SIZE}px`,
	};

	return (
		<div
			style={containerStyle}
			className="flex items-center justify-center"
		>
			<div style={dotsContainerStyle}>
				{Array.from({ length: numberOfDots }).map((_, index) => {
					// 2. Calculate a normalized animation delay for a consistent wave speed.
					const delay = (index / numberOfDots) * WAVE_DURATION;

					return (
						<div
							key={index}
							className="bg-gray-500 animate-light-up"
							style={{
								...dotStyle, // Apply the fixed dot size
								animationDelay: `${delay}s`, // Apply the normalized delay
							}}
						></div>
					);
				})}
			</div>
		</div>
	);
};

export default DottedBorder;
