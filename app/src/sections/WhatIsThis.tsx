export default function WhatIsThis() {
	return (
		<section className="flex flex-col gap-6 px-4 md:px-12 py-8">
			<div className="flex flex-col items-center justify-center pt-15 gap-2">
				<p className="font-bold text-white">What is this website?</p>
				<p className="font-medium text-font-secondary text-center mx-auto">
					Skystack is a tool that allows you to follow
					<br />
					Substack newsletters on Bluesky.
				</p>
			</div>
		</section>
	);
}
