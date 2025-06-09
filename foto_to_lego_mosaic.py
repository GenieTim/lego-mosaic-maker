#!/usr/bin/env python
"""
CLI application that converts a photo to a LEGO mosaic.
As arguments, it takes a path to a photo and either a width or a height,
which shall be the number of LEGO parts in the mosaic in that dimension.

The image is appropriately resized, and the colors of the pixels are converted to LEGO colors.
It uses the stored data in the `data` directory to find the colors that are closest to the colors in the photo.
It only uses colors of parts, that
1. have been released in the last 10 years,
2. are not retired or discontinued,
3. are 1x1 flat tiles or plates

To find the closest colors, it uses the CIEDE2000 color difference formula.
It then generates a mosaic image and saves it to the `output` directory.
The image is saved as well in the original dimensions, scaled up again to the original size of the photo,
as this makes it easier to see the image on other devices where zooming is not possible.
"""

import argparse
import multiprocessing
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
from functools import lru_cache
from pathlib import Path

import colorspacious
import numpy as np
import pandas as pd
from PIL import Image

# Global variable for multiprocessing
_lego_colors_global = None


def init_worker(lego_colors):
    """Initialize worker process with LEGO colors data."""
    global _lego_colors_global
    _lego_colors_global = lego_colors


def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_lab(rgb):
    """Convert RGB to LAB color space for CIEDE2000 calculation."""
    # Normalize RGB to 0-1 range
    rgb_normalized = np.array(rgb) / 255.0
    return colorspacious.cspace_convert(rgb_normalized, "sRGB1", "CIELab")


def calculate_ciede2000_distance(lab1, lab2):
    """Calculate CIEDE2000 color difference between two LAB colors."""
    return colorspacious.deltaE(lab1, lab2, input_space="CIELab")


def load_lego_colors():
    """Load and filter LEGO colors based on the criteria."""
    print("Loading LEGO color data...")

    # Load color data
    colors_df = pd.read_csv("data/colors.csv")
    parts_df = pd.read_csv("data/parts.csv")
    part_categories_df = pd.read_csv("data/part_categories.csv")

    # Filter for tiles and plates categories (14=Plates, 19=Tiles)
    tile_plate_categories = [14, 19]

    # Load inventory parts (this is a large file, so we'll read it in chunks)
    print("Processing inventory parts data...")

    # Get parts that are tiles or plates
    tile_plate_parts = parts_df[parts_df["part_cat_id"].isin(tile_plate_categories)]

    # Read inventory_parts in chunks to handle large file
    chunk_list = []
    chunk_size = 10000

    try:
        for chunk in pd.read_csv("data/inventory_parts.csv", chunksize=chunk_size):
            # Filter for tile/plate parts only
            filtered_chunk = chunk[chunk["part_num"].isin(tile_plate_parts["part_num"])]
            if not filtered_chunk.empty:
                chunk_list.append(filtered_chunk)
    except Exception as e:
        print(f"Error reading inventory_parts.csv: {e}")
        return {}

    if not chunk_list:
        print("No suitable parts found!")
        return {}

    inventory_parts_df = pd.concat(chunk_list, ignore_index=True)

    # Get unique colors from inventory parts
    used_colors = inventory_parts_df["color_id"].unique()

    # Filter colors based on criteria
    current_year = datetime.now().year
    valid_colors = colors_df[
        (colors_df["id"].isin(used_colors))  # Color is used in tiles/plates
        & (colors_df["y2"] >= current_year - 10)  # Released in last 10 years
        & (colors_df["y2"] >= current_year - 1)  # Not retired (still produced recently)
        & (~colors_df["is_trans"])  # Not transparent
    ]

    print(f"Found {len(valid_colors)} suitable LEGO colors")

    # Convert to dictionary with LAB colors for efficient lookup
    lego_colors = {}
    for _, color in valid_colors.iterrows():
        rgb = hex_to_rgb(color["rgb"])
        lab = rgb_to_lab(rgb)
        lego_colors[color["id"]] = {
            "name": color["name"],
            "rgb": rgb,
            "lab": lab,
            "hex": color["rgb"],
        }

    return lego_colors


def find_closest_lego_color(pixel_rgb, lego_colors):
    """Find the closest LEGO color to a given RGB pixel using CIEDE2000."""
    pixel_lab = rgb_to_lab(pixel_rgb)

    min_distance = float("inf")
    closest_color = None

    for color_id, color_data in lego_colors.items():
        distance = calculate_ciede2000_distance(pixel_lab, color_data["lab"])
        if distance < min_distance:
            min_distance = distance
            closest_color = color_data

    return closest_color


@lru_cache(maxsize=1024)
def find_closest_lego_color_cached(pixel_rgb):
    """Cached version of find_closest_lego_color for repeated colors."""
    return find_closest_lego_color(pixel_rgb, _lego_colors_global)


def process_color_batch(unique_colors_batch):
    """Process a batch of unique colors in a worker process."""
    results = {}
    for color_rgb in unique_colors_batch:
        closest_color = find_closest_lego_color(color_rgb, _lego_colors_global)
        results[color_rgb] = closest_color["rgb"]
    return results


def resize_image(image, target_width=None, target_height=None):
    """Resize image while maintaining aspect ratio."""
    original_width, original_height = image.size

    if target_width and target_height:
        raise ValueError("Cannot specify both width and height")

    if target_width:
        aspect_ratio = original_height / original_width
        new_height = int(target_width * aspect_ratio)
        return image.resize((target_width, new_height), Image.Resampling.LANCZOS)

    elif target_height:
        aspect_ratio = original_width / original_height
        new_width = int(target_height * aspect_ratio)
        return image.resize((new_width, target_height), Image.Resampling.LANCZOS)

    else:
        raise ValueError("Must specify either width or height")


def quantize_image(image, max_colors=256):
    """Reduce the number of colors in the image using PIL's quantization."""
    print(f"Quantizing image to max {max_colors} colors...")

    # Convert to P mode (palette mode) to reduce colors
    quantized = image.quantize(colors=max_colors, method=Image.Quantize.MEDIANCUT)
    # Convert back to RGB
    return quantized.convert("RGB")


def create_mosaic(
    image_path, output_dir, lego_colors, target_width=None, target_height=None
):
    """Create LEGO mosaic from input image."""
    print(f"Processing image: {image_path}")

    # Load and resize image
    try:
        image = Image.open(image_path).convert("RGB")
        original_size = image.size
        print(f"Original image size: {original_size[0]}x{original_size[1]}")
    except Exception as e:
        print(f"Error loading image: {e}")
        return

    # Resize image to target dimensions
    resized_image = resize_image(image, target_width, target_height)
    mosaic_width, mosaic_height = resized_image.size
    print(f"Mosaic dimensions: {mosaic_width}x{mosaic_height} LEGO pieces")

    # Quantize colors to reduce computation
    quantized_image = quantize_image(resized_image, max_colors=256)
    mosaic_array = np.array(quantized_image)

    # Find all unique colors in the quantized image
    print("Finding unique colors...")
    unique_colors = set()
    for y in range(mosaic_height):
        for x in range(mosaic_width):
            unique_colors.add(tuple(mosaic_array[y, x]))

    unique_colors = list(unique_colors)
    print(f"Found {len(unique_colors)} unique colors after quantization")

    # Process unique colors in parallel batches
    print("Converting unique colors to LEGO colors...")
    color_mapping = {}

    # Determine number of processes
    num_processes = min(multiprocessing.cpu_count(), len(unique_colors))
    batch_size = max(
        1, len(unique_colors) // (num_processes * 4)
    )  # Create more batches than processes

    # Split unique colors into batches
    color_batches = [
        unique_colors[i : i + batch_size]
        for i in range(0, len(unique_colors), batch_size)
    ]

    # Process batches in parallel
    with ProcessPoolExecutor(
        max_workers=num_processes, initializer=init_worker, initargs=(lego_colors,)
    ) as executor:
        future_to_batch = {
            executor.submit(process_color_batch, batch): batch
            for batch in color_batches
        }

        completed_batches = 0
        for future in as_completed(future_to_batch):
            batch_results = future.result()
            color_mapping.update(batch_results)
            completed_batches += 1
            progress = (completed_batches / len(color_batches)) * 100
            print(f"Color conversion progress: {progress:.1f}%", end="\r")

    print(f"\nColor mapping created for {len(color_mapping)} unique colors")

    # Apply color mapping to create mosaic
    print("Applying color mapping to create mosaic...")
    lego_mosaic = np.zeros_like(mosaic_array)

    # Vectorized approach using the color mapping
    total_pixels = mosaic_width * mosaic_height
    processed_pixels = 0

    for y in range(mosaic_height):
        for x in range(mosaic_width):
            pixel_rgb = tuple(mosaic_array[y, x])
            lego_mosaic[y, x] = color_mapping[pixel_rgb]

            processed_pixels += 1
            if (
                processed_pixels % 1000 == 0
            ):  # Update less frequently since it's faster now
                progress = (processed_pixels / total_pixels) * 100
                print(f"Mosaic creation progress: {progress:.1f}%", end="\r")

    print("\nCreating output images...")

    # Create mosaic image
    mosaic_image = Image.fromarray(lego_mosaic.astype(np.uint8))

    # Generate output filename
    input_filename = Path(image_path).stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save small mosaic (actual LEGO dimensions)
    small_output_path = os.path.join(
        output_dir,
        f"{input_filename}_mosaic_{mosaic_width}x{mosaic_height}_{timestamp}.png",
    )
    mosaic_image.save(small_output_path)
    print(f"Saved mosaic: {small_output_path}")

    # Save large mosaic (scaled up to original dimensions)
    large_mosaic = mosaic_image.resize(original_size, Image.Resampling.NEAREST)
    large_output_path = os.path.join(
        output_dir,
        f"{input_filename}_mosaic_large_{mosaic_width}x{mosaic_height}_{timestamp}.png",
    )
    large_mosaic.save(large_output_path)
    print(f"Saved large mosaic: {large_output_path}")

    # Generate color usage report
    print("\nGenerating color usage report...")
    unique_colors = {}
    for y in range(mosaic_height):
        for x in range(mosaic_width):
            color_rgb = tuple(lego_mosaic[y, x])
            if color_rgb in unique_colors:
                unique_colors[color_rgb] += 1
            else:
                unique_colors[color_rgb] = 1

    # Find color names
    color_report = []
    for rgb, count in unique_colors.items():
        for color_data in lego_colors.values():
            if color_data["rgb"] == rgb:
                color_report.append(
                    {
                        "name": color_data["name"],
                        "hex": color_data["hex"],
                        "count": count,
                    }
                )
                break

    # Sort by usage
    color_report.sort(key=lambda x: x["count"], reverse=True)

    # Save color report
    report_path = os.path.join(
        output_dir, f"{input_filename}_color_report_{timestamp}.txt"
    )
    with open(report_path, "w") as f:
        f.write(f"LEGO Mosaic Color Usage Report\n")
        f.write(f"Image: {image_path}\n")
        f.write(f"Mosaic size: {mosaic_width}x{mosaic_height} pieces\n")
        f.write(f"Total pieces: {sum(item['count'] for item in color_report)}\n")
        f.write(f"Unique colors: {len(color_report)}\n\n")

        for item in color_report:
            f.write(f"{item['name']} (#{item['hex']}): {item['count']} pieces\n")

    print(f"Saved color report: {report_path}")
    print(f"Used {len(color_report)} different LEGO colors")


def main():
    description = __doc__.strip()
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python foto_to_lego_mosaic.py photo.jpg --width 48
  python foto_to_lego_mosaic.py photo.png --height 32
        """,
    )

    parser.add_argument("image", help="Path to the input image")

    size_group = parser.add_mutually_exclusive_group(required=True)
    size_group.add_argument(
        "--width", "-w", type=int, help="Width of the mosaic in LEGO pieces"
    )
    size_group.add_argument(
        "--height", type=int, help="Height of the mosaic in LEGO pieces"
    )

    parser.add_argument(
        "--output", "-o", default="output", help="Output directory (default: output)"
    )

    args = parser.parse_args()

    # Validate input image
    if not os.path.exists(args.image):
        print(f"Error: Image file '{args.image}' not found")
        sys.exit(1)

    # Create output directory
    os.makedirs(args.output, exist_ok=True)

    # Change to script directory to find data files
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Check if data directory exists
    if not os.path.exists("data"):
        print(
            "Error: 'data' directory not found. Please ensure you have the LEGO parts database."
        )
        sys.exit(1)

    try:
        # Load LEGO colors
        lego_colors = load_lego_colors()

        if not lego_colors:
            print("Error: No suitable LEGO colors found. Please check your data files.")
            sys.exit(1)

        # Create mosaic
        create_mosaic(
            args.image,
            args.output,
            lego_colors,
            target_width=args.width,
            target_height=args.height,
        )

        print("\nMosaic creation completed successfully!")

    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
