"use client";

import React, { useState, useEffect, useRef } from "react";
import ImageWithTooltip from "@/components/ImageWithTooltip";
import { newsletterDataJson } from "@/lib/newsletterData";

interface GridItem {
	id: number;
	src: string;
	name: string;
	substackUrl: string;
	skystackUrl: string;
	col: number;
	row: number;
}

const ITEM_WIDTH = 100;
const ITEM_HEIGHT = 100;
const GAP = 30;

export default function Hero() {
	const containerRef = useRef<HTMLDivElement>(null);
	const [gridItems, setGridItems] = useState<GridItem[]>([]);
	const [gridStyles, setGridStyles] = useState({});

	useEffect(() => {
		const calculateGrid = () => {
			if (!containerRef.current) return;

			const { offsetWidth, offsetHeight } = containerRef.current;
			const columns = Math.floor(
				(offsetWidth + GAP) / (ITEM_WIDTH + GAP)
			);
			const rows = Math.floor((offsetHeight + GAP) / (ITEM_HEIGHT + GAP));

			if (columns <= 0 || rows <= 0) {
				setGridItems([]);
				return;
			}

			setGridStyles({
				display: "inline-grid",
				gridTemplateColumns: `repeat(${columns}, ${ITEM_WIDTH}px)`,
				gridTemplateRows: `repeat(${rows}, ${ITEM_HEIGHT}px)`,
				gap: `${GAP}px`,
			});

			const items: GridItem[] = [];
			let dataIndex = 0;

			for (let r = 0; r < rows; r++) {
				if (dataIndex >= newsletterDataJson.length) break;

				const addAnItem = (col: number, row: number) => {
					if (dataIndex < newsletterDataJson.length) {
						items.push({
							...newsletterDataJson[dataIndex++],
							col: col + 1,
							row: row + 1,
						});
					}
				};

				if (r < 2) {
					if (columns > 1) {
						addAnItem(0, r);
						addAnItem(columns - 1, r);
					} else {
						addAnItem(0, r);
					}
				} else {
					// For r>=2, determine how many items fit on each side
					if (columns === 1) {
						addAnItem(0, r);
					} else {
						const itemsToPlacePerSide = Math.min(
							r,
							Math.floor(columns / 2)
						);
						for (let i = 0; i < itemsToPlacePerSide; i++) {
							// Add from left
							addAnItem(i, r);
							// Add from right
							addAnItem(columns - 1 - i, r);
						}
					}
				}
			}
			setGridItems(items);
		};

		calculateGrid();

		const resizeObserver = new ResizeObserver(calculateGrid);
		if (containerRef.current) {
			resizeObserver.observe(containerRef.current);
		}

		return () => {
			if (containerRef.current) {
				resizeObserver.unobserve(containerRef.current);
			}
		};
	}, []);

	return (
		<section
			ref={containerRef}
			className="h-screen w-screen overflow-hidden p-4 text-center"
		>
			<div style={gridStyles}>
				{gridItems.map((item) => (
					<div
						key={item.id}
						style={{
							gridColumnStart: item.col,
							gridRowStart: item.row,
						}}
						className="flex items-center justify-center"
					>
						<ImageWithTooltip
							src={item.src}
							name={item.name}
							substackUrl={item.substackUrl}
							skystackUrl={item.skystackUrl}
							height={ITEM_HEIGHT}
							width={ITEM_WIDTH}
						/>
					</div>
				))}
			</div>
		</section>
	);
}
