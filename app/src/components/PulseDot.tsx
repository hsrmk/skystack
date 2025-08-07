import React from "react";

type PulseDotState = "step_completed" | "in_progress" | "error" | "finished";

interface PulseDotProps {
	state: PulseDotState;
	size?: "sm" | "md" | "lg";
	className?: string;
}

const PulseDot: React.FC<PulseDotProps> = ({
	state,
	size = "md",
	className = "",
}) => {
	const getStateStyles = () => {
		switch (state) {
			case "step_completed":
				return "bg-gray-700";
			case "in_progress":
				return "bg-blue-500";
			case "error":
				return "bg-red-500";
			case "finished":
				return "bg-green-500";
			default:
				return "bg-gray-700";
		}
	};

	const getSizeStyles = () => {
		switch (size) {
			case "sm":
				return "w-2 h-2";
			case "md":
				return "w-3 h-3";
			case "lg":
				return "w-4 h-4";
			default:
				return "w-3 h-3";
		}
	};

	const shouldPulse = state !== "step_completed";

	return (
		<div className={`relative inline-block ${className}`}>
			{/* Main dot */}
			<div
				className={`
                ${getSizeStyles()} 
                ${getStateStyles()} 
                rounded-full 
                relative 
                z-10
                `}
			/>

			{/* Pulse animation for in_progress and error states */}
			{shouldPulse && (
				<>
					<div
						className={`
                            ${getSizeStyles()} 
                            ${getStateStyles()} 
                            rounded-full 
                            absolute 
                            top-0 
                            left-0 
                            animate-ping
                            opacity-75
                            `}
					/>
					<div
						className={`
                            ${getSizeStyles()} 
                            ${getStateStyles()} 
                            rounded-full 
                            absolute 
                            top-0 
                            left-0 
                            animate-ping 
                            opacity-50
                            [animation-delay:2s]
                            `}
					/>
				</>
			)}
		</div>
	);
};

export default PulseDot;
