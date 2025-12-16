import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import NavBar from "@/sections/NavBar";
import Footer from "@/sections/Footer";

const inter = Inter({
	subsets: ["latin"],
	variable: "--font-inter",
});

export const metadata: Metadata = {
	title: "Skystack",
	description: "Follow Substack Newsletters on Bluesky",
	openGraph: {
		title: "Skystack",
		description: "Follow Substack Newsletters on Bluesky",
		images: [
			{
				url: "/skystack-og.png",
				width: 1200,
				height: 630,
				alt: "Skystack Logo",
			},
		],
		type: "website",
	},
	twitter: {
		card: "summary_large_image",
		title: "Skystack",
		description: "Follow Substack Newsletters on Bluesky",
		images: ["/skystack-og.png"],
	},
};

export default function RootLayout({
	children,
}: Readonly<{
	children: React.ReactNode;
}>) {
	return (
		<html lang="en" className="dark">
			<head>
				<meta
					name="viewport"
					content="width=device-width, initial-scale=1.0"
				/>
				<meta name="color-scheme" content="dark light" />
			</head>
			<body
				className={`${inter.variable} antialiased bg-black text-white overflow-x-hidden`}
			>
				<NavBar />
				{children}
				<Footer />
			</body>
		</html>
	);
}
