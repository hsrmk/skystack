import Image from "next/image";

export default function Footer() {
	return (
		<section className="flex flex-col md:flex-row gap-6 px-4 md:px-12 pt-14 pb-10 items-center justify-between w-full">
			<div className="flex items-center gap-4">
				<Image
					src="/skystack-logo.png"
					alt="Skystack Logo"
					width={35}
					height={35}
				/>
				<div className="flex flex-col items-start">
					<p className="font-bold text-white">Skystack</p>
					<p className="text-xs text-font-secondary">
						Follow Substack Newsletters on Bluesky
					</p>
				</div>
			</div>
			<div className="flex flex-row gap-6">
				<a href="" target="_blank" rel="noopener noreferrer">
					<Image
						src="/bluesky.svg"
						alt="Bluesky Skystack"
						width={35}
						height={35}
						className="hover:opacity-70"
					/>
				</a>
				<a
					href="https://github.com/hsrmk/skystack"
					target="_blank"
					rel="noopener noreferrer"
				>
					<Image
						src="/github.svg"
						alt="Github Skystack"
						width={30}
						height={30}
						className="hover:opacity-70"
					/>
				</a>
			</div>
		</section>
	);
}
