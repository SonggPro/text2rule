print("Script is starting...")
import json
import os

def get_processed_ids_from_file(filepath):
    """Reads a JSONL file and returns a set of (Calculator ID, Note ID) tuples."""
    processed_ids = set()
    if not os.path.exists(filepath):
        print(f"Error: File not found - {filepath}")
        return processed_ids
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            try:
                data = json.loads(line)
                calc_id = data.get("Calculator ID")
                note_id = data.get("Note ID")
                if calc_id is not None and note_id is not None:
                    processed_ids.add((str(calc_id), str(note_id)))
                else:
                    print(f"Warning: Line {i+1} in {filepath} is missing 'Calculator ID' or 'Note ID'.")
            except json.JSONDecodeError:
                print(f"Warning: Skipping malformed JSON line {i+1} in {filepath}: {line.strip()}")
    return processed_ids

if __name__ == "__main__":
    base_path = "outputs" # Assuming the script is run from the 'evaluation' directory
    
    file1_name = "OpenAI_qwen2.5-72b-instruct_one_shot.jsonl"
    file2_name = "OpenAI_qwen2.5-72b-instruct_direct_answer.jsonl"
    
    file1_path = os.path.join(base_path, file1_name)
    file2_path = os.path.join(base_path, file2_name)

    print(f"Comparing:\n1: {file1_path}\n2: {file2_path}\n")

    ids1 = get_processed_ids_from_file(file1_path)
    print(f"\nFound {len(ids1)} unique (Calculator ID, Note ID) pairs in {file1_name}.\n")
    
    ids2 = get_processed_ids_from_file(file2_path)
    print(f"\nFound {len(ids2)} unique (Calculator ID, Note ID) pairs in {file2_name}.\n")

    only_in_file1 = ids1 - ids2
    only_in_file2 = ids2 - ids1

    if only_in_file1:
        print(f"--- Items only in {file1_name} ({len(only_in_file1)} items) ---")
        for item in sorted(list(only_in_file1)): # sorted for consistent output
            print(item)
    else:
        print(f"--- No items found only in {file1_name} ---")

    print("\n---------------------------------------------------\n")

    if only_in_file2:
        print(f"--- Items only in {file2_name} ({len(only_in_file2)} items) ---")
        for item in sorted(list(only_in_file2)): # sorted for consistent output
            print(item)
    else:
        print(f"--- No items found only in {file2_name} ---")

    if not only_in_file1 and not only_in_file2:
        if ids1 == ids2 and len(ids1) > 0 :
             print(f"\nBoth files contain the exact same {len(ids1)} (Calculator ID, Note ID) pairs.")
        elif len(ids1) == 0 and len(ids2) == 0:
             print(f"\nBoth files are effectively empty or do not contain valid ID pairs to compare.")
        else: # Should not happen if previous checks are exhaustive
             print(f"\nFiles have the same elements but sets are not equal or sizes mismatch in an unexpected way. ids1_len: {len(ids1)}, ids2_len: {len(ids2)}")


    # Optional: If you want to see the common items
    # common_items = ids1.intersection(ids2)
    # print(f"\n--- Common items in both files ({len(common_items)} items) ---")
    # for item in sorted(list(common_items)):
    #     print(item)