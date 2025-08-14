#!/packages/apps/mamba/1.5.8/bin/python

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
            elif line.startswith("indexed_by"):
                indexed_by = line.split("=", 1)[1].strip()
                
               # print(image_filename, event, indexed_by)
                # If "indexed by" is not None, write to the output file
                if indexed_by and indexed_by.lower() != "none":
                    if image_filename and event:
                        output.write(f"{image_filename}, {event}\n")
    
    print(f"Filtered data written to {output_file}")

# Replace 'input.txt' with your file path and 'output.txt' for the output
extract_image_event('p21-t2-all.stream', 'indexable_hits.list')

