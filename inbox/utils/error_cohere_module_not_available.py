#!/usr/bin/env python3
"""
Fix script for the CLI's Process Images functionality
"""
import re

# Read the file
with open('cli.py', 'r') as file:
    content = file.read()

# Find the problematic section
pattern = r'(elif action_name == " • Process Images":\s+)result = action_fn\(session_root\[\d+\], recursive=action_args\[\d+\], provider=session_provider\[\d+\], log_callback=log_callback\)\s+console\.print\(f"\[bright_green\]Processed images in \{session_root\[\d+\]\}\[/bright_green\]"\)'

replacement = r'''\1# Prompt for options interactively
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
                                
                                if result.get('success', False):
                                    console.print(f"[bold bright_green]✅ Image processing completed successfully![/bold bright_green]")
                                    console.print(f"[bright_green]Processed {result.get('files_processed', 0)} images.[/bright_green]")
                                    console.print(f"[bright_green]Output directory: {result.get('output_dir', 'Unknown')}[/bright_green]")
                                else:
                                    console.print(f"[bold yellow]⚠️ Image processing completed with issues: {result.get('error', 'Unknown error')}[/bold yellow]")
                            except Exception as e:
                                console.print(f"[bold bright_red]❌ Error processing images: {e}[/bold bright_red]")'''

# Replace the section
modified_content = re.sub(pattern, replacement, content)

# Write the modified content back to the file
with open('cli.py', 'w') as file:
    file.write(modified_content)

print("File updated successfully.") 