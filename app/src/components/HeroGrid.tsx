import React, { useState, useEffect } from "react";
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

const MOBILE_ITEM_WIDTH = 80;
const MOBILE_ITEM_HEIGHT = 80;
const MOBILE_GAP = 10;

export default function HeroGrid() {
	const [gridItems, setGridItems] = useState<GridItem[]>([]);
	const [gridStyles, setGridStyles] = useState({});

	// Mobile grid state
	const [mobileGrid, setMobileGrid] = useState<
		((typeof newsletterDataJson)[0] | null)[][]
	>([]);
	const [mobileColumns, setMobileColumns] = useState(4);

	// Desktop grid calculation using window size
	useEffect(() => {
		function calculateGrid() {
			const width = window.innerWidth;
			const height = window.innerHeight;
			const columns = Math.floor((width + GAP) / (ITEM_WIDTH + GAP));
			const rows = Math.floor((height + GAP) / (ITEM_HEIGHT + GAP));

			if (columns <= 0 || rows <= 0) {
				setGridItems([]);
				return;
			}

			setGridStyles({
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
					if (columns === 1) {
						addAnItem(0, r);
					} else {
						const itemsToPlacePerSide = Math.min(
							r,
							Math.floor(columns / 2)
						);
						for (let i = 0; i < itemsToPlacePerSide; i++) {
							addAnItem(i, r);
							addAnItem(columns - 1 - i, r);
						}
					}
				}
			}

			// Check if there's space for an additional row and add more items
			if (dataIndex < newsletterDataJson.length && rows > 0) {
				const remainingItems = newsletterDataJson.length - dataIndex;

				// Calculate if there's space for an additional row
				const totalHeightUsed = rows * (ITEM_HEIGHT + GAP) - GAP; // Subtract GAP because there's no gap after the last row
				const availableSpace = height - totalHeightUsed;
				const canFitAdditionalRow = availableSpace >= ITEM_HEIGHT / 2;

				if (canFitAdditionalRow && columns > 0) {
					// Add items to a new row
					const newRow = rows + 1;
					const itemsToAdd = Math.min(remainingItems, columns);

					for (let i = 0; i < itemsToAdd; i++) {
						if (dataIndex < newsletterDataJson.length) {
							items.push({
								...newsletterDataJson[dataIndex++],
								col: i + 1,
								row: newRow,
							});
						}
					}
				}
			}

			setGridItems(items);
		}

		calculateGrid();
		window.addEventListener("resize", calculateGrid);
		return () => window.removeEventListener("resize", calculateGrid);
	}, []);

	// Mobile grid calculation
	useEffect(() => {
		function calculateMobileGrid() {
			const width = window.innerWidth;
			const columns = Math.max(
				Math.floor(
					(width + MOBILE_GAP) / (MOBILE_ITEM_WIDTH + MOBILE_GAP)
				),
				4
			);
			const rows = 4;
			let dataIndex = 0;
			const grid: ((typeof newsletterDataJson)[0] | null)[][] =
				Array.from({ length: rows }, () => Array(columns).fill(null));

			// Fill 4th (bottom) and 3rd rows fully
			for (let r = rows - 1; r >= rows - 2; r--) {
				for (let c = 0; c < columns; c++) {
					grid[r][c] = newsletterDataJson[dataIndex++];
				}
			}

			// 1st and 2nd row: leftmost and rightmost
			grid[1][0] = newsletterDataJson[dataIndex++];
			grid[1][columns - 1] = newsletterDataJson[dataIndex++];
			grid[0][0] = newsletterDataJson[dataIndex++];
			grid[0][columns - 1] = newsletterDataJson[dataIndex++];

			setMobileGrid(grid);
			setMobileColumns(columns);
		}

		calculateMobileGrid();
		window.addEventListener("resize", calculateMobileGrid);
		return () => window.removeEventListener("resize", calculateMobileGrid);
	}, []);

	return (
		<>
			{/* Desktop Grid */}
			<div className="hidden lg:inline-grid" style={gridStyles}>
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

			{/* Mobile Grid */}
			<div
				className="lg:hidden absolute left-0 bottom-0 w-full flex justify-center"
				style={{ pointerEvents: "auto" }}
			>
				<div
					style={{
						display: "grid",
						gridTemplateColumns: `repeat(${mobileColumns}, ${MOBILE_ITEM_WIDTH}px)`,
						gridTemplateRows: `repeat(4, ${MOBILE_ITEM_HEIGHT}px)`,
						gap: `${MOBILE_GAP}px`,
						marginBottom: 16,
					}}
				>
					{mobileGrid.flatMap((row, rowIndex) =>
						row.map((cell, colIndex) =>
							cell ? (
								<div
									key={cell.id}
									className="flex items-center justify-center"
								>
									<ImageWithTooltip
										src={cell.src}
										name={cell.name}
										substackUrl={cell.substackUrl}
										skystackUrl={cell.skystackUrl}
										height={MOBILE_ITEM_HEIGHT}
										width={MOBILE_ITEM_WIDTH}
									/>
								</div>
							) : (
								<div
									key={`empty-${rowIndex}-${colIndex}`}
									style={{
										width: MOBILE_ITEM_WIDTH,
										height: MOBILE_ITEM_HEIGHT,
									}}
								></div>
							)
						)
					)}
				</div>
			</div>
		</>
	);
}
