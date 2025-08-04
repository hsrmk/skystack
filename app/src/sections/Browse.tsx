"use client";

import { useState } from "react";
import { ArrowRight, Loader2Icon, Search } from "lucide-react";
import { AccountCard } from "@/components/AccountCard";
import { Button } from "@/components/ui/button";
import Box from "@/components/Box";

interface BrowseProps {
	data: {
		profilePicImage: string;
		name: string;
		username: string;
		description: string;
		substackUrl: string;
		skystackUrl: string;
	}[];
	isLoading: boolean;
	onCommandOpenChange: (open: boolean) => void;
}

export default function Browse({
	data,
	isLoading,
	onCommandOpenChange,
}: BrowseProps) {
	const [displayedCount, setDisplayedCount] = useState(6);
	const itemsPerPage = 6;

	const displayedData = data.slice(0, displayedCount);
	const hasMoreItems = displayedCount < data.length;

	const handleLoadMore = () => {
		setDisplayedCount((prev) => Math.min(prev + itemsPerPage, data.length));
	};

	return (
		<section className="flex flex-col gap-6 px-4 md:px-12 py-8">
			<div className="flex flex-col items-center justify-center pt-15 gap-2">
				<p className="font-bold text-white">Browse Accounts</p>
				<p className="font-medium text-font-secondary text-center mx-auto">
					Here you can find popular Substacks already
					<br />
					available to follow on Bluesky.
				</p>
			</div>

			<div className="flex justify-center w-full">
				<Box
					onClick={() => onCommandOpenChange(true)}
					className="text-font-secondary cursor-pointer p-6 lg:py-4 lg:pl-6 gap-2 flex flex-row items-center text-sm w-full max-w-lg justify-between"
				>
					<div className="flex flex-row items-center gap-2">
						<Search size={14} />
						<p className="font-medium">
							Search for a Substack Newsletter...
						</p>
					</div>
					<div className="px-2 py-1 rounded-sm bg-black border invisible lg:visible">
						⌘K
					</div>
				</Box>
			</div>

			{/* Grid of account cards */}
			<div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 pt-15">
				{displayedData.map((item) => (
					<AccountCard key={item.username} {...item} />
				))}
			</div>

			{/* Load More Button */}
			{hasMoreItems && (
				<div className="flex justify-center mt-8">
					<Button
						onClick={handleLoadMore}
						disabled={isLoading}
						variant="secondary"
						size="sm"
						className="px-6 bg-black border text-font-secondary"
					>
						{isLoading ? (
							<>
								<Loader2Icon className="animate-spin" />
								Loading...
							</>
						) : (
							<>
								See More
								<ArrowRight size={4} />
							</>
						)}
					</Button>
				</div>
			)}
		</section>
	);
}
