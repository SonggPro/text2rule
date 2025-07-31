import json
import os

ids_to_remove_calculators = {"49", "68", "69"}
input_filename = "outputs/OpenAI_qwen2.5-72b-instruct_one_shot.jsonl"
output_filename = "outputs/OpenAI_qwen2.5-72b-instruct_one_shot.jsonl.filtered" # Write to a new file first

lines_kept = 0
lines_removed = 0

with open(input_filename, 'r', encoding='utf-8') as infile, \
        open(output_filename, 'w', encoding='utf-8') as outfile:
    for line in infile:
        try:
            data = json.loads(line)
            calc_id = data.get("Calculator ID")
            if str(calc_id) in ids_to_remove_calculators:
                lines_removed += 1
                continue # Skip this line
            outfile.write(line)
            lines_kept += 1
        except json.JSONDecodeError:
            print(f"Warning: Malformed JSON line, writing as is: {line.strip()}")
            outfile.write(line) # Keep malformed lines if any, or decide to skip
            lines_kept +=1


print(f"Filtering complete.")
print(f"Lines kept: {lines_kept}")
print(f"Lines removed (Calculator IDs {', '.join(ids_to_remove_calculators)}): {lines_removed}")
print(f"Filtered content written to: {output_filename}")
print(f"Please verify '{output_filename}' and then, if correct, replace the original file:")
print(f"mv {output_filename} {input_filename}")