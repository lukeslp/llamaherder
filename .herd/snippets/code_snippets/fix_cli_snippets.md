# Code Snippets from storage/utils/fix_cli.py

File: `storage/utils/fix_cli.py`  
Language: Python  
Extracted: 2025-06-07 05:08:20  

## Snippet 1
Lines 3-11

```Python
Fix script for the CLI's Process Images functionality
"""
import re

# Read the file
with open('cli.py', 'r') as file:
    content = file.read()

# Find the problematic section
```

## Snippet 2
Lines 15-36

```Python
force = Prompt.ask("[bright_yellow]Force reprocessing even if .md or cache exists?[/bright_yellow] (y/n)", default="n").lower() == "y"
                            rename = Prompt.ask("[bright_yellow]Rename files based on content analysis?[/bright_yellow] (y/n)", default="n").lower() == "y"
                            override_md = Prompt.ask("[bright_yellow]Override existing markdown file check and reprocess images?[/bright_yellow] (y/n)", default="n").lower() == "y"
                            test = Prompt.ask("[bright_yellow]Check metadata before and after embedding alt text?[/bright_yellow] (y/n)", default="n").lower() == "y"
                            console.print(f"[bright_blue]Options: force={force}, rename={rename}, override_md={override_md}, test={test}[/bright_blue]")

                            # Import the correct function
                            from herd_ai.image_processor import process_directory as process_images

                            # Call with all required parameters
                            try:
                                result = process_images(
                                    directory=session_root[0],
                                    recursive=action_args[0],
                                    force=force,
                                    rename=rename,
                                    override_md=override_md,
                                    test=test,
                                    log_callback=log_callback,
                                    provider=session_provider[0]
                                )
```

## Snippet 3
Lines 46-53

```Python
# Replace the section
modified_content = re.sub(pattern, replacement, content)

# Write the modified content back to the file
with open('cli.py', 'w') as file:
    file.write(modified_content)

print("File updated successfully.")
```

