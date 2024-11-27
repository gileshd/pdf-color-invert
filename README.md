# Invert PDF Colours

A simple python script to invert the colours of a PDF file.

## Installation

Install python requirements with:
```
pip install -r requirements.txt
```

You will also need to install `poppler-utils` for the `pdftoppm` command:
- Windows: Download and install from poppler releases
- Mac: `brew install poppler`
- Linux: `sudo apt-get install poppler-utils`

## Usage

Call as script - `python invert-pdf-img.py`.

See help, `python invert-pdf-img.py -h`, for more information:
```
usage: invert-pdf-img.py [-h] [-o OUTPUT] [-p PAGES] [-i INTENSITY]
                         [-t TEXT_DARKNESS]
                         input_pdf

Convert specified pages of a PDF from dark text on light background to light
text on dark background.

positional arguments:
  input_pdf             Path to the input PDF file

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Path for the output PDF file (default:
                        input_inverted.pdf)
  -p PAGES, --pages PAGES
                        Range of pages to invert (e.g., "1-3,5,7-9"). If not
                        specified, all pages will be inverted.
  -i INTENSITY, --intensity INTENSITY
                        Inversion intensity (0.0 to 1.0, default: 1.0)
  -t TEXT_DARKNESS, --text-darkness TEXT_DARKNESS
                        Text darkness level (0.0 to 1.0, default: 0.8). Lower
                        values make text darker.
```
