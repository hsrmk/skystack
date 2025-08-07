import React, { useEffect, useRef, useState } from "react";
import PulseDot from "@/components/PulseDot";
import { AccountCard } from "@/components/AccountCard";

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

// Dummy event stream simulation
type DummyEvent = Omit<
	EventItem,
	| "profilePicImage"
	| "name"
	| "username"
	| "description"
	| "substackUrl"
	| "skystackUrl"
> &
	Partial<EventItem>;

const dummyEvents: DummyEvent[] = [
	{
		state: "step_completed",
		message: "Started",
		submessage: "Started processing...",
	},
	{
		state: "step_completed",
		message: "Fetching newsletter data",
		submessage: "Contacting Substack API...",
	},
	{
		state: "step_completed",
		message: "Parsing content",
		submessage: "Extracting articles...",
	},
	// {
	// 	state: "error",
	// 	message: "Building newsletter",
	// 	submessage: "Formatting for Bluesky...",
	// },
	{
		state: "finished",
		message: "Newsletter mirrored!",
		// AccountCard props below
		profilePicImage: "/skystack-logo.png",
		name: "Jane Doe",
		username: "janedoe",
		description: "Writes about tech and society.",
		substackUrl: "https://janedoe.substack.com",
		skystackUrl: "https://bsky.app/profile/janedoe.bsky.social",
	},
];

export default function ProcessingSubstack() {
	const [events, setEvents] = useState<EventItem[]>([]);
	const intervalRef = useRef<NodeJS.Timeout | null>(null);
	const containerRef = useRef<HTMLDivElement>(null);

	console.log("Processing Substack rendering, events count:", events.length);

	// Simulate streaming events
	useEffect(() => {
		console.log("Setting up event stream...");
		intervalRef.current = setInterval(() => {
			setEvents((prev) => {
				const nextIdx = prev.length;
				if (nextIdx < dummyEvents.length) {
					const newEvent = dummyEvents[nextIdx];
					console.log("Prev:", prev);
					console.log("New:", [...prev, newEvent]);
					return [...prev, newEvent];
				} else {
					if (intervalRef.current) {
						console.log("Event stream finished");
						clearInterval(intervalRef.current);
					}
					return prev; // no change
				}
			});
		}, 2000);
		return () => {
			if (intervalRef.current) clearInterval(intervalRef.current);
		};
	}, []);

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
					Starting Processing...
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
