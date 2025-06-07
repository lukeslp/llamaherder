# Code Snippets from toollama/soon/tools_pending/unprocessed/dev_efile_supreme.py

File: `toollama/soon/tools_pending/unprocessed/dev_efile_supreme.py`  
Language: Python  
Extracted: 2025-06-07 05:15:57  

## Snippet 1
Lines 1-3

```Python
"""
title: Supreme File Management
author: Wes Caldwell
```

## Snippet 2
Lines 4-20

```Python
email: Musicheardworldwide@gmail.com
date: 2024-07-19
version: 1.0
license: MIT
description: Big set of file management tools.
"""
import os
import json
import shutil
import logging
import hashlib
import datetime
import zipfile
import tarfile
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
```

## Snippet 3
Lines 27-31

```Python
def create_folder(self, folder_name: str, path: str = None) -> str:
        """
        Create a new folder.
        :param folder_name: The name of the folder to create.
        :param path: The path where the folder should be created.
```

## Snippet 4
Lines 35-44

```Python
if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            logging.info(
                f"Folder '{folder_name}' created successfully at {folder_path}!"
            )
            return f"Folder '{folder_name}' created successfully!"
        else:
            logging.warning(f"Folder '{folder_name}' already exists at {folder_path}.")
            return f"Folder '{folder_name}' already exists."
```

## Snippet 5
Lines 45-49

```Python
def delete_folder(self, folder_name: str, path: str = None) -> str:
        """
        Delete a folder.
        :param folder_name: The name of the folder to delete.
        :param path: The path where the folder is located.
```

## Snippet 6
Lines 53-62

```Python
if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            logging.info(
                f"Folder '{folder_name}' deleted successfully from {folder_path}!"
            )
            return f"Folder '{folder_name}' deleted successfully!"
        else:
            logging.warning(f"Folder '{folder_name}' does not exist at {folder_path}.")
            return f"Folder '{folder_name}' does not exist."
```

## Snippet 7
Lines 63-68

```Python
def create_file(self, file_name: str, content: str = "", path: str = None) -> str:
        """
        Create a new file.
        :param file_name: The name of the file to create.
        :param content: The content to write to the file.
        :param path: The path where the file should be created.
```

## Snippet 8
Lines 71-76

```Python
file_path = os.path.join(path if path else self.base_path, file_name)
        with open(file_path, "w") as file:
            file.write(content)
        logging.info(f"File '{file_name}' created successfully at {file_path}!")
        return f"File '{file_name}' created successfully!"
```

## Snippet 9
Lines 77-81

```Python
def delete_file(self, file_name: str, path: str = None) -> str:
        """
        Delete a file.
        :param file_name: The name of the file to delete.
        :param path: The path where the file is located.
```

## Snippet 10
Lines 85-92

```Python
if os.path.exists(file_path):
            os.remove(file_path)
            logging.info(f"File '{file_name}' deleted successfully from {file_path}!")
            return f"File '{file_name}' deleted successfully!"
        else:
            logging.warning(f"File '{file_name}' does not exist at {file_path}.")
            return f"File '{file_name}' does not exist."
```

## Snippet 11
Lines 93-99

```Python
def read_file(self, file_name: str, path: str = None) -> str:
        """
        Read the content of a file.
        :param file_name: The name of the file to read.
        :param path: The path where the file is located.
        :return: The content of the file.
        """
```

## Snippet 12
Lines 101-109

```Python
if os.path.exists(file_path):
            with open(file_path, "r") as file:
                content = file.read()
            logging.info(f"File '{file_name}' read successfully from {file_path}!")
            return content
        else:
            logging.warning(f"File '{file_name}' does not exist at {file_path}.")
            return f"File '{file_name}' does not exist."
```

## Snippet 13
Lines 110-115

```Python
def write_to_file(self, file_name: str, content: str, path: str = None) -> str:
        """
        Write content to a file.
        :param file_name: The name of the file to write to.
        :param content: The content to write to the file.
        :param path: The path where the file is located.
```

## Snippet 14
Lines 118-125

```Python
file_path = os.path.join(path if path else self.base_path, file_name)
        with open(file_path, "w") as file:
            file.write(content)
        logging.info(
            f"Content written to file '{file_name}' successfully at {file_path}!"
        )
        return f"Content written to file '{file_name}' successfully!"
```

## Snippet 15
Lines 126-131

```Python
def list_files(self, path: str = None) -> str:
        """
        List all files in the specified directory.
        :param path: The path where the files should be listed.
        :return: A list of files in the specified directory.
        """
```

## Snippet 16
Lines 132-136

```Python
directory_path = path if path else self.base_path
        files = os.listdir(directory_path)
        logging.info(f"Files listed successfully from {directory_path}!")
        return "Files in the specified directory:\n" + "\n".join(files)
```

## Snippet 17
Lines 137-143

```Python
def read_json_file(self, file_name: str, path: str = None) -> dict:
        """
        Read the content of a JSON file.
        :param file_name: The name of the JSON file to read.
        :param path: The path where the JSON file is located.
        :return: The content of the JSON file as a dictionary.
        """
```

## Snippet 18
Lines 145-153

```Python
if os.path.exists(file_path):
            with open(file_path, "r") as file:
                content = json.load(file)
            logging.info(f"JSON file '{file_name}' read successfully from {file_path}!")
            return content
        else:
            logging.warning(f"JSON file '{file_name}' does not exist at {file_path}.")
            return f"JSON file '{file_name}' does not exist."
```

## Snippet 19
Lines 154-159

```Python
def write_json_file(self, file_name: str, content: dict, path: str = None) -> str:
        """
        Write content to a JSON file.
        :param file_name: The name of the JSON file to write to.
        :param content: The content to write to the JSON file as a dictionary.
        :param path: The path where the JSON file should be created.
```

## Snippet 20
Lines 162-169

```Python
file_path = os.path.join(path if path else self.base_path, file_name)
        with open(file_path, "w") as file:
            json.dump(content, file, indent=4)
        logging.info(
            f"Content written to JSON file '{file_name}' successfully at {file_path}!"
        )
        return f"Content written to JSON file '{file_name}' successfully!"
```

## Snippet 21
Lines 170-178

```Python
def copy_file(
        self, src_file: str, dest_file: str, src_path: str = None, dest_path: str = None
    ) -> str:
        """
        Copy a file from source to destination.
        :param src_file: The name of the source file.
        :param dest_file: The name of the destination file.
        :param src_path: The path where the source file is located.
        :param dest_path: The path where the destination file should be created.
```

## Snippet 22
Lines 185-192

```Python
if os.path.exists(src_file_path):
            shutil.copy2(src_file_path, dest_file_path)
            logging.info(f"File '{src_file}' copied successfully to {dest_file_path}!")
            return f"File '{src_file}' copied successfully to {dest_file}!"
        else:
            logging.warning(f"File '{src_file}' does not exist at {src_file_path}.")
            return f"File '{src_file}' does not exist."
```

## Snippet 23
Lines 193-205

```Python
def copy_folder(
        self,
        src_folder: str,
        dest_folder: str,
        src_path: str = None,
        dest_path: str = None,
    ) -> str:
        """
        Copy a folder from source to destination.
        :param src_folder: The name of the source folder.
        :param dest_folder: The name of the destination folder.
        :param src_path: The path where the source folder is located.
        :param dest_path: The path where the destination folder should be created.
```

## Snippet 24
Lines 206-208

```Python
:return: A success message if the folder is copied successfully.
        """
        src_folder_path = os.path.join(
```

## Snippet 25
Lines 214-225

```Python
if os.path.exists(src_folder_path):
            shutil.copytree(src_folder_path, dest_folder_path)
            logging.info(
                f"Folder '{src_folder}' copied successfully to {dest_folder_path}!"
            )
            return f"Folder '{src_folder}' copied successfully to {dest_folder}!"
        else:
            logging.warning(
                f"Folder '{src_folder}' does not exist at {src_folder_path}."
            )
            return f"Folder '{src_folder}' does not exist."
```

## Snippet 26
Lines 226-234

```Python
def move_file(
        self, src_file: str, dest_file: str, src_path: str = None, dest_path: str = None
    ) -> str:
        """
        Move a file from source to destination.
        :param src_file: The name of the source file.
        :param dest_file: The name of the destination file.
        :param src_path: The path where the source file is located.
        :param dest_path: The path where the destination file should be created.
```

## Snippet 27
Lines 241-248

```Python
if os.path.exists(src_file_path):
            shutil.move(src_file_path, dest_file_path)
            logging.info(f"File '{src_file}' moved successfully to {dest_file_path}!")
            return f"File '{src_file}' moved successfully to {dest_file}!"
        else:
            logging.warning(f"File '{src_file}' does not exist at {src_file_path}.")
            return f"File '{src_file}' does not exist."
```

## Snippet 28
Lines 249-261

```Python
def move_folder(
        self,
        src_folder: str,
        dest_folder: str,
        src_path: str = None,
        dest_path: str = None,
    ) -> str:
        """
        Move a folder from source to destination.
        :param src_folder: The name of the source folder.
        :param dest_folder: The name of the destination folder.
        :param src_path: The path where the source folder is located.
        :param dest_path: The path where the destination folder should be created.
```

## Snippet 29
Lines 262-264

```Python
:return: A success message if the folder is moved successfully.
        """
        src_folder_path = os.path.join(
```

## Snippet 30
Lines 270-281

```Python
if os.path.exists(src_folder_path):
            shutil.move(src_folder_path, dest_folder_path)
            logging.info(
                f"Folder '{src_folder}' moved successfully to {dest_folder_path}!"
            )
            return f"Folder '{src_folder}' moved successfully to {dest_folder}!"
        else:
            logging.warning(
                f"Folder '{src_folder}' does not exist at {src_folder_path}."
            )
            return f"Folder '{src_folder}' does not exist."
```

## Snippet 31
Lines 286-289

```Python
:return: True if the path is a file, False otherwise.
        """
        return os.path.isfile(path)
```

## Snippet 32
Lines 294-297

```Python
:return: True if the path is a directory, False otherwise.
        """
        return os.path.isdir(path)
```

## Snippet 33
Lines 298-301

```Python
def encrypt_file(self, file_name: str, key: str, path: str = None) -> str:
        """
        Encrypt a file using a key.
        :param file_name: The name of the file to encrypt.
```

## Snippet 34
Lines 307-311

```Python
if os.path.exists(file_path):
            with open(file_path, "rb") as file:
                data = file.read()
            key = hashlib.sha256(key.encode()).digest()
            encrypted_data = bytearray(
```

## Snippet 35
Lines 313-317

```Python
)
            with open(file_path, "wb") as file:
                file.write(encrypted_data)
            logging.info(f"File '{file_name}' encrypted successfully at {file_path}!")
            return f"File '{file_name}' encrypted successfully!"
```

## Snippet 36
Lines 318-321

```Python
else:
            logging.warning(f"File '{file_name}' does not exist at {file_path}.")
            return f"File '{file_name}' does not exist."
```

## Snippet 37
Lines 322-325

```Python
def decrypt_file(self, file_name: str, key: str, path: str = None) -> str:
        """
        Decrypt a file using a key.
        :param file_name: The name of the file to decrypt.
```

## Snippet 38
Lines 331-335

```Python
if os.path.exists(file_path):
            with open(file_path, "rb") as file:
                data = file.read()
            key = hashlib.sha256(key.encode()).digest()
            decrypted_data = bytearray(
```

## Snippet 39
Lines 337-341

```Python
)
            with open(file_path, "wb") as file:
                file.write(decrypted_data)
            logging.info(f"File '{file_name}' decrypted successfully at {file_path}!")
            return f"File '{file_name}' decrypted successfully!"
```

## Snippet 40
Lines 342-345

```Python
else:
            logging.warning(f"File '{file_name}' does not exist at {file_path}.")
            return f"File '{file_name}' does not exist."
```

## Snippet 41
Lines 346-352

```Python
def get_file_metadata(self, file_name: str, path: str = None) -> dict:
        """
        Get metadata of a file.
        :param file_name: The name of the file to get metadata for.
        :param path: The path where the file is located.
        :return: A dictionary containing the file's metadata.
        """
```

## Snippet 42
Lines 354-371

```Python
if os.path.exists(file_path):
            metadata = os.stat(file_path)
            return {
                "size": metadata.st_size,
                "creation_time": datetime.datetime.fromtimestamp(
                    metadata.st_ctime
                ).strftime("%Y-%m-%d %H:%M:%S"),
                "modification_time": datetime.datetime.fromtimestamp(
                    metadata.st_mtime
                ).strftime("%Y-%m-%d %H:%M:%S"),
                "access_time": datetime.datetime.fromtimestamp(
                    metadata.st_atime
                ).strftime("%Y-%m-%d %H:%M:%S"),
            }
        else:
            logging.warning(f"File '{file_name}' does not exist at {file_path}.")
            return f"File '{file_name}' does not exist."
```

## Snippet 43
Lines 372-379

```Python
def batch_rename_files(
        self, directory: str, old_pattern: str, new_pattern: str
    ) -> str:
        """
        Batch rename files in a directory.
        :param directory: The directory containing the files to rename.
        :param old_pattern: The old pattern in the file names to replace.
        :param new_pattern: The new pattern to replace the old pattern with.
```

## Snippet 44
Lines 380-382

```Python
:return: A success message if the files are renamed successfully.
        """
        directory_path = os.path.join(self.base_path, directory)
```

## Snippet 45
Lines 385-390

```Python
if old_pattern in filename:
                    new_filename = filename.replace(old_pattern, new_pattern)
                    os.rename(
                        os.path.join(directory_path, filename),
                        os.path.join(directory_path, new_filename),
                    )
```

## Snippet 46
Lines 393-398

```Python
else:
            logging.warning(
                f"Directory '{directory}' does not exist at {directory_path}."
            )
            return f"Directory '{directory}' does not exist."
```

## Snippet 47
Lines 399-411

```Python
def compress_file(
        self,
        file_name: str,
        output_filename: str,
        format: str = "zip",
        path: str = None,
    ) -> str:
        """
        Compress a file into the specified format.
        :param file_name: The name of the file to compress.
        :param output_filename: The name of the output compressed file.
        :param format: The compression format ('zip', 'tar', 'gztar').
        :param path: The path where the file is located.
```

## Snippet 48
Lines 417-419

```Python
if format == "zip":
                with zipfile.ZipFile(output_path, "w") as zipf:
                    zipf.write(file_path, os.path.basename(file_path))
```

## Snippet 49
Lines 420-422

```Python
elif format == "tar":
                with tarfile.open(output_path, "w") as tarf:
                    tarf.add(file_path, os.path.basename(file_path))
```

## Snippet 50
Lines 423-432

```Python
elif format == "gztar":
                with tarfile.open(output_path, "w:gz") as tarf:
                    tarf.add(file_path, os.path.basename(file_path))
            else:
                logging.warning(f"Unsupported compression format: {format}.")
                return f"Unsupported compression format: {format}."
            logging.info(
                f"File '{file_name}' compressed successfully to {output_path}!"
            )
            return f"File '{file_name}' compressed successfully to {output_filename}!"
```

## Snippet 51
Lines 433-436

```Python
else:
            logging.warning(f"File '{file_name}' does not exist at {file_path}.")
            return f"File '{file_name}' does not exist."
```

## Snippet 52
Lines 437-444

```Python
def decompress_file(
        self, file_name: str, output_directory: str, path: str = None
    ) -> str:
        """
        Decompress a file into the specified directory.
        :param file_name: The name of the file to decompress.
        :param output_directory: The directory where the decompressed files will be stored.
        :param path: The path where the file is located.
```

## Snippet 53
Lines 450-452

```Python
if file_name.endswith(".zip"):
                with zipfile.ZipFile(file_path, "r") as zipf:
                    zipf.extractall(output_path)
```

## Snippet 54
Lines 453-461

```Python
elif (
                file_name.endswith(".tar")
                or file_name.endswith(".tar.gz")
                or file_name.endswith(".tgz")
            ):
                with tarfile.open(file_path, "r") as tarf:
                    tarf.extractall(output_path)
            else:
                logging.warning(
```

## Snippet 55
Lines 465-470

```Python
logging.info(
                f"File '{file_name}' decompressed successfully to {output_path}!"
            )
            return (
                f"File '{file_name}' decompressed successfully to {output_directory}!"
            )
```

## Snippet 56
Lines 471-474

```Python
else:
            logging.warning(f"File '{file_name}' does not exist at {file_path}.")
            return f"File '{file_name}' does not exist."
```

## Snippet 57
Lines 475-479

```Python
def save_file_version(self, file_name: str, path: str = None) -> str:
        """
        Save a version of the file.
        :param file_name: The name of the file to save a version of.
        :param path: The path where the file is located.
```

## Snippet 58
Lines 492-495

```Python
else:
            logging.warning(f"File '{file_name}' does not exist at {file_path}.")
            return f"File '{file_name}' does not exist."
```

## Snippet 59
Lines 496-503

```Python
def restore_file_version(
        self, file_name: str, version: int, path: str = None
    ) -> str:
        """
        Restore a file to a previous version.
        :param file_name: The name of the file to restore.
        :param version: The version number to restore.
        :param path: The path where the file is located.
```

## Snippet 60
Lines 520-523

```Python
else:
            logging.warning(f"File '{file_name}' does not exist at {file_path}.")
            return f"File '{file_name}' does not exist."
```

## Snippet 61
Lines 524-532

```Python
def share_file(
        self, file_name: str, user: str, permissions: str, path: str = None
    ) -> str:
        """
        Share a file with a specific user and set permissions.
        :param file_name: The name of the file to share.
        :param user: The user to share the file with.
        :param permissions: The permissions to set (e.g., 'read', 'write').
        :param path: The path where the file is located.
```

## Snippet 62
Lines 536-545

```Python
if os.path.exists(file_path):
            # Implement sharing logic here (e.g., store sharing information in a database or file)
            logging.info(
                f"File '{file_name}' shared with user '{user}' with permissions '{permissions}'!"
            )
            return f"File '{file_name}' shared with user '{user}' with permissions '{permissions}'!"
        else:
            logging.warning(f"File '{file_name}' does not exist at {file_path}.")
            return f"File '{file_name}' does not exist."
```

## Snippet 63
Lines 550-552

```Python
:param path: The path where to search for files.
        :return: A list of file paths that match the search criteria.
        """
```

## Snippet 64
Lines 557-561

```Python
if keyword in file:
                    matching_files.append(os.path.join(root, file))
                else:
                    file_path = os.path.join(root, file)
                    with open(file_path, "r") as f:
```

## Snippet 65
Lines 569-573

```Python
def synchronize_files(self, source_path: str, destination_path: str) -> str:
        """
        Synchronize files between two directories.
        :param source_path: The source directory to synchronize from.
        :param destination_path: The destination directory to synchronize to.
```

## Snippet 66
Lines 578-583

```Python
for file in files:
                    source_file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(source_file_path, source_path)
                    destination_file_path = os.path.join(
                        destination_path, relative_path
                    )
```

## Snippet 67
Lines 584-590

```Python
if (
                        not os.path.exists(destination_file_path)
                        or os.stat(source_file_path).st_mtime
                        - os.stat(destination_file_path).st_mtime
                        > 1
                    ):
                        shutil.copy2(source_file_path, destination_file_path)
```

## Snippet 68
Lines 591-594

```Python
logging.info(
                f"Synchronization from '{source_path}' to '{destination_path}' completed successfully!"
            )
            return f"Synchronization from '{source_path}' to '{destination_path}' completed successfully!"
```

## Snippet 69
Lines 595-598

```Python
else:
            logging.warning(f"Source or destination path does not exist.")
            return f"Source or destination path does not exist."
```

## Snippet 70
Lines 599-604

```Python
def add_tag(self, file_name: str, tag: str, path: str = None) -> str:
        """
        Add a tag to a file.
        :param file_name: The name of the file to add a tag to.
        :param tag: The tag to add.
        :param path: The path where the file is located.
```

## Snippet 71
Lines 608-615

```Python
if os.path.exists(file_path):
            self.tags[file_name].append(tag)
            logging.info(f"Tag '{tag}' added to file '{file_name}'!")
            return f"Tag '{tag}' added to file '{file_name}'!"
        else:
            logging.warning(f"File '{file_name}' does not exist at {file_path}.")
            return f"File '{file_name}' does not exist."
```

## Snippet 72
Lines 618-620

```Python
Get the tags for a file.
        :param file_name: The name of the file to get tags for.
        :param path: The path where the file is located.
```

## Snippet 73
Lines 627-630

```Python
else:
            logging.warning(f"File '{file_name}' does not exist at {file_path}.")
            return f"File '{file_name}' does not exist."
```

## Snippet 74
Lines 631-636

```Python
def convert_file(self, file_name: str, output_format: str, path: str = None) -> str:
        """
        Convert a file to a different format.
        :param file_name: The name of the file to convert.
        :param output_format: The desired output format.
        :param path: The path where the file is located.
```

## Snippet 75
Lines 645-648

```Python
else:
            logging.warning(f"File '{file_name}' does not exist at {file_path}.")
            return f"File '{file_name}' does not exist."
```

## Snippet 76
Lines 649-653

```Python
def backup_files(self, source_path: str, backup_path: str) -> str:
        """
        Backup files from the source directory to the backup directory.
        :param source_path: The source directory to backup from.
        :param backup_path: The backup directory to backup to.
```

## Snippet 77
Lines 658-661

```Python
for file in files:
                    source_file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(source_file_path, source_path)
                    backup_file_path = os.path.join(backup_path, relative_path)
```

## Snippet 78
Lines 665-668

```Python
logging.info(
                f"Backup from '{source_path}' to '{backup_path}' completed successfully!"
            )
            return f"Backup from '{source_path}' to '{backup_path}' completed successfully!"
```

## Snippet 79
Lines 669-672

```Python
else:
            logging.warning(f"Source or backup path does not exist.")
            return f"Source or backup path does not exist."
```

## Snippet 80
Lines 673-677

```Python
def recover_files(self, backup_path: str, destination_path: str) -> str:
        """
        Recover files from the backup directory to the destination directory.
        :param backup_path: The backup directory to recover from.
        :param destination_path: The destination directory to recover to.
```

## Snippet 81
Lines 682-687

```Python
for file in files:
                    backup_file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(backup_file_path, backup_path)
                    destination_file_path = os.path.join(
                        destination_path, relative_path
                    )
```

## Snippet 82
Lines 691-694

```Python
logging.info(
                f"Recovery from '{backup_path}' to '{destination_path}' completed successfully!"
            )
            return f"Recovery from '{backup_path}' to '{destination_path}' completed successfully!"
```

## Snippet 83
Lines 695-697

```Python
else:
            logging.warning(f"Backup or destination path does not exist.")
            return f"Backup or destination path does not exist."
```

