import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import NavBar from "@/sections/NavBar";

const inter = Inter({
	subsets: ["latin"],
	variable: "--font-inter",
});

export const metadata: Metadata = {
	title: "Skystack",
	description: "Follow Substack Newsletters on Bluesky",
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
				className={`${inter.variable} antialiased bg-black text-white`}
			>
				<NavBar />
				{children}
			</body>
		</html>
	);
}
