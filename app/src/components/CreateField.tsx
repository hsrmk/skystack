import React from "react";
import { ArrowRight } from "lucide-react";
import Box from "@/components/Box";

export default function CreateField({
	onClick,
}: {
	onClick?: React.MouseEventHandler<HTMLDivElement>;
}) {
	return (
		<Box
			onClick={onClick}
			className="pointer-events-auto cursor-pointer p-6 lg:py-6 lg:pl-6 lg:pr-20 flex flex-col items-start gap-4 text-sm min-w-5/6 lg:min-w-0 lg:w-auto"
		>
			<p className="text-font-secondary font-medium">
				Enter a Substack URL to follow on Bluesky...
			</p>
			<p className="flex flex-row items-center gap-2 font-medium">
				Start Processing
				<ArrowRight size={16} />
			</p>
		</Box>
	);
}
