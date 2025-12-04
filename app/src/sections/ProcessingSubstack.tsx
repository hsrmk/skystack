import React, { useEffect, useRef, useState } from "react";
import PulseDot from "@/components/PulseDot";
import { AccountCard } from "@/components/AccountCard";

interface FinishedAccountData {
	profilePicImage: string;
	name: string;
	username: string;
	description: string;
	substackUrl: string;
	skystackUrl: string;
}

interface ProcessingSubstackProps {
	url: string;
	onFinish?: (account: FinishedAccountData) => void;
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

export default function ProcessingSubstack({
	url,
	onFinish,
}: ProcessingSubstackProps) {
	const [events, setEvents] = useState<EventItem[]>([]);
	const abortControllerRef = useRef<AbortController | null>(null);
	const containerRef = useRef<HTMLDivElement>(null);
	const finishedCalledRef = useRef(false);

	const onFinishRef = useRef(onFinish);

	useEffect(() => {
		onFinishRef.current = onFinish;
	}, [onFinish]);

	useEffect(() => {
		// Constants
		const API_ENDPOINT =
			"https://skystack-apis-937189978209.us-central1.run.app/createNewsletter";
		const MAX_RETRIES = 3;
		const RETRY_DELAY_MS = 1000;

		let cancelled = false;
		abortControllerRef.current?.abort();
		setEvents([]);
		finishedCalledRef.current = false;

		// Helper: Extract base URL from input
		const getBaseUrl = (inputUrl: string): string => {
			try {
				const parsed = new URL(inputUrl);
				return `${parsed.protocol}//${parsed.host}`;
			} catch {
				return inputUrl;
			}
		};

		// Helper: Create newsletter API request
		const createNewsletterRequest = async (
			cleanedUrl: string,
			signal: AbortSignal
		): Promise<Response> => {
			const response = await fetch(API_ENDPOINT, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({ url: cleanedUrl }),
				signal,
			});

			if (!response.body || !response.ok) {
				throw new Error("No response body");
			}

			return response;
		};

		// Helper: Parse event from SSE data line
		const parseEventLine = (line: string): EventItem | null => {
			if (!line.startsWith("data: ")) return null;

			try {
				const parsed = JSON.parse(line.replace("data: ", ""));
				if (parsed?.state && parsed?.message) {
					return parsed as EventItem;
				}
			} catch {
				// Invalid JSON, skip
			}

			return null;
		};

		// Helper: Extract finished data from event
		const extractFinishedData = (
			event: EventItem
		): FinishedAccountData => ({
			profilePicImage: event.profilePicImage || "",
			name: event.name || "",
			username: event.username || "",
			description: event.description || "",
			substackUrl: event.substackUrl || "",
			skystackUrl: event.skystackUrl || "",
		});

		// Helper: Handle event processing
		// Returns: true = continue, false = error (retry), "finished" = success (stop)
		const handleEvent = (
			event: EventItem,
			isLastRetry: boolean
		): boolean | "finished" => {
			// Handle stream errors
			if (event.state === "error") {
				if (isLastRetry) {
					setEvents((prev) => [...prev, event]);
				}
				return false; // Signal failure
			}

			// Add event to state
			setEvents((prev) => [...prev, event]);

			// Handle finished state
			if (event.state === "finished" && !finishedCalledRef.current) {
				finishedCalledRef.current = true;
				const finishedData = extractFinishedData(event);
				onFinishRef.current?.(finishedData);
				return "finished"; // Signal success - stop reading
			}

			return true; // Continue reading
		};

		// Helper: Handle connection errors
		const handleConnectionError = (err: unknown, isLastRetry: boolean) => {
			if (!cancelled && isLastRetry) {
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
		};

		// Helper: Read and process event stream
		const readEventStream = async (
			reader: ReadableStreamDefaultReader<Uint8Array>,
			isLastRetry: boolean
		): Promise<boolean> => {
			let buffer = "";
			const decoder = new TextDecoder();

			while (!cancelled) {
				const { value, done } = await reader.read();
				if (done) break;

				buffer += decoder.decode(value, { stream: true });

				// Process complete events (separated by \n\n)
				while (true) {
					const eventEnd = buffer.indexOf("\n\n");
					if (eventEnd === -1) break;

					const eventRaw = buffer.slice(0, eventEnd).trim();
					buffer = buffer.slice(eventEnd + 2);

					// Parse each line in the event
					for (const line of eventRaw.split("\n")) {
						const event = parseEventLine(line);
						if (event) {
							const result = handleEvent(event, isLastRetry);
							if (result === false) {
								return false; // Error - retry
							}
							if (result === "finished") {
								return true; // Success - finished, stop reading
							}
							// result === true, continue reading
						}
					}
				}
			}

			return true; // Success
		};

		// Main SSE connection function
		const connectSSE = async (isLastRetry: boolean): Promise<boolean> => {
			try {
				const cleanedUrl = getBaseUrl(url);
				const response = await createNewsletterRequest(
					cleanedUrl,
					abortControllerRef.current!.signal
				);

				const reader = response.body!.getReader();
				return await readEventStream(reader, isLastRetry);
			} catch (err) {
				handleConnectionError(err, isLastRetry);
				return false;
			}
		};

		// Retry wrapper
		const waitBeforeRetry = (): Promise<void> => {
			return new Promise((resolve) =>
				setTimeout(resolve, RETRY_DELAY_MS)
			);
		};

		// Retry logic
		const connectWithRetry = async (): Promise<void> => {
			let retryCount = 0;

			while (retryCount < MAX_RETRIES && !cancelled) {
				// If finished was already called, don't retry
				if (finishedCalledRef.current) {
					break;
				}

				// Create new AbortController for each attempt
				abortControllerRef.current?.abort();
				abortControllerRef.current = new AbortController();

				// Clear events on retry attempts
				if (retryCount > 0) {
					setEvents([]);
				}

				const isLastRetry = retryCount === MAX_RETRIES - 1;
				const success = await connectSSE(isLastRetry);

				if (success) {
					break; // Success, exit retry loop
				}

				// If finished was called during this attempt, don't retry
				if (finishedCalledRef.current) {
					break;
				}

				retryCount++;
				if (retryCount < MAX_RETRIES && !cancelled) {
					await waitBeforeRetry();
				}
			}
		};

		connectWithRetry();

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
			className="h-72 overflow-y-auto pr-2 scrollbar-hide p-4"
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
