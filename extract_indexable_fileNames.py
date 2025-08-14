#!/usr/bin/env python3
import argparse

# Parseing args
def parse_args():
    p = argparse.ArgumentParser(description="Getting files to process")
    p.add_argument("-i", "--input", required=True, help="Input stream file path or '-' for stdin")
    p.add_argument("-o", "--output", required=True,help="Output text file path or '-' for stdout")
    p.add_argument("--delimiter", default=" ", help="Separator between filename and event in the output (default: space)." )
    return p.parse_args()

def open_in(path: str):
    return sys.stdin if path == "-" else open(path, "rt", encoding="utf-8", newline="")

def open_out(path: str):
    return sys.stdout if path == "-" else open(path, "wt", encoding="utf-8", newline="")

# Read and process the text file
def extract_image_event(infile_file, output_file, delimiter: str = " ") -> None:
    """
    Stream the input file line-by-line and write:
        <image_filename><delimiter><event>
    for each Event belonging to the current Image filename.

    Assumes the stream order is:
      Image filename: <name>
      Event: <id>
      Event: <id>
      ...
      Image filename: <next>
      ...
    """
    current_image: str | None = None
    with open_in(infile_file) as f_in, open_out(output_file) as f_out:
        
        for raw in f_in:
            line = raw.strip()
            
            if not line:
                continue
                
            if line.startswith("Image filename:"):
                current_image = line.split(":", 1)[1].strip()
                #print(image_filename)
            elif line.startswith("Event:"):
                if current_image is None:
                    continue
                event = line.split(":", 1)[1].strip()
                #print(event)
                f_out.write(f"{current_image}{delimiter}{event}\n")
    
    print(f"Filtered data written to {output_file}")

def main():
    args = parse_args()
    infile  = args.input
    outfile = args.output
    delimiter = args.delimiter
    # Replace 'input.txt' with your file path and 'output.txt' for the output
    extract_image_event(infile, outfile, delimiter = delimiter)
    

if __name__ == "__main__":
    main()
    


