import React from "react";

interface BoxProps extends React.HTMLAttributes<HTMLDivElement> {
	className?: string;
	children: React.ReactNode;
}

export default function Box({ className = "", children }: BoxProps) {
	return (
		<div
			className={`inset-shadow-2xs inset-shadow-slate-500/80 rounded-2xl border border-slate-50/7 lg:border-slate-50/5 bg-gradient-to-br from-midnight/80 to-latenight/30 backdrop-blur ${className}`}
		>
			{children}
		</div>
	);
}
