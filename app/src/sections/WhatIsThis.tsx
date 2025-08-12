import Image from "next/image";
import { ArrowRight } from "lucide-react";
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
						Substacks are great, the Substack App is not. The app is
						riddled with black box algorithms, and an overt focus on
						writing written for the algorithm. Skystack helps you
						follow Substack Newsletters on Bluesky.
						<br />
						<br />
						On Bluesky, we can control what we want to see in our
						timelines. I want to be able to follow my newsletters
						across the fediverse, and not be stuck in some doom-loop
						algorithm.
						<br />
						<br />
						More so, most of the great substack writing is old, and
						by relying on the latest hit pieces, we lose so much
						good content that is never able to resurface.
						<br />
						<br />
						With Bluesky’s Custom Feeds, we’re no longer limited to
						the latest posts. We can build feeds that spotlight and
						revive classic posts as well.
					</p>

					<p
						className={`${robotoMono.className} md:max-w-lg text-md text-font-secondary no-underline`}
					>
						Old Posts
					</p>
					<p className="w-full text-sm text-font-secondary md:max-w-[500px]">
						Substack’s RSS caps out at 20 posts, leaving older work
						stuck in the archives.
						<br /> <br />
						Although there exists tools like Bridgy Fed, which help
						port RSS Feeds to Bluesky, they too are limited by the
						RSS limit. Skystack is able mirrors to Bluesky posts,
						that are older than the ones listed in the RSS feed.
					</p>

					<p
						className={`${robotoMono.className} md:max-w-lg text-md text-font-secondary no-underline`}
					>
						Social Graph
					</p>
					<p className="w-full text-sm text-font-secondary md:max-w-[500px]">
						Substack has a rich social graph of newsletters. By
						capturing that, we are able to allow a lot more
						discovery on Bluesky, and hopefully help the writers
						reach their 1000 True Fans.
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
