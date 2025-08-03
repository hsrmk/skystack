"use client";

import { useEffect, useState, useCallback } from "react";
import Hero from "@/sections/Hero";
import Browse from "@/sections/Browse";
import { browseSectionPartialData } from "@/lib/browseSectionPartialData";
import SearchCommand from "@/components/SearchCommand";

interface AccountData {
	profilePicImage: string;
	name: string;
	username: string;
	description: string;
	substackUrl: string;
	skystackUrl: string;
}

export default function Home() {
	const [mergedData, setMergedData] = useState<AccountData[]>(
		browseSectionPartialData
	);
	const [isLoading, setIsLoading] = useState(true);
	const [searchOpen, setSearchOpen] = useState(false);

	useEffect(() => {
		const fetchAndMergeData = async () => {
			try {
				const response = await fetch(
					"https://gist.githubusercontent.com/hsrmk/1027b77ed539bb5296bc2154445687d3/raw/76ae2aa53a2a0f9910a6e79a9535a64672f5b627/skystack_mock_data.json"
				);
				const remoteData: AccountData[] = await response.json();

				// Create a set of usernames from browseSectionPartialData for quick lookup
				const partialUsernames = new Set(
					browseSectionPartialData.map((item) => item.username)
				);

				// Filter out items from remote data that exist in browseSectionPartialData
				const filteredRemoteData = remoteData.filter(
					(item) => !partialUsernames.has(item.username)
				);

				// Merge the data: browseSectionPartialData first, then filtered remote data
				const merged = [
					...browseSectionPartialData,
					...filteredRemoteData,
				];

				setMergedData(merged);
			} catch (error) {
				console.error("Error fetching data:", error);
				// If fetch fails, just use browseSectionPartialData
				setMergedData(browseSectionPartialData);
			} finally {
				setIsLoading(false);
			}
		};

		fetchAndMergeData();
	}, []);

	// Command+K or Ctrl+K to open SearchCommand
	const handleKeyDown = useCallback((e: KeyboardEvent) => {
		if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
			e.preventDefault();
			setSearchOpen(true);
		}
	}, []);

	useEffect(() => {
		document.addEventListener("keydown", handleKeyDown);
		return () => document.removeEventListener("keydown", handleKeyDown);
	}, [handleKeyDown]);

	return (
		<>
			<SearchCommand
				open={searchOpen}
				onOpenChange={setSearchOpen}
				accounts={mergedData}
			/>
			<Hero data={mergedData} />
			<Browse data={mergedData} isLoading={isLoading} />
		</>
	);
}
