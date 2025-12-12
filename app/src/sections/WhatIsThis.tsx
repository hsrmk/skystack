import Image from "next/image";
import { ArrowRight, ArrowUpRight } from "lucide-react";
import { Roboto_Mono } from "next/font/google";

const robotoMono = Roboto_Mono({ subsets: ["latin"], weight: ["400"] });

export default function WhatIsThis() {
	return (
		<section
			className="flex flex-col gap-6 px-4 md:px-12 py-8"
			id="whatisthis"
		>
			<div className="flex flex-col items-center justify-center pt-15 gap-2">
				<p className="font-bold text-white">What is this website?</p>
				<p className="font-medium text-font-secondary text-center mx-auto">
					Skystack is a tool that allows you to follow
					<br />
					Substack newsletters on Bluesky.
				</p>
			</div>

			{/* New info rows aligned in a two-column grid */}
			<div className="mx-auto flex justify-center pt-6">
				<div className="grid w-full max-w-5xl grid-cols-1 items-start gap-y-10 md:gap-y-20 md:grid-cols-[200px_minmax(0,1fr)] md:gap-x-20">
					<a
						href="https://nitter.net/SBF_FTX/status/1591989554881658880#m"
						target="_blank"
						rel="noopener noreferrer"
						className={`${robotoMono.className} md:max-w-lg text-md text-font-secondary no-underline hover:text-white`}
					>
						1) What
					</a>
					<p className="w-full text-sm text-font-secondary md:max-w-[500px]">
						Substacks are great, but the Substack App could be
						better. The app relies heavily on algorithmic
						recommendations that prioritize content designed for
						recency and engagement.
						<br />
						<br />
						Bluesky gives you more control over your timeline. You
						can follow accounts across the fediverse without being
						limited to algorithm-driven feeds. Skystack helps you
						follow Substack Newsletters on Bluesky!
					</p>
					<div className="col-span-1 md:col-span-2 flex flex-col items-center justify-center gap-3 pt-2">
						<div className="flex items-start justify-center gap-6 md:gap-10">
							<div className="flex flex-col items-center">
								<Image
									src="/lists.png"
									alt="Substack follow"
									width={192}
									height={128}
									className="h-auto w-40 md:w-60"
									sizes="(min-width: 768px) 12rem, 8rem"
								/>
								<p className="mt-2 w-40 text-left text-sm text-font-secondary md:w-60">
									Lists of Substack Bestsellers is already
									available to follow on Bluesky{" "}
									<a
										href="https://bsky.app/profile/skystack.xyz"
										target="_blank"
										rel="noopener noreferrer"
										className="inline-flex items-center text-white underline"
									>
										here.
										<ArrowUpRight className="h-4 w-4" />
									</a>
								</p>
							</div>
							<div className="flex flex-col items-center">
								<Image
									src="/subs-feed.png"
									alt="Bluesky follow"
									width={192}
									height={128}
									className="h-auto w-40 md:w-60"
									sizes="(min-width: 768px) 12rem, 8rem"
								/>
								<p className="mt-2 w-40 text-left text-sm text-font-secondary md:w-60">
									A custom feed of your subscriptions, shaped
									by the algorithms you prefer.
								</p>
							</div>
						</div>
					</div>

					<p
						className={`${robotoMono.className} md:max-w-lg text-md text-font-secondary no-underline`}
					>
						Old Posts
					</p>
					<p className="w-full text-sm text-font-secondary md:max-w-[500px]">
						Substack’s RSS feeds only show the 20 most recent posts,
						which means older content stays hidden in the archives.
						<br /> <br />
						While tools like{" "}
						<a
							href="https://fed.brid.gy/"
							target="_blank"
							rel="noopener noreferrer"
							className="text-white underline"
						>
							Bridgy Fed
						</a>{" "}
						can help bring RSS feeds to Bluesky, they’re also
						limited by this 20-post cap. Skystack goes further by
						mirroring posts to Bluesky that are older than what
						appears in the RSS feed, making more of a newsletter’s
						archive accessible.
					</p>

					<p
						className={`${robotoMono.className} md:max-w-lg text-md text-font-secondary no-underline`}
					>
						Social Graph
					</p>
					<p className="w-full text-sm text-font-secondary md:max-w-[500px]">
						Substack has a rich network of interconnected
						newsletters. By capturing these connections, Skystack
						helps you discover new newsletters on Bluesky too.
					</p>
				</div>
			</div>

			{/* Follow flow: Substack -> Arrow (left) -> Bluesky */}
			<div className="mx-auto flex w-full items-center justify-center gap-6 pt-10 md:gap-10">
				<Image
					src="/substack_follow.png"
					alt="Substack follow"
					width={192}
					height={128}
					className="h-auto w-40 md:w-60"
					sizes="(min-width: 768px) 12rem, 8rem"
				/>
				<ArrowRight className="h-4 w-4 text-font-secondary md:h-4 md:w-4" />
				<Image
					src="/bsky_follow.png"
					alt="Bluesky follow"
					width={192}
					height={128}
					className="h-auto w-40 md:w-60"
					sizes="(min-width: 768px) 12rem, 8rem"
				/>
			</div>
		</section>
	);
}
