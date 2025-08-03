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
import { UserRoundPlus } from "lucide-react";

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
}

function isValidUrl(input: string) {
	try {
		new URL(input);
		return true;
	} catch {
		return false;
	}
}

export default function SearchCommand({
	open,
	onOpenChange,
	accounts,
}: SearchCommandProps) {
	const [search, setSearch] = useState("");

	// Helper function for handling account selection
	const handleAccountSelect = (skystackUrl: string) => {
		window.open(skystackUrl, "_blank", "noopener,noreferrer");
	};

	return (
		<CommandDialog open={open} onOpenChange={onOpenChange}>
			<CommandInput
				value={search}
				onValueChange={setSearch}
				placeholder="Search for Substack by name or Substack URL..."
				autoFocus
			/>
			<CommandList>
				<CommandGroup heading="Suggestions">
					{accounts.map((acc) => (
						<CommandItem
							key={acc.username}
							onSelect={() =>
								handleAccountSelect(acc.skystackUrl)
							}
							asChild
						>
							<a
								href={acc.skystackUrl}
								target="_blank"
								rel="noopener noreferrer"
								style={{ textDecoration: "none" }}
								className="flex items-center gap-3 cursor-pointer"
							>
								<Image
									src={acc.profilePicImage}
									alt={acc.name}
									width={32}
									height={32}
									className="rounded-full object-cover"
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
									className="ml-auto flex items-center gap-1 pointer-events-none bg-none border"
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
				<CommandEmpty>No results found.</CommandEmpty>
				{isValidUrl(search) && (
					<CommandGroup
						heading="Mirror Substack to Bluesky"
						forceMount
					>
						<CommandItem asChild>
							<div className="flex items-center gap-2 cursor-pointer">
								<span> </span>
								<UserRoundPlus />
								<span>Bridge Substack to Bluesky</span>
							</div>
						</CommandItem>
					</CommandGroup>
				)}
			</CommandList>
		</CommandDialog>
	);
}
