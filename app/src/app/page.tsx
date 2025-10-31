"use client";

import { useEffect, useState, useCallback } from "react";
import Hero from "@/sections/Hero";
import Browse from "@/sections/Browse";
import { browseSectionPartialData } from "@/lib/browseSectionPartialData";
import SearchCommand from "@/sections/SearchCommand";
import WhatIsThis from "@/sections/WhatIsThis";

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

	// Move fetchAndMergeData out and define refresh
	const fetchAndMergeData = async () => {
		try {
			const response = await fetch(
				"https://firebasestorage.googleapis.com/v0/b/vibrant-victory-469112-d7.firebasestorage.app/o/static%2Fnewsletters.json?alt=media",
				{ cache: "no-store" }
			);
			const remoteData: AccountData[] = await response.json();
			const partialUsernames = new Set(
				browseSectionPartialData.map((item) => item.username)
			);
			const filteredRemoteData = remoteData.filter(
				(item) => !partialUsernames.has(item.username)
			);
			const merged = [...browseSectionPartialData, ...filteredRemoteData];
			console.log(merged);
			setMergedData(merged);
		} catch (error) {
			console.error("Error fetching data:", error);
			setMergedData(browseSectionPartialData);
		} finally {
			setIsLoading(false);
		}
	};
	// Initial load
	useEffect(() => {
		console.log("Fetching and merging..");
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

	// Add a callback for refresh
	const refreshMergedData = (newAccount?: AccountData) => {
		console.log("onFinish (refreshMergedData) starts");
		if (newAccount) {
			setMergedData((prev) => {
				const exists = prev.some(
					(item) => item.username === newAccount.username
				);
				return exists ? prev : [...prev, newAccount];
			});
			console.log("onFinish (refreshMergedData) ends with local append");
			return;
		}
		setIsLoading(true);
		fetchAndMergeData();
		console.log("onFinish (refreshMergedData) ends");
	};

	return (
		<>
			<SearchCommand
				open={searchOpen}
				onOpenChange={setSearchOpen}
				accounts={mergedData}
				onRefresh={refreshMergedData}
			/>
			<Hero onCommandOpenChange={setSearchOpen} />
			<Browse
				data={mergedData}
				isLoading={isLoading}
				onCommandOpenChange={setSearchOpen}
			/>
			<WhatIsThis />
		</>
	);
}
