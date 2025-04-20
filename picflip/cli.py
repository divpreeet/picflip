import argparse
import os
import io
import logging
import warnings
from rembg import remove
from PIL import Image
from colorama import init, Fore, Style

warnings.filterwarnings("ignore", message=".*context leak detected.*")
logging.getLogger("onnxruntime").setLevel(logging.ERROR)
init(autoreset=True)  

ASCII_ART = f"""{Fore.CYAN}

           /$$            /$$$$$$  /$$ /$$          
          |__/           /$$__  $$| $$|__/          
  /$$$$$$  /$$  /$$$$$$$| $$  \__/| $$ /$$  /$$$$$$ 
 /$$__  $$| $$ /$$_____/| $$$$    | $$| $$ /$$__  $$
| $$  \ $$| $$| $$      | $$_/    | $$| $$| $$  \ $$
| $$  | $$| $$| $$      | $$      | $$| $$| $$  | $$
| $$$$$$$/| $$|  $$$$$$$| $$      | $$| $$| $$$$$$$/
| $$____/ |__/ \_______/|__/      |__/|__/| $$____/ 
| $$                                      | $$      
| $$                                      | $$      
|__/                                      |__/      

{Style.RESET_ALL}
"""

def print_banner():
    print(ASCII_ART)
    print(f"{Fore.YELLOW}this is picflip! remove backgrounds and convert images!{Style.RESET_ALL}")

def remove_background(input_path, output_path):
    try:
        with open(input_path, 'rb') as f:
            input_data = f.read()
        output_data = remove(input_data)
        image = Image.open(io.BytesIO(output_data))
        image.save(output_path)
        print(f"{Fore.GREEN}✓ Background removed! It's at {output_path}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}✘ Couldn't remove background: {e}{Style.RESET_ALL}")

def convert_image(input_path, output_path, output_format):
    supported_formats = {'png', 'jpg', 'jpeg', 'webp'}
    output_format = output_format.lower()
    
    if output_format not in supported_formats:
        print(f"{Fore.RED}✘ Unsupported output format. Supported formats are: {', '.join(supported_formats)}{Style.RESET_ALL}")
        return

    ext = os.path.splitext(input_path)[1].lower()
    try:
        if ext == '.svg':
            try:
                import cairosvg
            except ImportError:
                print(f"{Fore.RED}cairosvg is not installed! Install it with: pip install cairosvg{Style.RESET_ALL}")
                return
            cairosvg.svg2png(url=input_path, write_to=output_path)
            print(f"{Fore.GREEN}✓ Converted SVG to PNG: {output_path}{Style.RESET_ALL}")
        else:
            with Image.open(input_path) as img:
                if output_format in ['jpg', 'jpeg'] and img.mode == 'RGBA':
                    img = img.convert('RGB')
                img.save(output_path, output_format.upper())
            print(f"{Fore.GREEN}✓ Converted {ext[1:].upper()} to {output_format.upper()}: {output_path}{Style.RESET_ALL}")
    except FileNotFoundError:
        print(f"{Fore.RED}✘ Input file not found: {input_path}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}✘ Error converting image: {e}{Style.RESET_ALL}")

def usage():
    print_banner()
    print(f"{Fore.MAGENTA}Usage:{Style.RESET_ALL}")
    print(f"  python cli.py {Fore.YELLOW}remove{Style.RESET_ALL} <input_image> <output_image>")
    print(f"  python cli.py {Fore.YELLOW}convert{Style.RESET_ALL} <input_image> <output_image> <output_format>")
    print(f"{Fore.MAGENTA}Examples:{Style.RESET_ALL}")
    print(f"  python cli.py convert shrek.webp shrek.jpg jpg")
    print(f"  python cli.py remove selfie.png selfie_nobg.png")

def main():
    print_banner()
    parser = argparse.ArgumentParser(
        description="picflip - A simple tool to remove backgrounds and convert images!",
        epilog=f"""{Fore.CYAN}
Examples:
  Remove background:    python cli.py remove input.jpg output.png
  Convert image:        python cli.py convert input.jpg output.png png
  Convert formats:      python cli.py convert photo.webp photo.jpg jpg
  Convert SVG:          python cli.py convert icon.svg icon.png png
{Style.RESET_ALL}
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    parser_remove = subparsers.add_parser("remove", 
        help="Remove the background from an image",
        description="Remove the background from any image and save it as PNG (recommended) or other formats"
    )
    parser_remove.add_argument("input", help="Path to the input image (supports jpg, png, webp)")
    parser_remove.add_argument("output", help="Path for the output image (PNG recommended for transparency)")
    
    parser_convert = subparsers.add_parser("convert",
        help="Convert images between formats",
        description="Convert images between different formats (PNG, JPG, JPEG, WEBP, SVG)"
    )
    parser_convert.add_argument("input", help="Path to the input image")
    parser_convert.add_argument("output", help="Path for the output image")
    parser_convert.add_argument("format", help="Output format (png, jpg, jpeg, webp)")
    
    args = parser.parse_args()
    if args.command == "remove":
        remove_background(args.input, args.output)
    elif args.command == "convert":
        convert_image(args.input, args.output, args.format)
    elif args.command == "usage":
        usage()

if __name__ == "__main__":
    main()
