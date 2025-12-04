import React, { useState } from "react";
import Image from "next/image";
import {
	CommandDialog,
	CommandInput,
	CommandList,
	CommandItem,
	CommandEmpty,
	CommandGroup,
	CommandSeparator,
} from "@/components/ui/command";
import { Button } from "@/components/ui/button";
import { UserRoundPlus, Loader2 } from "lucide-react";
import MirrorNewsletterDialog from "@/sections/MirrorNewsletterDialog";

interface AccountData {
	profilePicImage: string;
	name: string;
	username: string;
	description: string;
	substackUrl: string;
	skystackUrl: string;
}

interface SearchCommandProps {
	open: boolean;
	onOpenChange: (open: boolean) => void;
	accounts: AccountData[];
	onRefresh?: (account: AccountData) => void; // <-- Add this
}

function isValidUrl(input: string) {
	try {
		new URL(input);
		return true;
	} catch {
		return false;
	}
}

const ITEMS_PER_PAGE = 10;
const INITIAL_VISIBLE_COUNT = 10;

export default function SearchCommand({
	open,
	onOpenChange,
	accounts,
	onRefresh,
}: SearchCommandProps) {
	const [search, setSearch] = useState("");
	const [debouncedSearch, setDebouncedSearch] = useState("");
	const [isSearching, setIsSearching] = useState(false);
	const [visibleCount, setVisibleCount] = useState(INITIAL_VISIBLE_COUNT);
	const listRef = React.useRef<HTMLDivElement>(null);

	// Reset state when dialog closes
	React.useEffect(() => {
		if (!open) {
			const timer = setTimeout(() => {
				setSearch("");
				setDebouncedSearch("");
				setIsSearching(false);
				setVisibleCount(INITIAL_VISIBLE_COUNT);
			}, 300); // Wait for close animation
			return () => clearTimeout(timer);
		}
	}, [open]);

	// Debounce search input
	React.useEffect(() => {
		if (search.length === 0) {
			setDebouncedSearch("");
			setIsSearching(false);
			setVisibleCount(INITIAL_VISIBLE_COUNT);
			return;
		}

		setIsSearching(true);
		const timer = setTimeout(() => {
			let finalSearch = search;
			if (isValidUrl(finalSearch) && finalSearch.endsWith("/")) {
				finalSearch = finalSearch.slice(0, -1);
			}
			setDebouncedSearch(finalSearch);
			setIsSearching(false);
			setVisibleCount(INITIAL_VISIBLE_COUNT); // Reset visible count on new search
		}, 3000);

		return () => clearTimeout(timer);
	}, [search]);

	// Filter accounts based on debounced search
	const filteredAccounts = React.useMemo(() => {
		if (!debouncedSearch) return accounts;
		const lowerSearch = debouncedSearch.toLowerCase();
		return accounts.filter(
			(acc) =>
				acc.name.toLowerCase().includes(lowerSearch) ||
				acc.username.toLowerCase().includes(lowerSearch) ||
				acc.substackUrl.toLowerCase().includes(lowerSearch)
		);
	}, [accounts, debouncedSearch]);

	// Visible accounts for lazy loading
	const visibleAccounts = React.useMemo(() => {
		return filteredAccounts.slice(0, visibleCount);
	}, [filteredAccounts, visibleCount]);

	// Handle scroll for lazy loading
	const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
		const { scrollTop, scrollHeight, clientHeight } = e.currentTarget;
		if (scrollHeight - scrollTop <= clientHeight + 100) {
			setVisibleCount((prev) =>
				Math.min(prev + ITEMS_PER_PAGE, filteredAccounts.length)
			);
		}
	};

	const [mirrorDialogOpen, setMirrorDialogOpen] = useState(false);

	// Helper function for handling account selection
	const handleAccountSelect = (skystackUrl: string) => {
		window.open(skystackUrl, "_blank", "noopener,noreferrer");
	};

	// Helper function for handling mirror dialog
	const handleMirrorDialog = () => {
		setMirrorDialogOpen(true);
		onOpenChange(false); // Close the command dialog
	};

	return (
		<>
			<CommandDialog
				open={open}
				onOpenChange={onOpenChange}
				commandProps={{ shouldFilter: false }}
			>
				<div className="bg-black text-white rounded-lg shadow-lg">
					<CommandInput
						value={search}
						onValueChange={setSearch}
						placeholder="Search for Substack by Name or URL..."
						autoFocus
					/>
					<CommandList onScroll={handleScroll}>
						{isSearching ? (
							<div className="flex items-center justify-center py-6 text-sm text-muted-foreground">
								<Loader2 className="mr-2 h-4 w-4 animate-spin" />
								Searching...
							</div>
						) : (
							<>
								<CommandGroup heading="Suggestions">
									{visibleAccounts.map((acc) => (
										<CommandItem
											key={acc.username}
											onSelect={() =>
												handleAccountSelect(
													acc.skystackUrl
												)
											}
											asChild
										>
											<a
												href={acc.skystackUrl}
												target="_blank"
												rel="noopener noreferrer"
												style={{
													textDecoration: "none",
												}}
												className="flex items-center gap-3 cursor-pointer"
											>
												<Image
													src={
														acc.profilePicImage ||
														"/substack.svg"
													}
													alt={acc.name}
													width={32}
													height={32}
													className="rounded-full object-cover bg-white"
													loading="lazy"
												/>
												<div className="flex flex-col flex-1 min-w-0">
													<span className="font-medium truncate">
														{acc.name}
													</span>
													<span className="text-xs text-font-secondary truncate">
														@{acc.username}
													</span>
													<span className="sr-only invisible">
														{acc.substackUrl}
													</span>
													<span className="sr-only invisible">
														{acc.description}
													</span>
												</div>
												<Button
													variant="secondary"
													size="sm"
													className="ml-auto flex items-center gap-1 pointer-events-none bg-transparent border"
													tabIndex={-1}
													asChild
												>
													<span className="flex items-center gap-1">
														<Image
															src="/bluesky.svg"
															alt="Bluesky"
															width={16}
															height={16}
														/>
														Follow
													</span>
												</Button>
											</a>
										</CommandItem>
									))}
								</CommandGroup>

								<CommandSeparator />
								{filteredAccounts.length === 0 && (
									<CommandEmpty>
										No results found.
									</CommandEmpty>
								)}
								{isValidUrl(search) && (
									<CommandGroup
										heading="Mirror Substack to Bluesky"
										forceMount
									>
										<CommandItem
											onSelect={handleMirrorDialog}
										>
											<div className="flex items-center gap-2 cursor-pointer">
												<span> </span>
												<UserRoundPlus />
												<span>
													Start processing Substack
												</span>
											</div>
										</CommandItem>
									</CommandGroup>
								)}
							</>
						)}
					</CommandList>
				</div>
			</CommandDialog>

			<MirrorNewsletterDialog
				url={search}
				open={mirrorDialogOpen}
				onOpenChange={setMirrorDialogOpen}
				onRefresh={onRefresh}
			/>
		</>
	);
}
