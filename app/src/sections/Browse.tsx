import { AccountCard } from "@/components/AccountCard";
import { Button } from "@/components/ui/button";
import { Loader2Icon } from "lucide-react";

interface BrowseProps {
	data: {
		profilePicImage: string;
		name: string;
		username: string;
		description: string;
		substackUrl: string;
		skystackUrl: string;
	}[];
	onLoadMore: () => void;
	hasMore: boolean;
	loadingMore: boolean;
}

export default function Browse({
	data,
	onLoadMore,
	hasMore,
	loadingMore,
}: BrowseProps) {
	return (
		<section className="flex flex-col md:grid md:grid-cols-2 lg:grid-cols-3 gap-6 px-4 md:px-12 py-8">
			{data.map((item) => (
				<AccountCard key={item.username} {...item} />
			))}
			{hasMore && (
				<div className="col-span-full flex justify-center mt-4">
					<Button
						size="sm"
						onClick={onLoadMore}
						disabled={loadingMore}
					>
						{loadingMore ? (
							<>
								<Loader2Icon className="animate-spin" />
								Loading...
							</>
						) : (
							"Load More"
						)}
					</Button>
				</div>
			)}
		</section>
	);
}
