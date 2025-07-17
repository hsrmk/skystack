"use client";
import Box from "@/components/Box";
import React, { useState } from "react";
import Image from "next/image";
import { ArrowUpRight, Menu, X } from "lucide-react";

function NavLinks({ className = "" }: { className?: string }) {
	return (
		<div
			className={`flex flex-col lg:flex-row gap-2 lg:gap-8 text-sm ${className}`}
		>
			<a
				href="#"
				className="text-font-secondary hover:text-font-primary font-medium px-2 py-2 rounded transition-colors"
			>
				Browse Accounts
			</a>
			<a
				href="#"
				className="text-font-secondary hover:text-font-primary font-medium px-2 py-2 rounded transition-colors"
			>
				What is this?
			</a>
			<a
				href="#"
				target="_blank"
				rel="noopener noreferrer"
				className="flex items-center text-font-secondary hover:text-font-primary font-medium px-2 py-2 rounded transition-colors"
			>
				GitHub <ArrowUpRight size={16} />
			</a>
		</div>
	);
}

function LoginButton({ className = "" }: { className?: string }) {
	return (
		<button
			className={`flex items-center gap-2 bg-white text-slate-900 text-sm font-medium rounded-lg shadow hover:bg-slate-300 transition-colors ${className}`}
		>
			<Image src="/bluesky.svg" alt="Logo" width={16} height={14} />
			<span>Login with Bluesky</span>
		</button>
	);
}

export default function NavBar() {
	const [menuOpen, setMenuOpen] = useState(false);

	return (
		<Box className="fixed top-4 left-1/12 z-50 px-8 py-3.5 w-5/6 mx-auto">
			{/* Desktop Nav */}
			<nav className="flex items-center justify-between w-full lg:flex">
				{/* Left: Logo + Text */}
				<div className="flex items-center gap-2">
					<Image
						src="/skystack-logo.png"
						alt="Logo"
						width={32}
						height={32}
						className="h-8 w-8"
					/>
					<span className="font-bold text-slate-50">SkyStack</span>
				</div>

				{/* Center: Links (Desktop only) */}
				<div className="hidden lg:flex mx-auto">
					<NavLinks className="flex-row gap-8" />
				</div>

				{/* Right: Button (Desktop only) */}
				<div className="hidden lg:flex">
					<LoginButton className="px-4 py-2" />
				</div>

				{/* Hamburger (Mobile only) */}
				<div className="lg:hidden flex items-center">
					<button
						aria-label={menuOpen ? "Close menu" : "Open menu"}
						onClick={() => setMenuOpen((v) => !v)}
						className="p-2 rounded focus:outline-none"
					>
						{menuOpen ? (
							<X size={24} className="text-slate-200" />
						) : (
							<Menu size={24} className="text-slate-200" />
						)}
					</button>
				</div>
			</nav>

			{/* Mobile Menu (expanded) */}
			<div
				className={`lg:hidden overflow-hidden transition-[max-height] duration-700 ease-in-out ${menuOpen ? "max-h-96" : "max-h-0"}`}
			>
				<div
					className={`flex flex-col gap-2 mt-6 backdrop-blur-md transition-all duration-500 ${menuOpen ? "opacity-100 blur-0" : "opacity-0 blur-sm pointer-events-none"}`}
				>
					<NavLinks />
					<LoginButton className="px-5 py-3 my-2 max-w-fit" />
				</div>
			</div>
		</Box>
	);
}
