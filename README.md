# 🧱 LEGO Mosaic Maker

Convert any image into a beautiful LEGO mosaic with realistic color matching and detailed building instructions!

- [🧱 LEGO Mosaic Maker](#-lego-mosaic-maker)
  - [✨ Features](#-features)
  - [🚀 Quick Start](#-quick-start)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Basic Usage](#basic-usage)
  - [📖 Detailed Usage](#-detailed-usage)
    - [Command Line Options](#command-line-options)
    - [Examples](#examples)
  - [📁 Output Files](#-output-files)
    - [Sample Color Report](#sample-color-report)
  - [🔧 Advanced Configuration](#-advanced-configuration)
    - [Updating LEGO Parts Database](#updating-lego-parts-database)
    - [Color Selection Criteria](#color-selection-criteria)
    - [Performance Optimization](#performance-optimization)
  - [🎨 Tips for Best Results](#-tips-for-best-results)
    - [Image Selection](#image-selection)
    - [Size Recommendations](#size-recommendations)
    - [Building Tips](#building-tips)
  - [🛠️ Technical Details](#️-technical-details)
    - [Dependencies](#dependencies)
    - [Algorithm Overview](#algorithm-overview)
    - [Color Accuracy](#color-accuracy)
  - [⚠️ Disclaimer](#️-disclaimer)
  - [📄 License](#-license)
  - [🤝 Contributing](#-contributing)
    - [Pull Request Process](#pull-request-process)
    - [Automatic Code Formatting](#automatic-code-formatting)
  - [📞 Support](#-support)
  - [🙏 Acknowledgments](#-acknowledgments)

## ✨ Features

- **Precise Color Matching**: Uses CIEDE2000 color difference formula for accurate color conversion
- **Realistic LEGO Colors**: Only uses colors from parts that are:
  - Released in the last 10 years
  - Currently available (not retired/discontinued)
  - 1x1 flat tiles or plates
- **Multiple Output Formats**:
  - Small mosaic (actual LEGO dimensions)
  - Large mosaic (scaled to original image size)
  - Detailed color usage report with part counts
- **Optimized Performance**: Multi-core processing for fast conversion
- **Flexible Sizing**: Specify either width or height in LEGO pieces

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Required packages (install via `pip install -r requirements.txt`)

### Installation

1. Clone this repository:

```bash
git clone https://github.com/your-username/lego-mosaic-maker.git
cd lego-mosaic-maker
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Download LEGO parts database:

```bash
python update_lego_parts_data.py
```

### Basic Usage

```bash
# Create a 48-piece wide mosaic
python foto_to_lego_mosaic.py your_image.jpg --width 48

# Create a 32-piece tall mosaic
python foto_to_lego_mosaic.py your_image.png --height 32
```

## 📖 Detailed Usage

### Command Line Options

```
usage: foto_to_lego_mosaic.py [-h] (--width WIDTH | --height HEIGHT) [--output OUTPUT] image

positional arguments:
  image                 Path to the input image

optional arguments:
  -h, --help            show this help message and exit
  --width WIDTH, -w WIDTH
                        Width of the mosaic in LEGO pieces
  --height HEIGHT       Height of the mosaic in LEGO pieces
  --output OUTPUT, -o OUTPUT
                        Output directory (default: output)
```

### Examples

```bash
# Basic usage with width specification
python foto_to_lego_mosaic.py photo.jpg --width 48

# Specify height instead of width
python foto_to_lego_mosaic.py landscape.png --height 32

# Custom output directory
python foto_to_lego_mosaic.py portrait.jpg --width 64 --output my_mosaics
```

## 📁 Output Files

For each processed image, the tool generates:

1. **`[filename]_mosaic_[width]x[height]_[timestamp].png`**

   - Small mosaic at actual LEGO piece resolution
   - Perfect for viewing pixel-by-pixel instructions

2. **`[filename]_mosaic_large_[width]x[height]_[timestamp].png`**

   - Large mosaic scaled to original image dimensions
   - Better for viewing on devices without zoom capability

3. **`[filename]_color_report_[timestamp].txt`**
   - Detailed breakdown of required LEGO pieces
   - Lists each color with exact piece counts
   - Perfect for shopping list creation

### Sample Color Report

```
LEGO Mosaic Color Usage Report
Image: /path/to/your/photo.jpg
Mosaic size: 96x130 pieces
Total pieces: 12480
Unique colors: 8

White (#FFFFFF): 3207 pieces
Glow in Dark White (#D9D9D9): 2782 pieces
Light Bluish Gray (#A0A5A9): 1835 pieces
Pearl Titanium (#3E3C39): 1457 pieces
Black (#05131D): 921 pieces
Dark Bluish Gray (#6C6E68): 913 pieces
Flat Silver (#898788): 743 pieces
Light Aqua (#ADC3C0): 622 pieces
```

## 🔧 Advanced Configuration

### Updating LEGO Parts Database

The tool uses data from [Rebrickable](https://rebrickable.com/downloads/) to ensure accurate color information. Update the database periodically:

```bash
python update_lego_parts_data.py
```

This script:

1. Downloads the latest LEGO parts data from Rebrickable
2. Extracts and processes the CSV files
3. Stores them in the `data/` directory

### Color Selection Criteria

The tool filters LEGO colors based on:

- **Availability**: Only colors used in 1x1 tiles or plates
- **Recency**: Parts released in the last 10 years
- **Status**: Currently available (not discontinued)
- **Transparency**: Excludes transparent pieces

### Performance Optimization

- **Multi-core Processing**: Automatically uses all available CPU cores
- **Color Quantization**: Reduces similar colors to speed up processing
- **Caching**: Reuses color calculations for identical pixels

## 🎨 Tips for Best Results

### Image Selection

- **High Contrast**: Images with clear contrasts work best
- **Simple Subjects**: Portraits, logos, and simple scenes are ideal
- **Avoid Gradients**: Sharp color transitions look better than smooth gradients

### Size Recommendations

- **Small Mosaics (16-32 pieces)**: Good for simple images, logos
- **Medium Mosaics (48-64 pieces)**: Best balance of detail and buildability
- **Large Mosaics (96+ pieces)**: For complex images, requires many pieces

### Building Tips

- Use the small mosaic image for pixel-perfect reference
- Build row by row for easier assembly
- Consider framing options for display

## 🛠️ Technical Details

### Dependencies

- **Pillow (PIL)**: Image processing and manipulation
- **NumPy**: Efficient array operations
- **Pandas**: Data processing and filtering
- **colorspacious**: CIEDE2000 color difference calculations
- **requests**: Downloading LEGO parts data
- **beautifulsoup4**: Web scraping for data updates

### Algorithm Overview

1. **Image Preprocessing**: Resize and quantize colors
2. **Color Analysis**: Extract unique colors from quantized image
3. **LEGO Matching**: Find closest LEGO colors using CIEDE2000
4. **Mosaic Generation**: Apply color mapping to create final mosaic
5. **Output Creation**: Generate images and usage reports

### Color Accuracy

Uses the CIEDE2000 color difference formula, which closely matches human color perception, ensuring the most visually accurate color matching possible.

## ⚠️ Disclaimer

This project is **not affiliated with, endorsed by, or sponsored by The LEGO Group**.

- LEGO® is a trademark of The LEGO Group
- This is an unofficial, fan-created tool for educational and personal use
- The LEGO Group does not sponsor, authorize, or endorse this project
- All trademarks and copyrights belong to their respective owners
- This tool is provided "as is" without warranty of any kind

For official LEGO products and services, please visit [lego.com](https://www.lego.com).

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Code Style**: All code must pass PEP8 compliance checks
2. **Formatting**: Use `black` and `isort` for code formatting
3. **Testing**: Ensure your changes don't break existing functionality
4. **Documentation**: Update README if adding new features

### Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following code quality standards
4. Run quality checks locally: `black . && isort . && flake8 .`
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Automatic Code Formatting

If your PR doesn't pass formatting checks, collaborators can comment `/format` on the PR to automatically format the code.

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/your-username/lego-mosaic-maker/issues) page
2. Create a new issue with detailed information about your problem
3. Include your Python version, operating system, and example command

## 🙏 Acknowledgments

- [Rebrickable](https://rebrickable.com/) for providing comprehensive LEGO parts database
- The LEGO Group for creating the amazing building system that inspired this project
- The open-source community for the excellent libraries that make this tool possible

---

_Happy building! 🧱_
