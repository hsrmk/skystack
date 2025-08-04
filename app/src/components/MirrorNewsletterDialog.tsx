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

interface MirrorNewsletterDialogProps {
	open: boolean;
	onOpenChange: (open: boolean) => void;
}

export default function MirrorNewsletterDialog({
	open,
	onOpenChange,
}: MirrorNewsletterDialogProps) {
	return (
		<Dialog open={open} onOpenChange={onOpenChange}>
			<DialogContent
				className="sm:max-w-md"
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
						Processing the Substack and importing posts and social
						graph to Bluesky.
					</DialogDescription>
				</DialogHeader>
				{/* Content will be added here */}
				<div className="flex items-center justify-center gap-2">
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
			</DialogContent>
		</Dialog>
	);
}
