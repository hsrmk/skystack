import * as React from "react";

interface DottedBorderProps {
	width?: number;
	height?: number;
	orientation?: "horizontal" | "vertical";
	animate?: boolean;
	animationDuration?: number;
	animationDirection?: "forward" | "reverse";
	className?: string;
}

const DottedBorder: React.FC<DottedBorderProps> = ({
	width = 85,
	height = 1,
	orientation = "horizontal",
	animate = false,
	animationDuration = 2,
	animationDirection = "forward",
	className = "",
}) => {
	const isHorizontal = orientation === "horizontal";
	const actualWidth = isHorizontal ? width : height;
	const actualHeight = isHorizontal ? height : width;

	// Generate unique ID for the gradient to avoid conflicts
	const gradientId = React.useId();
	const uniqueId = gradientId.replace(/:/g, "");

	// Animation keyframes for gradient transform
	const animationName = `gradient-move-${uniqueId}`;

	React.useEffect(() => {
		if (!animate) return;

		// Create and inject CSS animation for gradient transform
		const style = document.createElement("style");
		const direction =
			animationDirection === "reverse" ? "reverse" : "normal";

		if (isHorizontal) {
			style.textContent = `
				@keyframes ${animationName} {
					0% { transform: translateX(-100%); }
					100% { transform: translateX(100%); }
				}
				.${animationName} {
					animation: ${animationName} ${animationDuration}s linear infinite ${direction};
				}
			`;
		} else {
			style.textContent = `
				@keyframes ${animationName} {
					0% { transform: translateY(-100%); }
					100% { transform: translateY(100%); }
				}
				.${animationName} {
					animation: ${animationName} ${animationDuration}s linear infinite ${direction};
				}
			`;
		}

		document.head.appendChild(style);

		return () => {
			document.head.removeChild(style);
		};
	}, [
		animate,
		animationName,
		animationDuration,
		animationDirection,
		isHorizontal,
	]);

	const pathD = isHorizontal
		? `M0 ${actualHeight / 2}h${actualWidth}`
		: `M${actualWidth / 2} 0v${actualHeight}`;

	// Gradient properties - making it about 120% of the total length for spotlight effect
	const gradientWidth = isHorizontal ? actualWidth * 1.2 : actualHeight * 1.2;

	const gradientProps = isHorizontal
		? {
				x1: 0,
				x2: gradientWidth,
				y1: actualHeight / 2,
				y2: actualHeight / 2,
				gradientUnits: "userSpaceOnUse" as const,
			}
		: {
				x1: actualWidth / 2,
				x2: actualWidth / 2,
				y1: 0,
				y2: gradientWidth,
				gradientUnits: "userSpaceOnUse" as const,
			};

	return (
		<svg
			xmlns="http://www.w3.org/2000/svg"
			width={actualWidth}
			height={actualHeight}
			fill="none"
			className={className}
		>
			<path stroke="url(#a)" strokeDasharray="2 2" d={pathD} />
			<defs>
				<linearGradient
					id="a"
					{...gradientProps}
					className={animate ? animationName : ""}
				>
					<stop stopColor="#fff" stopOpacity={0} />
					<stop offset={0.2} stopColor="#fff" stopOpacity={0.3} />
					<stop offset={0.5} stopColor="#fff" stopOpacity={0.6} />
					<stop offset={0.8} stopColor="#fff" stopOpacity={0.3} />
					<stop offset={1} stopColor="#fff" stopOpacity={0} />
				</linearGradient>
			</defs>
		</svg>
	);
};

export default DottedBorder;
