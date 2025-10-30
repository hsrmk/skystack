import React, { useEffect, useRef, useState } from "react";
import PulseDot from "@/components/PulseDot";
import { AccountCard } from "@/components/AccountCard";

interface ProcessingSubstackProps {
	url: string;
}

// Types for event
interface EventItem {
	state: "step_completed" | "in_progress" | "error" | "finished";
	message: string;
	submessage?: string;
	// AccountCard props for finished state
	profilePicImage?: string;
	name?: string;
	username?: string;
	description?: string;
	substackUrl?: string;
	skystackUrl?: string;
}

// Removed dummyEvents and simulation interval logic

export default function ProcessingSubstack({ url }: ProcessingSubstackProps) {
	const [events, setEvents] = useState<EventItem[]>([]);
	const abortControllerRef = useRef<AbortController | null>(null);
	const containerRef = useRef<HTMLDivElement>(null);

	useEffect(() => {
		let cancelled = false;
		abortControllerRef.current?.abort(); // Clean up previous instance if any
		abortControllerRef.current = new AbortController();
		setEvents([]);

		async function connectSSE() {
			try {
				const response = await fetch(
					"https://skystack-apis-937189978209.us-central1.run.app/createNewsletter",
					{
						method: "POST",
						headers: {
							"Content-Type": "application/json",
						},
						body: JSON.stringify({ url }),
						signal: abortControllerRef.current!.signal,
					}
				);
				if (!response.body || !response.ok)
					throw new Error("No response body");

				const reader = response.body.getReader();
				let buffer = "";
				while (!cancelled) {
					const { value, done } = await reader.read();
					if (done) break;
					buffer += new TextDecoder().decode(value, { stream: true });
					while (true) {
						const eventEnd = buffer.indexOf("\n\n");
						if (eventEnd === -1) break;
						const eventRaw = buffer.slice(0, eventEnd).trim();
						buffer = buffer.slice(eventEnd + 2);
						for (const line of eventRaw.split("\n")) {
							if (line.startsWith("data: ")) {
								try {
									const parsed = JSON.parse(
										line.replace("data: ", "")
									);
									// Defensive: check shape
									if (
										parsed &&
										parsed.state &&
										parsed.message
									) {
										setEvents((prev) => [...prev, parsed]);
									}
								} catch {}
							}
						}
					}
				}
			} catch (err) {
				if (!cancelled) {
					setEvents((prev) => [
						...prev,
						{
							state: "error",
							message: "Failed to connect to Skystack.",
							submessage:
								err instanceof Error
									? err.message
									: "Unknown error",
						},
					]);
				}
			}
		}

		connectSSE();
		return () => {
			cancelled = true;
			abortControllerRef.current?.abort();
		};
	}, [url]);

	// Scroll to bottom on new event
	useEffect(() => {
		if (containerRef.current) {
			containerRef.current.scrollTop = containerRef.current.scrollHeight;
		}
	}, [events]);

	return (
		<div
			ref={containerRef}
			className="h-64 overflow-y-auto pr-2 scrollbar-hide p-4"
			style={{ scrollbarWidth: "none" }}
		>
			{events.length === 0 && (
				<div className="text-center text-gray-500 py-8">
					Connecting to Skystack...
				</div>
			)}
			<ul className="flex flex-col relative">
				{events.map((event, idx) => {
					console.log("Rendering event:", event, "at index:", idx);

					if (!event) return null;
					// Special state handling for last item
					const isLast = idx === events.length - 1;
					let state = event.state;
					if (isLast && state === "step_completed")
						state = "in_progress";

					// Error/finished overrides
					let message = event.message;
					let submessage = event.submessage;
					if (state === "error") {
						message = "Oops! Something went wrong.";
						submessage =
							"Reported to Admin. Please check later, the newsletter should be available for use.";
					}

					return (
						<li
							key={idx + event.message}
							className="flex items-start relative"
						>
							{/* Timeline column: PulseDot and dotted line */}
							<div className="flex flex-col items-center mr-4 mt-2">
								{/* Padding above first dot */}
								{idx === 0 && <div className="h-1" />}
								<PulseDot state={state} size="sm" />
								{/* Dotted line below (for all except last) - longer to create space between content blocks */}
								{!isLast && (
									<div
										className="w-px h-10 border-l-2 border-dotted border-gray-700 mt-2"
										aria-hidden
									/>
								)}
							</div>
							<div className="flex-1 min-w-0">
								{state === "finished" ? (
									<>
										<div className="text-sm mb-2">
											{message}
										</div>
										<AccountCard
											profilePicImage={
												event.profilePicImage || ""
											}
											name={event.name || ""}
											username={event.username || ""}
											description={
												event.description || ""
											}
											substackUrl={
												event.substackUrl || ""
											}
											skystackUrl={
												event.skystackUrl || ""
											}
										/>
									</>
								) : (
									<>
										<div className="text-sm">{message}</div>
										{submessage && (
											<div className="text-sm text-gray-400">
												{submessage}
											</div>
										)}
									</>
								)}
							</div>
						</li>
					);
				})}
			</ul>
		</div>
	);
}
