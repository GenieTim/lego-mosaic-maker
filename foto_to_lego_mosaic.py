#!/usr/bin/env python

"""
This is a CLI application that converts a photo to a LEGO mosaic.
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
