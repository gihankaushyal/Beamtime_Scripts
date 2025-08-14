#!/usr/bin/env python3

# Read and process the text file
def extract_image_event(file_path, output_file):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    with open(output_file, 'w') as output:
        image_filename = None
        event = None
        indexed_by = None
        
        for line in lines:
            #print(line)
            if line.startswith("Image filename:"):
                image_filename = line.split(":", 1)[1].strip()
                #print(image_filename)
            elif line.startswith("Event:"):
                event = line.split(":", 1)[1].strip()
                #print(event)
                
                if image_filename and event:
                    output.write(f"{image_filename} {event}\n")
    
    print(f"Filtered data written to {output_file}")

# Replace 'input.txt' with your file path and 'output.txt' for the output
extract_image_event('E5-all.stream', 'indexable_hits.list')

