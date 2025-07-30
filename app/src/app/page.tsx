"use client";
import Hero from "@/sections/Hero";
import Browse from "@/sections/Browse";
import { useEffect, useState, useRef } from "react";
import { browseSectionPartialData } from "@/lib/browseSectionPartialData";

const REMOTE_URL =
	"https://gist.githubusercontent.com/hsrmk/1027b77ed539bb5296bc2154445687d3/raw/76ae2aa53a2a0f9910a6e79a9535a64672f5b627/skystack_mock_data.json";
const PAGE_SIZE = 6;

type AccountData = {
	profilePicImage: string;
	name: string;
	username: string;
	description: string;
	substackUrl: string;
	skystackUrl: string;
};

export default function Home() {
	const [remoteData, setRemoteData] = useState<AccountData[]>([]);
	const [remoteLoaded, setRemoteLoaded] = useState(false);
	const [page, setPage] = useState(1); // 1 = just initial, 2 = +6, etc.
	const [loadingMore, setLoadingMore] = useState(false);
	const fetchedRef = useRef(false);

	// Prefetch remote JSON after initial render
	useEffect(() => {
		if (!fetchedRef.current) {
			fetchedRef.current = true;
			console.log("Fetching remote data from:", REMOTE_URL);
			fetch(REMOTE_URL)
				.then((res) => {
					console.log("Response status:", res.status);
					console.log("Response headers:", res.headers);
					if (!res.ok) {
						throw new Error(`HTTP error! status: ${res.status}`);
					}
					return res.text();
				})
				.then((text) => {
					console.log("Raw response text:", text);
					return JSON.parse(text);
				})
				.then((data: AccountData[]) => {
					// Deduplicate using username
					console.log("Parsed data:", data);
					console.log("Data length:", data.length);

					const initialUsernames = new Set(
						browseSectionPartialData.map((item) => item.username)
					);
					console.log(
						"Initial usernames:",
						Array.from(initialUsernames)
					);

					const filtered = data.filter(
						(item: AccountData) =>
							!initialUsernames.has(item.username)
					);
					console.log("Filtered data:", filtered);
					console.log("Filtered length:", filtered.length);

					setRemoteData(filtered);
					setRemoteLoaded(true);
				})
				.catch((error) => {
					console.error("Fetch error:", error);
					setRemoteLoaded(true); // Mark as loaded even if failed (silent fail)
				});
		}
	}, []);

	// Compute what to show
	const initial = browseSectionPartialData;
	const remoteToShow = remoteData.slice(0, (page - 1) * PAGE_SIZE);
	const allToShow = [...initial, ...remoteToShow];
	const hasMore = remoteData.length > remoteToShow.length;

	// Handler for Load More
	const handleLoadMore = () => {
		if (!remoteLoaded) {
			setLoadingMore(true);
			// Wait for remote to load, then increment page
			const interval = setInterval(() => {
				if (remoteLoaded) {
					setPage((p) => p + 1);
					setLoadingMore(false);
					clearInterval(interval);
				}
			}, 100);
		} else {
			setPage((p) => p + 1);
		}
	};

	return (
		<>
			<Hero />
			<Browse
				data={allToShow}
				onLoadMore={handleLoadMore}
				hasMore={hasMore}
				loadingMore={loadingMore || (!remoteLoaded && page > 1)}
			/>
		</>
	);
}
