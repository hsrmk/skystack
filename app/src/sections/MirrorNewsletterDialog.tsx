"use client";

import React from "react";
import Image from "next/image";
import {
	Dialog,
	DialogContent,
	DialogHeader,
	DialogTitle,
} from "@/components/ui/dialog";
import { DialogDescription } from "@radix-ui/react-dialog";

import Box from "@/components/Box";
import DottedBorder from "@/components/DottedBorder";
// import PulseDot from "@/components/PulseDot";
import ProcessingSubstack from "@/sections/ProcessingSubstack";

interface AccountData {
	profilePicImage: string;
	name: string;
	username: string;
	description: string;
	substackUrl: string;
	skystackUrl: string;
}

interface MirrorNewsletterDialogProps {
	url: string;
	open: boolean;
	onOpenChange: (open: boolean) => void;
	onRefresh?: (account: AccountData) => void;
}

export default function MirrorNewsletterDialog({
	url,
	open,
	onOpenChange,
	onRefresh,
}: MirrorNewsletterDialogProps) {
	return (
		<Dialog open={open} onOpenChange={onOpenChange}>
			<DialogContent
				className="sm:max-w-lg"
				onPointerDownOutside={(e) => {
					e.preventDefault();
				}}
				onInteractOutside={(e) => {
					e.preventDefault();
				}}
			>
				<DialogHeader className="gap-1">
					<DialogTitle className="text-sm">
						Mirror Newsletter to Bluesky
					</DialogTitle>
					<DialogDescription className="text-sm text-font-secondary">
						Importing posts and social graph to Bluesky for{" "}
						<a
							href={url}
							target="_blank"
							rel="noopener noreferrer"
							className="hover:text-white underline"
						>
							{url}
						</a>
					</DialogDescription>
				</DialogHeader>
				{/* Content will be added here */}
				<div className="flex items-center justify-center gap-2 pt-2 pb-4">
					<Box className="p-3 w-14 h-14 flex items-center justify-center">
						<Image
							src="/substack.svg"
							alt="Substack Logo"
							width={30}
							height={30}
						/>
					</Box>
					<DottedBorder />
					<Box className="p-3 w-14 h-14 flex items-center justify-center">
						<Image
							src="/bluesky.svg"
							alt="Bluesky Logo"
							width={30}
							height={30}
						/>
					</Box>
				</div>
				{/* <PulseDot state="error" size="sm" /> */}
				<ProcessingSubstack url={url} onFinish={onRefresh} />
			</DialogContent>
		</Dialog>
	);
}
