import argparse
import os
import sys
from pdf_preview.core import generate_preview, PDFValidationError


def parse_args():
    parser = argparse.ArgumentParser(description="Generate an animated preview (GIF/MP4) from a PDF.")
    parser.add_argument("input_file", help="Path to the input PDF file.")
    parser.add_argument("--output", default=None, help="Base name for output file(s) (without extension). Default is input filename in current directory.")
    parser.add_argument("--max-duration", type=float, default=10.0, help="Maximum duration in seconds (default: 10).")
    parser.add_argument("--format", choices=["gif", "mp4", "all"], default="gif", help='Output format (default: "gif").')
    parser.add_argument("--dimensions", default="480x640", help='Dimensions as "WIDTHxHEIGHT" (default: "480x640").')
    return parser.parse_args()


def main():
    args = parse_args()
    pdf_path = args.input_file

    if args.output:
        output_basename = args.output
        if output_basename.lower().endswith((".gif", ".mp4")):
            output_basename = os.path.splitext(output_basename)[0]
    else:
        base = os.path.splitext(os.path.basename(pdf_path))[0]
        output_basename = os.path.join(os.getcwd(), base + "_preview")

    try:
        outputs = generate_preview(
            pdf_path=pdf_path,
            output_basename=output_basename,
            max_duration=args.max_duration,
            format=args.format,
            dimensions=args.dimensions,
        )
        print("Success! Generated file(s):")
        for p in outputs:
            print(f" - {p}")
        return 0
    except PDFValidationError as e:
        print(f"Validation error: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())