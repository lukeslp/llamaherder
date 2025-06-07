# Code Snippets from toollama/API/api-tools/tools/Untitled/runCode.py

File: `toollama/API/api-tools/tools/Untitled/runCode.py`  
Language: Python  
Extracted: 2025-06-07 05:20:05  

## Snippet 1
Lines 1-17

```Python
"""
id: run_code
title: Run code
description: Run arbitrary Python or Bash code safely in a gVisor sandbox.
author: EtiennePerot
author_url: https://github.com/EtiennePerot/safe-code-execution
funding_url: https://github.com/EtiennePerot/safe-code-execution
version: 0.8.0
license: Apache-2.0
"""

# NOTE: If running Open WebUI in a container, you *need* to set up this container to allow sandboxed code execution.
# Please read the docs here:
#
#   https://github.com/EtiennePerot/safe-code-execution/blob/master/README.md
#
# This is an OpenWebUI *tool*. It allows an LLM to generate and call code on its own.
```

## Snippet 2
Lines 32-61

```Python
# You can also use it for one-off code execution like this:
#
#   echo 'print("Hello world!")' | python3 run_code.py
#

import asyncio
import argparse
import json
import os
import os.path
import pydantic
import subprocess
import sys
import tempfile
import typing
import inspect
import base64
import ctypes
import ctypes.util
import copy
import hashlib
import platform
import re
import shutil
import signal
import threading
import time
import urllib.request
import datetime
import urllib.error
```

## Snippet 3
Lines 65-78

```Python
class Valves(pydantic.BaseModel):
        _VALVE_OVERRIDE_ENVIRONMENT_VARIABLE_NAME_PREFIX = "CODE_EVAL_VALVE_OVERRIDE_"
        NETWORKING_ALLOWED: bool = pydantic.Field(
            default=True,
            description=f"Whether to allow network access during code execution; may be overridden by environment variable {_VALVE_OVERRIDE_ENVIRONMENT_VARIABLE_NAME_PREFIX}NETWORKING_ALLOWED.",
        )
        MAX_RUNTIME_SECONDS: int = pydantic.Field(
            ge=1,
            default=30,
            description=f"Maximum number of seconds code is given to run; may be overridden by environment variable {_VALVE_OVERRIDE_ENVIRONMENT_VARIABLE_NAME_PREFIX}MAX_RUNTIME_SECONDS.",
        )
        MAX_RAM_MEGABYTES: int = pydantic.Field(
            ge=0,
            default=128,
```

## Snippet 4
Lines 80-86

```Python
)
        REQUIRE_RESOURCE_LIMITING: bool = pydantic.Field(
            default=True,
            description=f"Whether to enforce resource limiting, which requires cgroups v2 to be available; may be overridden by environment variable {_VALVE_OVERRIDE_ENVIRONMENT_VARIABLE_NAME_PREFIX}REQUIRE_RESOURCE_LIMITING.",
        )
        AUTO_INSTALL: bool = pydantic.Field(
            default=True,
```

## Snippet 5
Lines 88-90

```Python
)
        CHECK_FOR_UPDATES: bool = pydantic.Field(
            default=True,
```

## Snippet 6
Lines 92-97

```Python
)
        DEBUG: bool = pydantic.Field(
            default=False,
            description=f"Whether to produce debug logs during execution; may be overridden by environment variable {_VALVE_OVERRIDE_ENVIRONMENT_VARIABLE_NAME_PREFIX}DEBUG.",
        )
```

## Snippet 7
Lines 100-104

```Python
for valve_name, valve_value in valves.dict().items():
            override = os.getenv(
                self.valves._VALVE_OVERRIDE_ENVIRONMENT_VARIABLE_NAME_PREFIX
                + valve_name
            )
```

## Snippet 8
Lines 105-107

```Python
if override is None:
                continue
            try:
```

## Snippet 9
Lines 108-113

```Python
if type(valve_value) is type(True):
                    assert override.lower() in (
                        "true",
                        "false",
                    ), 'Value must be "true" or "false"'
                    override = override.lower() == "true"
```

## Snippet 10
Lines 114-118

```Python
elif type(valve_value) is type(42):
                    override = int(override)
                else:
                    valve_value_type = type(valve_value)
                    raise ValueError(f"Unknown valve type: {valve_value_type}")
```

## Snippet 11
Lines 119-125

```Python
except Exception as e:
                raise ValueError(
                    f"Valve override {self.valves._VALVE_OVERRIDE_ENVIRONMENT_VARIABLE_NAME_PREFIX}{valve_name}={valve_value}: bad value: {e}"
                )
            else:
                setattr(self.valves, valve_name, override)
```

## Snippet 12
Lines 126-151

```Python
async def run_bash_command(
        self,
        bash_command: str,
        __event_emitter__: typing.Callable[[dict], typing.Any] = None,
    ) -> str:
        """
        Run a bash command-line or script safely in a gVisor sandbox.

        :param bash_command: Bash command or script to run.

        :return: A JSON object with the following fields: `bash_command`, `status`, `output`. In most cases, when `status` is "OK", the user is interested in the content of the `output` field. Otherwise, report the `status` field first.
        """
        result = await self._run_code(
            language=Sandbox.LANGUAGE_BASH,
            code=bash_command,
            event_emitter=__event_emitter__,
        )
        return json.dumps(
            {
                "bash_command": bash_command,
                "status": result["status"],
                "output": result["output"],
            },
            ensure_ascii=False,
        )
```

## Snippet 13
Lines 152-177

```Python
async def run_python_code(
        self,
        python_code: str,
        __event_emitter__: typing.Callable[[dict], typing.Any] = None,
    ) -> str:
        """
        Run Python code safely in a gVisor sandbox.

        :param python_code: Python code to run.

        :return: A JSON object with the following fields: `python_code`, `status`, `output`. In most cases, when `status` is "OK", the user is interested in the content of the `output` field. Otherwise, report the `status` field first.
        """
        result = await self._run_code(
            language=Sandbox.LANGUAGE_PYTHON,
            code=python_code,
            event_emitter=__event_emitter__,
        )
        return json.dumps(
            {
                "python_code": python_code,
                "status": result["status"],
                "output": result["output"],
            },
            ensure_ascii=False,
        )
```

## Snippet 14
Lines 178-196

```Python
async def _run_code(
        self,
        language: str,
        code: str,
        event_emitter: typing.Callable[[dict], typing.Any] = None,
    ) -> str:
        """
        Run code safely in a gVisor sandbox.

        :param language: Programming language of the code.
        :param code: The code to run.
        :param event_emitter: Event emitter to send status updates to.

        :return: A dictionary with the following fields: `status`, `output`.
        """
        valves = self.valves
        debug = valves.DEBUG
        emitter = EventEmitter(event_emitter, debug=debug)
```

## Snippet 15
Lines 200-204

```Python
try:
                newer_version = UpdateCheck.get_newer_version()
            except UpdateCheck.VersionCheckError as e:
                emitter.set_status_prefix(f"[Code execution update check failed: {e}] ")
            else:
```

## Snippet 16
Lines 205-212

```Python
if newer_version is not None:
                    await emitter.status(
                        f"Code execution: Update available: {newer_version}"
                    )
                    emitter.set_status_prefix(
                        f"[Code execution update available: {newer_version}] "
                    )
```

## Snippet 17
Lines 214-221

```Python
if debug:
                await emitter.fail(
                    f"[DEBUG MODE] {error_message}; language={language}; code={code}; valves=[{valves}]"
                )
            else:
                await emitter.fail(error_message)
            return {"status": status, "output": error_message}
```

## Snippet 18
Lines 227-233

```Python
await emitter.status("Checking if environment supports sandboxing...")
            Sandbox.check_setup(
                language=language,
                auto_install_allowed=valves.AUTO_INSTALL,
                require_resource_limiting=valves.REQUIRE_RESOURCE_LIMITING,
            )
```

## Snippet 19
Lines 234-269

```Python
if valves.AUTO_INSTALL and Sandbox.runsc_needs_installation():
                await emitter.status("Auto-installing gVisor...")
                Sandbox.install_runsc()

            await emitter.status("Initializing sandbox configuration...")
            status = "UNKNOWN"
            output = None
            language_title = language.title()

            # If the provided code starts/ends with "```" or
            # "```SOME_LANGUAGE", remove that.
            code = code.strip()
            code = code.removeprefix("```" + language)
            code = code.removeprefix("```")
            code = code.removesuffix("```")

            # If the provided code is a single line enclosed in
            # "`"s, strip those and whitespace away.
            code = code.strip()
            code = code.strip("`")
            code = code.strip()

            with tempfile.TemporaryDirectory(prefix="sandbox_") as tmp_dir:
                sandbox = Sandbox(
                    tmp_dir=tmp_dir,
                    language=language,
                    code=code,
                    debug=debug,
                    networking_allowed=valves.NETWORKING_ALLOWED,
                    max_runtime_seconds=valves.MAX_RUNTIME_SECONDS,
                    max_ram_bytes=max_ram_bytes,
                    require_resource_limiting=valves.REQUIRE_RESOURCE_LIMITING,
                    persistent_home_dir=None,
                )

                await emitter.status(
```

## Snippet 20
Lines 271-280

```Python
)

                await emitter.citation(
                    document=[code], metadata=[code], source={"name": "run_code"}
                )

                try:
                    result = sandbox.run()
                except Sandbox.ExecutionTimeoutError as e:
                    await emitter.fail(
```

## Snippet 21
Lines 285-296

```Python
except Sandbox.InterruptedExecutionError as e:
                    await emitter.fail("Code used too many resources")
                    status = "INTERRUPTED"
                    output = e.stderr
                except Sandbox.CodeExecutionError as e:
                    await emitter.fail(f"{language_title}: {e}")
                    status = "ERROR"
                    output = e.stderr
                else:
                    await emitter.status(
                        status="complete",
                        done=True,
```

## Snippet 22
Lines 308-311

```Python
if filename not in per_file_logs:
                            per_file_logs[filename] = []
                        per_file_logs[filename].append(log_line)
```

## Snippet 23
Lines 318-321

```Python
return {
                "status": status,
                "output": output,
            }
```

## Snippet 24
Lines 322-331

```Python
except Sandbox.PlatformNotSupportedException as e:
            return await _fail(f"Sandbox cannot run on this machine: {e}")
        except Sandbox.SandboxRuntimeException as e:
            return await _fail(f"Sandbox runtime failed: {e}")
        except Sandbox.FixableException as e:
            return await _fail(f"Environment needs setup work: {e}")
        except Sandbox.SandboxException as e:
            return await _fail(f"Sandbox exception: {e}")
        except Exception as e:
            return await _fail(f"Unhandled exception: {e}")
```

## Snippet 25
Lines 340-356

```Python
async def run_bash_command(
        self,
        bash_command: str,
        __event_emitter__: typing.Callable[[dict], typing.Any] = None,
    ) -> str:
        """
        Run a bash command-line or script safely in a gVisor sandbox.

        :param bash_command: Bash command or script to run.

        :return: A JSON object with the following fields: `status`, `output`. In most cases, when `status` is "OK", the user is interested in the content of the `output` field. Otherwise, report the `status` field first.
        """
        return await _Tools(self.valves).run_bash_command(
            bash_command=bash_command,
            __event_emitter__=__event_emitter__,
        )
```

## Snippet 26
Lines 357-372

```Python
async def run_python_code(
        self,
        python_code: str,
        __event_emitter__: typing.Callable[[dict], typing.Any] = None,
    ) -> str:
        """
        Run Python code safely in a gVisor sandbox.

        :param python_code: Python code to run.

        :return: A JSON object with the following fields: `status`, `output`. In most cases, when `status` is "OK", the user is interested in the content of the `output` field. Otherwise, report the `status` field first.
        """
        return await _Tools(self.valves).run_python_code(
            python_code=python_code,
            __event_emitter__=__event_emitter__,
        )
```

## Snippet 27
Lines 380-388

```Python
def __init__(
        self,
        event_emitter: typing.Callable[[dict], typing.Any] = None,
        debug: bool = False,
    ):
        self.event_emitter = event_emitter
        self._debug = debug
        self._status_prefix = None
```

## Snippet 28
Lines 395-402

```Python
if not self.event_emitter:
            return None
        maybe_future = self.event_emitter(
            {
                "type": typ,
                "data": data,
            }
        )
```

## Snippet 29
Lines 406-408

```Python
async def status(
        self, description="Unknown state", status="in_progress", done=False
    ):
```

## Snippet 30
Lines 409-418

```Python
if self._status_prefix is not None:
            description = f"{self._status_prefix}{description}"
        await self._emit(
            "status",
            {
                "status": status,
                "description": description,
                "done": done,
            },
        )
```

## Snippet 31
Lines 421-431

```Python
# Only do it for relatively small statuses; when debug mode is enabled,
            # this can take up a lot of space.
            await self._emit(
                "status",
                {
                    "status": status,
                    "description": description,
                    "done": done,
                },
            )
```

## Snippet 32
Lines 435-442

```Python
async def message(self, content):
        await self._emit(
            "message",
            {
                "content": content,
            },
        )
```

## Snippet 33
Lines 443-452

```Python
async def citation(self, document, metadata, source):
        await self._emit(
            "citation",
            {
                "document": document,
                "metadata": metadata,
                "source": source,
            },
        )
```

## Snippet 34
Lines 453-459

```Python
async def code_execution_result(self, output):
        await self._emit(
            "code_execution_result",
            {
                "output": output,
            },
        )
```

## Snippet 35
Lines 462-492

```Python
class Sandbox:
    """
    Sandbox manages a gVisor sandbox's lifecycle.
    """

    # Set of supported programming languages.
    LANGUAGE_PYTHON = "python"
    LANGUAGE_BASH = "bash"
    SUPPORTED_LANGUAGES = [LANGUAGE_PYTHON, LANGUAGE_BASH]

    # The following directories will be exposed as read-only to the
    # sandboxed environment. This must contain at least the necessary
    # files and libraries necessary to run the code interpreter.
    # Subdirectories of these directories may be hidden by adding them
    # to the `EMPTY_READ_ONLY_DIRECTORIES` or `EMPTY_WRITABLE_DIRECTORIES`
    # lists below.
    EXPOSED_SYSTEM_DIRECTORIES = [
        "/bin",
        "/etc/alternatives",
        "/etc/ssl/certs",
        "/lib",
        "/lib32",
        "/lib64",
        "/opt",
        "/sbin",
        "/usr",
        "/var/lib",
    ]

    # The following files will be exposed as read-only to the sandboxed
    # environment. This should contain the set of files necessary by the
```

## Snippet 36
Lines 493-598

```Python
# code interpreter to function correctly, e.g. `/etc/resolv.conf`
    # is necessary to properly resolve hosts through DNS.
    EXPOSED_SYSTEM_FILES = [
        "/etc/hosts",
        "/etc/localtime",
        "/etc/mime.types",
        "/etc/nsswitch.conf",
        "/etc/os-release",
        "/etc/resolv.conf",
        "/etc/shells",
    ]

    # The following directories will exist in the sandbox environment but
    # will appear as empty and read-only.
    # This is useful to have a filesystem that feels like a normal Linux
    # environment without actually revealing these directories to the
    # sandbox.
    EMPTY_READ_ONLY_DIRECTORIES = [
        "/etc",
        "/home",
        "/lost+found",
        "/root",
        "/run",
        "/run/user",
        "/sys",
        "/var",
    ]

    # The following directories will exist in the sandbox environment but
    # will appear as empty and writable.
    # This is useful to have a filesystem that feels like a normal Linux
    # environment without actually revealing these directories to the
    # sandbox.
    EMPTY_WRITABLE_DIRECTORIES = [
        "/dev/shm",
        "/home/user",
        "/run/user/1000",
        "/var/run",
        "/var/tmp",
        "/tmp",
    ]

    # Static parts of the OCI configuration.
    OCI_CONFIG_SKELETON = {
        "ociVersion": "1.0.0",
        "process": {
            "user": {"uid": 1000, "gid": 1000},
            "args": ["/bin/INVALID"],  # Will be filled in.
            "env": [
                # Basic environment variables.
                "EDITOR=cat",
                "LANG=C.UTF-8",
                "LC_ALL=C.UTF-8",
                "LC_CTYPE=C.UTF-8",
                "HOME=/home/user",
                "HOSTNAME=sandbox",
                "PAGER=cat",
                "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                "PWD=/home/user",
                "SHLVL=1",
                "TERM=xterm",
                "USER=user",
                "TZ=" + time.tzname[0],
            ],
            "cwd": "/home/user",
            "capabilities": {
                # No capabilities whatsoever.
                "bounding": [],
                "effective": [],
                "inheritable": [],
                "permitted": [],
            },
            "rlimits": [
                {"type": "RLIMIT_NOFILE", "hard": 1048576, "soft": 1048576},
            ],
            "noNewPrivileges": True,
        },
        "root": {
            "path": "/invalid",  # Will be filled in.
            "readonly": True,
        },
        "hostname": "sandbox",
        "mounts": [
            {"destination": "/dev", "type": "dev"},
            {"destination": "/proc", "type": "proc"},
        ],
        "linux": {
            "namespaces": [
                {"type": "pid"},
                {"type": "ipc"},
                {"type": "uts"},
                {"type": "mount"},
            ],
            "resources": {
                "memory": {
                    # `limit` may be be filled in here depending on user configuration.
                    "disableOOMKiller": False,
                },
            },
        },
    }

    # The path where the `runsc` binary will be downloaded and installed if
    # requested.
    AUTO_INSTALLATION_PATH = "/tmp/gvisor/runsc"
```

## Snippet 37
Lines 599-635

```Python
# Regular expression for log filename prefixes generated by `runsc`.
    _LOG_FILENAME_TRUNCATE_RE = re.compile(r"^runsc\.log\.\d{8}-\d{6}(?:\.\d+)?\.")

    # Other files worth logging when dumping debug logs.
    _EXTRA_DEBUG_LOG_PATHS = (
        "/etc/os-release",
        "/proc/self/cgroup",
        "/proc/self/personality",
        "/proc/self/mountinfo",
        "/proc/self/setgroups",
        "/proc/self/status",
        "/proc/self/uid_map",
        "/proc/self/gid_map",
        "/proc/cmdline",
        "/proc/cpuinfo",
        "/proc/cgroups",
        "/proc/mounts",
        "/proc/version",
    )

    # Other commands worth running when dumping debug logs.
    _EXTRA_DEBUG_LOG_COMMANDS = (
        ("pwd",),
        ("id",),
        ("uname", "-a"),
        ("ls", "-l", "/proc/self/ns"),
        ("findmnt",),
        (sys.executable, "--version"),
    )

    # Environment variable used to detect interpreter re-execution.
    _MARKER_ENVIRONMENT_VARIABLE = "__CODE_EXECUTION_STAGE"

    # libc bindings.
    # Populated using `_libc`.
    _LIBC = None
```

## Snippet 38
Lines 636-640

```Python
class _Libc:
        """
        Wrapper over libc functions.
        """
```

## Snippet 39
Lines 641-645

```Python
def __init__(self):
            libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)
            libc.mount.argtypes = (ctypes.c_char_p,)
            self._libc = libc
```

## Snippet 40
Lines 647-662

```Python
if (
                self._libc.mount(
                    source.encode("ascii"),
                    target.encode("ascii"),
                    fs.encode("ascii"),
                    0,
                    options.encode("ascii"),
                )
                < 0
            ):
                errno = ctypes.get_errno()
                raise OSError(
                    errno,
                    f"mount({source}, {target}, {fs}, {options}): {os.strerror(errno)}",
                )
```

## Snippet 41
Lines 664-667

```Python
if self._libc.umount(path.encode("ascii")) < 0:
                errno = ctypes.get_errno()
                raise OSError(errno, f"umount({path}): {os.strerror(errno)}")
```

## Snippet 42
Lines 672-678

```Python
class _SelfFile:
        """
        Manages a copy of this file's own contents.
        """

        _CONTENTS = None
```

## Snippet 43
Lines 680-683

```Python
def init(cls):
            """
            Read `__file__` into `cls._CONTENTS`. Must be called during init.
            """
```

## Snippet 44
Lines 684-687

```Python
if cls._CONTENTS is None:
                with open(__file__, "rb") as self_f:
                    cls._CONTENTS = self_f.read().decode("ascii")
```

## Snippet 45
Lines 689-695

```Python
def contents(cls) -> str:
            """
            Return this file's own contents.
            """
            assert cls._CONTENTS is not None, f"{cls.__name__}.init not called"
            return cls._CONTENTS
```

## Snippet 46
Lines 698-707

```Python
Management of the switcheroo procedure for running in a usable cgroup namespace and node.
        """

        _CGROUP_ROOT = "/sys/fs/cgroup"
        _CGROUP_NAME_PREFIX = "codeeval_"
        _CGROUP_MAX_COUNT = 4096
        _CGROUP_SANDBOX_NAME = "sandbox"
        _CGROUP_SUPERVISOR_NAME = "supervisor"
        _CGROUP_LEAF = "leaf"
```

## Snippet 47
Lines 708-717

```Python
def __init__(self, libc, log_path, max_sandbox_ram_bytes, do_resource_limiting):
            self._libc = libc
            self._log_path = log_path
            self._max_sandbox_ram_bytes = max_sandbox_ram_bytes
            self._do_resource_limiting = do_resource_limiting
            self._my_euid = None
            self._my_egid = None
            self._checkpoint = None
            self._cgroup_controllers = None
            self._needed_controllers = set()
```

## Snippet 48
Lines 718-732

```Python
if max_sandbox_ram_bytes is not None:
                self._needed_controllers.add("memory")
            self._initial_cgroup_name = None
            self._codeeval_cgroup_name = None
            self._moved = False
            self._operations = [
                # Save EUID and EGID before we move to a new user namespace.
                ("save_euid", self._save_euid),
                ("save_egid", self._save_egid),
                ("unshare_user", self._unshare_user),
                # Map our current user as being root in the new user namespace.
                ("write_uid_map", self._write_uid_map),
                ("write_setgroups", self._write_setgroups),
                ("write_gid_map", self._write_gid_map),
            ]
```

## Snippet 49
Lines 733-744

```Python
if do_resource_limiting:
                self._operations.extend(
                    (
                        # cgroupfs's view does not take into account cgroup namespaces.
                        # Weird, right?
                        # This means `/proc/PID/cgroup` will show the namespaced view of
                        # the cgroup that the PID is in, but `/sys/fs/cgroup` will still
                        # contain the whole system cgroup hierarchy regardless of namespace.
                        # Instead, namespaces act as "boundary box" around process movement
                        # requests when writing to cgroup.procs or creating new cgroups.
                        # So our first order of business here is to find out which cgroup we
                        # are running in. We do this by scanning the whole cgroupfs hierarchy
```

## Snippet 50
Lines 745-780

```Python
# and looking for our PID. This will populate
                        # `self._initial_cgroup_name`.
                        (
                            "find_self_in_cgroup_hierarchy",
                            self._find_self_in_cgroup_hierarchy,
                        ),
                        # The cgroup nesting rules are complicated, but the short of it is:
                        # A cgroup can either **contain processes** OR **have limits**.
                        # Also, cgroups that contain processes must be leaf nodes.
                        # Also, cgroups that enforce limits must have their parent cgroup
                        # also have the same limit "controller" be active.
                        # So we will have two types of cgroups:
                        #  - Leaf nodes with no controllers
                        #  - Non-leaf nodes with controllers
                        # So initially, all the processes in the container's initial
                        # namespace need to be moved out to a new leaf node,
                        # otherwise we cannot turn on controllers on the initial
                        # cgroup.
                        # So we will set up the following hierarchy:
                        #   /sys/fs/cgroup/$INITIAL:
                        #     The cgroup where the container's processes were running
                        #     the first time we run any Sandbox in the container.
                        #     It may initially have no controllers enabled, but we will
                        #     turn them on later.
                        #   /sys/fs/cgroup/$INITIAL/leaf:
                        #     The cgroup where the container's processes are moved to
                        #     from the $INITIAL cgroup upon first run of any Sandbox in
                        #     this container. When this code runs again, processes that
                        #     are already in `$INITIAL/leaf` are not moved.
                        #   /sys/fs/cgroup/$INITIAL/codeeval_$NUM:
                        #     A per-Sandbox cgroup that never contains any processes.
                        #     It will have controllers enabled on it but will never have
                        #     specific limits enforced.
                        #   /sys/fs/cgroup/$INITIAL/codeeval_$NUM/sandbox:
                        #     A per-Sandbox cgroup that never contains any processes.
                        #     It will have controllers enabled on it and will enforce
```

## Snippet 51
Lines 790-867

```Python
#     resource limits for the processes running in its /leaf.
                        #   /sys/fs/cgroup/$INITIAL/codeeval_$NUM/supervisor/leaf:
                        #     A per-Sandbox cgroup that is running a Python interpreter
                        #     that manages the lifetime of the `runsc` process.
                        #     It will run `Sandbox.maybe_main`.
                        #     It has no controllers enabled on it, but resources are
                        #     being enforced by virtue of being a child of
                        #     `$INITIAL/codeeval_$NUM/sandbox` which does enforce limits.
                        #
                        # This particular step creates the `$INITIAL/leaf` cgroup.
                        # If already created, it does nothing.
                        (
                            "create_initial_leaf_cgroup",
                            self._create_initial_leaf_cgroup,
                        ),
                        # Move all processes in `$INITIAL` to `$INITIAL/leaf`.
                        (
                            "move_initial_cgroup_processes_to_initial_leaf_cgroup",
                            self._move_initial_cgroup_processes_to_initial_leaf_cgroup,
                        ),
                        # Read the cgroup controllers enabled in `$INITIAL`. This acts
                        # as a bounding set on the ones we can enable in any child of it.
                        ("read_cgroup_controllers", self._read_cgroup_controllers),
                        # Cleanup old `$INITIAL/codeeval_*` cgroups that may be lying
                        # around from past runs.
                        ("cleanup_old_cgroups", self._cleanup_old_cgroups),
                        # Create a new `$INITIAL/codeeval_$NUM` cgroup.
                        ("create_codeeval_cgroup", self._create_codeeval_cgroup),
                        # Create a new `$INITIAL/codeeval_$NUM/sandbox` cgroup.
                        ("create_sandbox_cgroup", self._create_sandbox_cgroup),
                        # Create a new `$INITIAL/codeeval_$NUM/sandbox/leaf` cgroup.
                        (
                            "create_sandbox_leaf_cgroup",
                            self._create_sandbox_leaf_cgroup,
                        ),
                        # Create a new `$INITIAL/codeeval_$NUM/supervisor` cgroup.
                        ("create_supervisor_cgroup", self._create_supervisor_cgroup),
                        # Create a new `$INITIAL/codeeval_$NUM/supervisor/leaf` cgroup.
                        (
                            "create_supervisor_leaf_cgroup",
                            self._create_supervisor_leaf_cgroup,
                        ),
                        # Add controllers to `$INITIAL`.
                        (
                            "add_cgroup_controllers_to_root",
                            self._add_cgroup_controllers_to_root,
                        ),
                        # Add controllers to `$INITIAL/codeeval_$NUM`.
                        (
                            "add_cgroup_controllers_to_codeeval",
                            self._add_cgroup_controllers_to_codeeval,
                        ),
                        # Add controllers to `$INITIAL/codeeval_$NUM/sandbox`.
                        (
                            "add_cgroup_controllers_to_sandbox",
                            self._add_cgroup_controllers_to_sandbox,
                        ),
                        # Set resource limits on `$INITIAL/codeeval_$NUM`.
                        ("set_sandbox_cgroup_limits", self._set_sandbox_cgroup_limits),
                        # Add controllers to `$INITIAL/codeeval_$NUM/supervisor`.
                        (
                            "add_cgroup_controllers_to_supervisor",
                            self._add_cgroup_controllers_to_supervisor,
                        ),
                        # Set resource limits on `$INITIAL/codeeval_$NUM/supervisor`.
                        (
                            "set_supervisor_cgroup_limits",
                            self._set_supervisor_cgroup_limits,
                        ),
                        # Move current process to
                        # `$INITIAL/codeeval_$NUM/supervisor/leaf`.
                        (
                            "move_process_to_supervisor_leaf",
                            self._move_process_to_supervisor_leaf,
                        ),
                        # Double-check that we have moved to
                        # `$INITIAL/codeeval_$NUM/supervisor/leaf`.
                        ("sanity_check_own_cgroup", self._sanity_check_own_cgroup),
```

## Snippet 52
Lines 871-874

```Python
def _status(self):
            """
            Return the current switcheroo status.
```

## Snippet 53
Lines 875-877

```Python
:return: The last successful operation name, "UNSTARTED" if unstarted, or "OK" if all done, and some information.
            """
            main_status = self._checkpoint
```

## Snippet 54
Lines 886-917

```Python
for cgroup_components in (
                    (self._initial_cgroup_name,),
                    (self._initial_cgroup_name, self._CGROUP_LEAF),
                    (self._initial_cgroup_name, self._codeeval_cgroup_name),
                    (
                        self._initial_cgroup_name,
                        self._codeeval_cgroup_name,
                        self._CGROUP_LEAF,
                    ),
                    (
                        self._initial_cgroup_name,
                        self._codeeval_cgroup_name,
                        self._CGROUP_SUPERVISOR_NAME,
                    ),
                    (
                        self._initial_cgroup_name,
                        self._codeeval_cgroup_name,
                        self._CGROUP_SUPERVISOR_NAME,
                        self._CGROUP_LEAF,
                    ),
                    (
                        self._initial_cgroup_name,
                        self._codeeval_cgroup_name,
                        self._CGROUP_SANDBOX_NAME,
                    ),
                    (
                        self._initial_cgroup_name,
                        self._codeeval_cgroup_name,
                        self._CGROUP_SANDBOX_NAME,
                        self._CGROUP_LEAF,
                    ),
                ):
```

## Snippet 55
Lines 921-938

```Python
for filename in ("procs", "controllers", "subtree_control"):
                        data = None
                        try:
                            with self._open(
                                self._cgroup_path(
                                    *(cgroup_components + (f"cgroup.{filename}",))
                                ),
                                "rb",
                            ) as f:
                                data = f.read().decode("ascii").replace("\n", " ")
                        except Exception as e:
                            data = f"[fail: {e}]"
                        file_data.append(f"{filename}: {data}")
                    cgroup_components_joined = os.sep.join(cgroup_components)
                    file_data_joined = ", ".join(file_data)
                    cgroupfs_data.append(
                        f"{cgroup_components_joined}=[{file_data_joined}]"
                    )
```

## Snippet 56
Lines 939-941

```Python
if len(cgroupfs_data) > 0:
                    cgroupfs_data_joined = " ".join(cgroupfs_data)
                    status_line += f" {cgroupfs_data_joined}"
```

## Snippet 57
Lines 950-957

```Python
def _log(self, log_f, message):
            """
            Log a message to `log_f`.

            :param log_f: Log file object.
            """
            timestamp = time.strftime("%H:%M:%S")
            status = self._status()
```

## Snippet 58
Lines 960-966

```Python
def do(self):
            """
            Do the switcheroo.

            :raises OSError: If anything goes wrong. Progress is saved.
            """
            op_index = -1
```

## Snippet 59
Lines 968-970

```Python
if self._checkpoint == op:
                    op_index = i
                    break
```

## Snippet 60
Lines 980-984

```Python
for attempt in range(1, 4):
                        try:
                            fn()
                        except OSError as e:
                            do_log(f"OSError #{attempt}: {op}: {e}")
```

## Snippet 61
Lines 989-992

```Python
else:
                            success = True
                            break
                        time.sleep(0.1)
```

## Snippet 62
Lines 993-998

```Python
if success:
                        self._checkpoint = op
                        do_log(f"Success: {op}")
                        continue
                    assert len(errors) > 0, "Logic error"
                    first_exception = errors[0]
```

## Snippet 63
Lines 1007-1032

```Python
for cgroup_components in (
                (
                    self._initial_cgroup_name,
                    codeeval_name,
                    self._CGROUP_SANDBOX_NAME,
                    self._CGROUP_LEAF,
                ),
                (
                    self._initial_cgroup_name,
                    codeeval_name,
                    self._CGROUP_SUPERVISOR_NAME,
                    self._CGROUP_LEAF,
                ),
                (self._initial_cgroup_name, codeeval_name, self._CGROUP_SANDBOX_NAME),
                (
                    self._initial_cgroup_name,
                    codeeval_name,
                    self._CGROUP_SUPERVISOR_NAME,
                ),
                (self._initial_cgroup_name, codeeval_name),
            ):
                try:
                    os.rmdir(self._cgroup_path(*cgroup_components))
                except OSError:
                    pass
```

## Snippet 64
Lines 1039-1042

```Python
def _open(self, path, mode):
            try:
                return open(path, mode)
            except OSError as e:
```

## Snippet 65
Lines 1060-1063

```Python
def _write_setgroups(self):
            with self._open("/proc/self/setgroups", "wb") as setgroups_f:
                setgroups_f.write(b"deny")
```

## Snippet 66
Lines 1068-1074

```Python
def _find_self_in_cgroup_hierarchy(self):
            my_pid = os.getpid()
            cgroup_root_slash = self._CGROUP_ROOT + os.sep
            found_cgroup = None
            num_checked = 0
            num_except = 0
            sample_exception = None
```

## Snippet 67
Lines 1082-1089

```Python
if "cgroup.procs" not in subfiles:
                    continue
                num_checked += 1
                found_pid = False
                try:
                    with self._open(
                        os.path.join(dirpath, "cgroup.procs"), "rb"
                    ) as cgroup_procs_f:
```

## Snippet 68
Lines 1092-1097

```Python
if not pid_str:
                                    continue
                                try:
                                    pid = int(pid_str)
                                except ValueError:
                                    continue
```

## Snippet 69
Lines 1098-1100

```Python
if pid == my_pid:
                                    found_pid = True
                                    break
```

## Snippet 70
Lines 1103-1105

```Python
if sample_exception is None:
                        sample_exception = e.__class__(f"{dirpath}: {e}")
                    continue
```

## Snippet 71
Lines 1106-1108

```Python
if not found_pid:
                    continue
                current_cgroup = dirpath[len(cgroup_root_slash) :]
```

## Snippet 72
Lines 1122-1126

```Python
def _read_cgroup_controllers(self):
            cgroup_controllers = []
            with self._open(
                self._cgroup_path(self._initial_cgroup_name, "cgroup.controllers"), "rb"
            ) as cgroup_controllers_f:
```

## Snippet 73
Lines 1143-1151

```Python
def _create_initial_leaf_cgroup(self):
            try:
                os.mkdir(
                    self._cgroup_path(self._initial_cgroup_name, self._CGROUP_LEAF),
                    mode=0o755,
                )
            except FileExistsError:
                pass
```

## Snippet 74
Lines 1153-1168

```Python
for counter in range(0, self._CGROUP_MAX_COUNT):
                codeeval_cgroup_name_candidate = f"{self._CGROUP_NAME_PREFIX}{counter}"
                cgroup_path = self._cgroup_path(
                    self._initial_cgroup_name, codeeval_cgroup_name_candidate
                )
                try:
                    os.mkdir(cgroup_path, mode=0o755)
                except FileExistsError:
                    pass
                else:
                    self._codeeval_cgroup_name = codeeval_cgroup_name_candidate
                    return
            initial_cgroup_path_prefix = self._cgroup_path(
                self._initial_cgroup_name, self._CGROUP_NAME_PREFIX
            )
            raise OSError(
```

## Snippet 75
Lines 1172-1181

```Python
def _create_sandbox_cgroup(self):
            os.mkdir(
                self._cgroup_path(
                    self._initial_cgroup_name,
                    self._codeeval_cgroup_name,
                    self._CGROUP_SANDBOX_NAME,
                ),
                mode=0o755,
            )
```

## Snippet 76
Lines 1182-1192

```Python
def _create_sandbox_leaf_cgroup(self):
            os.mkdir(
                self._cgroup_path(
                    self._initial_cgroup_name,
                    self._codeeval_cgroup_name,
                    self._CGROUP_SANDBOX_NAME,
                    self._CGROUP_LEAF,
                ),
                mode=0o755,
            )
```

## Snippet 77
Lines 1193-1202

```Python
def _create_supervisor_cgroup(self):
            os.mkdir(
                self._cgroup_path(
                    self._initial_cgroup_name,
                    self._codeeval_cgroup_name,
                    self._CGROUP_SUPERVISOR_NAME,
                ),
                mode=0o755,
            )
```

## Snippet 78
Lines 1203-1213

```Python
def _create_supervisor_leaf_cgroup(self):
            os.mkdir(
                self._cgroup_path(
                    self._initial_cgroup_name,
                    self._codeeval_cgroup_name,
                    self._CGROUP_SUPERVISOR_NAME,
                    self._CGROUP_LEAF,
                ),
                mode=0o755,
            )
```

## Snippet 79
Lines 1214-1216

```Python
def _add_cgroup_controllers_to(self, *cgroup_components):
            add_controllers = tuple(
                controller
```

## Snippet 80
Lines 1219-1226

```Python
)
            cgroup_components = tuple(cgroup_components) + ("cgroup.subtree_control",)
            cgroup_subtree_control_path = self._cgroup_path(*cgroup_components)
            try:
                with self._open(
                    cgroup_subtree_control_path, "wb"
                ) as cgroup_subtree_control_f:
                    controllers_data = (
```

## Snippet 81
Lines 1235-1239

```Python
got_controllers = set()
            try:
                with self._open(
                    cgroup_subtree_control_path, "rb"
                ) as cgroup_subtree_control_f:
```

## Snippet 82
Lines 1242-1244

```Python
if not controller:
                                continue
                            got_controllers.add(controller.decode("ascii"))
```

## Snippet 83
Lines 1245-1249

```Python
except OSError as e:
                raise OSError(
                    f"Reading controllers from {cgroup_subtree_control_path}: {e}"
                )
            assert all(
```

## Snippet 84
Lines 1256-1260

```Python
def _add_cgroup_controllers_to_codeeval(self):
            return self._add_cgroup_controllers_to(
                self._initial_cgroup_name, self._codeeval_cgroup_name
            )
```

## Snippet 85
Lines 1261-1267

```Python
def _add_cgroup_controllers_to_sandbox(self):
            return self._add_cgroup_controllers_to(
                self._initial_cgroup_name,
                self._codeeval_cgroup_name,
                self._CGROUP_SANDBOX_NAME,
            )
```

## Snippet 86
Lines 1268-1274

```Python
def _add_cgroup_controllers_to_supervisor(self):
            return self._add_cgroup_controllers_to(
                self._initial_cgroup_name,
                self._codeeval_cgroup_name,
                self._CGROUP_SUPERVISOR_NAME,
            )
```

## Snippet 87
Lines 1275-1282

```Python
def _move_initial_cgroup_processes_to_initial_leaf_cgroup(self):
            initial_cgroup_procs_path = self._cgroup_path(
                self._initial_cgroup_name, "cgroup.procs"
            )
            initial_leaf_cgroup_procs_path = self._cgroup_path(
                self._initial_cgroup_name, self._CGROUP_LEAF, "cgroup.procs"
            )
            done_zero_pid = False
```

## Snippet 88
Lines 1283-1287

```Python
while True:
                moving_process_pid = None
                with self._open(
                    initial_cgroup_procs_path, "rb"
                ) as initial_cgroup_procs_f:
```

## Snippet 89
Lines 1292-1297

```Python
if not pid_str:
                                continue
                            try:
                                pid = int(pid_str)
                            except ValueError:
                                continue
```

## Snippet 90
Lines 1299-1301

```Python
if done_zero_pid:
                                    continue
                                done_zero_pid = True
```

## Snippet 91
Lines 1304-1312

```Python
if moving_process_pid is None:
                    break
                with self._open(
                    initial_leaf_cgroup_procs_path, "wb"
                ) as initial_leaf_cgroup_procs_f:
                    initial_leaf_cgroup_procs_f.write(
                        f"{moving_process_pid}\n".encode("ascii")
                    )
```

## Snippet 92
Lines 1313-1330

```Python
def _move_process_to_supervisor_leaf(self):
            supervisor_leaf_cgroup_procs_path = self._cgroup_path(
                self._initial_cgroup_name,
                self._codeeval_cgroup_name,
                self._CGROUP_SUPERVISOR_NAME,
                self._CGROUP_LEAF,
                "cgroup.procs",
            )
            f = self._open(supervisor_leaf_cgroup_procs_path, "wb")
            try:
                f.write(b"0\n")
                self._moved = True
            finally:
                try:
                    f.close()
                except OSError:
                    pass
```

## Snippet 93
Lines 1331-1344

```Python
def _move_process_back(self):
            initial_leaf_cgroup_procs_path = self._cgroup_path(
                self._initial_cgroup_name, self._CGROUP_LEAF, "cgroup.procs"
            )
            f = self._open(initial_leaf_cgroup_procs_path, "wb")
            try:
                f.write(b"0\n")
                self._moved = False
            finally:
                try:
                    f.close()
                except OSError:
                    pass
```

## Snippet 94
Lines 1345-1347

```Python
def _set_cgroup_limits(self, *cgroup_components):
            cgroup_components = tuple(cgroup_components) + ("memory.max",)
            cgroup_memory_max_path = self._cgroup_path(*cgroup_components)
```

## Snippet 95
Lines 1348-1355

```Python
if self._max_sandbox_ram_bytes is not None:
                try:
                    with self._open(cgroup_memory_max_path, "wb") as memory_max_f:
                        memory_max_f.write(
                            f"{self._max_sandbox_ram_bytes}\n".encode("ascii")
                        )
                except OSError as e:
                    raise OSError(
```

## Snippet 96
Lines 1358-1362

```Python
for swap_type in ("swap", "zswap"):
                cgroup_swap_components = tuple(cgroup_components) + (
                    f"memory.{swap_type}.max",
                )
                cgroup_swap_path = self._cgroup_path(*cgroup_swap_components)
```

## Snippet 97
Lines 1363-1369

```Python
if not os.path.exists(cgroup_swap_path):
                    continue
                try:
                    with self._open(cgroup_swap_path, "wb") as swap_max_f:
                        swap_max_f.write("0\n".encode("ascii"))
                except OSError as e:
                    raise OSError(
```

## Snippet 98
Lines 1373-1379

```Python
def _set_supervisor_cgroup_limits(self):
            return self._set_cgroup_limits(
                self._initial_cgroup_name,
                self._codeeval_cgroup_name,
                self._CGROUP_SUPERVISOR_NAME,
            )
```

## Snippet 99
Lines 1380-1386

```Python
def _set_sandbox_cgroup_limits(self):
            return self._set_cgroup_limits(
                self._initial_cgroup_name,
                self._codeeval_cgroup_name,
                self._CGROUP_SANDBOX_NAME,
            )
```

## Snippet 100
Lines 1387-1398

```Python
def _sanity_check_own_cgroup(self):
            supervisor_cgroup_path = self._cgroup_path(
                self._initial_cgroup_name,
                self._codeeval_cgroup_name,
                self._CGROUP_SUPERVISOR_NAME,
            )
            with self._open("/proc/self/cgroup", "rb") as cgroup_f:
                cgroup_data = cgroup_f.read().decode("ascii").strip()
            assert cgroup_data.endswith(
                os.sep + os.path.join(self._CGROUP_SUPERVISOR_NAME, self._CGROUP_LEAF)
            ), f"Unexpected self cgroup after moving to {supervisor_cgroup_path}: {cgroup_data}"
```

## Snippet 101
Lines 1403-1405

```Python
:return: A function to move the current process to the sandbox cgroup.
            :raises SandboxException: If not queried after we have already chosen a new cgroup name.
            """
```

## Snippet 102
Lines 1408-1412

```Python
if self._codeeval_cgroup_name is None:
                raise Sandbox.SandboxException(
                    "Tried to move process to sandbox leaf cgroup before we know it"
                )
```

## Snippet 103
Lines 1414-1429

```Python
"""Dependency-free preexec_fn-compatible function to move to the given cgroup.procs."""
                try:
                    f = open(cgroup_path, "wb")
                except OSError as e:
                    raise OSError(f"Cannot open cgroup path {cgroup_path}: {e}")
                try:
                    f.write(b"0\n")
                except OSError as e:
                    raise OSError(f"Cannot move process to {cgroup_path}: {e}")
                finally:
                    try:
                        f.close()
                    except OSError:
                        pass
                clone_newcgroup = (
                    os.CLONE_NEWCGROUP
```

## Snippet 104
Lines 1433-1443

```Python
if "unshare" in os.__dict__:  # Python >= 3.12.
                    try:
                        os.unshare(clone_newcgroup)
                    except OSError as e:
                        raise OSError(f"unshare({clone_newcgroup}) failed: {e}")
                else:
                    import ctypes

                    libc = ctypes.CDLL(None)
                    libc.unshare.argtypes = [ctypes.c_int]
                    rc = libc.unshare(clone_newcgroup)
```

## Snippet 105
Lines 1447-1455

```Python
sandbox_cgroup_procs_path = self._cgroup_path(
                self._initial_cgroup_name,
                self._codeeval_cgroup_name,
                self._CGROUP_SANDBOX_NAME,
                self._CGROUP_LEAF,
                "cgroup.procs",
            )[:]
            return lambda: _move(sandbox_cgroup_procs_path)
```

## Snippet 106
Lines 1465-1479

```Python
if not self._do_resource_limiting:
                return lambda: None
            self_memory_path = self._cgroup_path(
                self._initial_cgroup_name,
                self._codeeval_cgroup_name,
                "memory.peak",
            )
            sandbox_procs_path = self._cgroup_path(
                self._initial_cgroup_name,
                self._codeeval_cgroup_name,
                self._CGROUP_SANDBOX_NAME,
                self._CGROUP_LEAF,
                "cgroup.procs",
            )
```

## Snippet 107
Lines 1480-1482

```Python
def _kill():
                new_pids_to_kill = True
                pids_to_kill = set()
```

## Snippet 108
Lines 1483-1485

```Python
while new_pids_to_kill:
                    prev_pids_to_kill_len = len(pids_to_kill)
                    with self._open(sandbox_procs_path, "rb") as cgroup_procs_f:
```

## Snippet 109
Lines 1488-1493

```Python
if not pid_str:
                                    continue
                                try:
                                    pid = int(pid_str)
                                except ValueError:
                                    continue
```

## Snippet 110
Lines 1496-1502

```Python
for pid_to_kill in pids_to_kill:
                        try:
                            os.kill(pid_to_kill, signal.SIGKILL)
                        except Exception:
                            pass
                    new_pids_to_kill = prev_pids_to_kill_len < len(pids_to_kill)
```

## Snippet 111
Lines 1504-1509

```Python
if self._max_sandbox_ram_bytes is not None:
                    try:
                        with self._open(self_memory_path, "rb") as memory_peak_f:
                            memory_peak_bytes = int(
                                memory_peak_f.read().decode("ascii").strip()
                            )
```

## Snippet 112
Lines 1512-1517

```Python
except Exception as e:
                        print(
                            f"Warning: Failed to enforce code execution RAM: {e}",
                            file=sys.stderr,
                        )
```

## Snippet 113
Lines 1522-1524

```Python
while True:
                    time.sleep(0.1)
                    with lock:
```

## Snippet 114
Lines 1534-1540

```Python
def _cancel():
                with lock:
                    enabled[0] = False
                monitor_thread.join()

            return _cancel
```

## Snippet 115
Lines 1546-1550

```Python
def __init__(self, *args, **kwargs):
            self._sandbox_exception_args = tuple(args)
            self._sandbox_exception_kwargs = dict(kwargs)
            super().__init__(*args, **kwargs)
```

## Snippet 116
Lines 1551-1556

```Python
class PlatformNotSupportedException(SandboxException):
        """
        Raised when the sandbox cannot run on the current platform.
        The only way to fix this is to run on a different platform.
        """
```

## Snippet 117
Lines 1557-1562

```Python
class SandboxRuntimeException(SandboxException):
        """
        Raised when the sandbox fails to run properly.
        This means gVisor itself is failing, not the code in the sandbox.
        """
```

## Snippet 118
Lines 1563-1568

```Python
class ExecutionError(subprocess.CalledProcessError):
        """
        Raised when the sandboxed code fails to run.
        This means the sandbox worked, but the code that ran within failed.
        """
```

## Snippet 119
Lines 1569-1575

```Python
def __init__(self, code, **kwargs):
            super().__init__(**kwargs)
            self._code = code
            self._sandbox_exception_args = ()
            self._sandbox_exception_kwargs = kwargs.copy()
            self._sandbox_exception_kwargs["code"] = code
```

## Snippet 120
Lines 1576-1579

```Python
def __str__(self):
            super_str = super().__str__()
            full_code = self._code
            short_code = full_code.replace("\n", ";")
```

## Snippet 121
Lines 1594-1598

```Python
class CodeExecutionError(ExecutionError):
        """
        Raised when the sandboxed code returns with a non-zero exit code.
        """
```

## Snippet 122
Lines 1599-1602

```Python
def __str__(self):
            super_str = super().__str__()
            return f"Code error: {super_str}"
```

## Snippet 123
Lines 1608-1611

```Python
def __str__(self):
            super_str = super().__str__()
            return f"Timeout: {super_str}"
```

## Snippet 124
Lines 1612-1617

```Python
class InterruptedExecutionError(ExecutionError):
        """
        Raised when the code runs but is interrupted before it finishes.
        This could happen from running out of resources.
        """
```

## Snippet 125
Lines 1618-1621

```Python
def __str__(self):
            super_str = super().__str__()
            return f"Interrupted: {super_str}"
```

## Snippet 126
Lines 1627-1631

```Python
class GVisorNotInstalledException(FixableException):
        """
        Raised when gVisor is not installed (`runsc` not found in $PATH).
        """
```

## Snippet 127
Lines 1632-1636

```Python
class CorruptDownloadException(FixableException):
        """
        Raised when auto-downloading gVisor resulted in a hash mismatch.
        """
```

## Snippet 128
Lines 1637-1642

```Python
class EnvironmentNeedsSetupException(FixableException):
        """
        Raised when the environment does not give adequate control over the
        system to run gVisor properly.
        """
```

## Snippet 129
Lines 1644-1651

```Python
def check_platform(cls):
        """
        Verifies that this tool is running on a supported platform.

        :return: Nothing.
        :raises PlatformNotSupportedException: If running on an unsupported platform.
        """
        uname = platform.uname()
```

## Snippet 130
Lines 1660-1662

```Python
Verifies that cgroupfs is mounted and usable for resource limiting.

        :return: Nothing.
```

## Snippet 131
Lines 1673-1680

```Python
# Try to open the file for writing to see if we can actually control cgroups.
        # They may be mounted read-only, as is default with Docker.
        try:
            with open(
                "/sys/fs/cgroup/cgroup.subtree_control", "wb"
            ) as subtree_control_f:
                pass
        except OSError:
```

## Snippet 132
Lines 1696-1704

```Python
def check_procfs(cls):
        """
        Verifies that we have an unobstructed view of procfs.

        :return: Nothing.
        :raises EnvironmentNeedsSetupException: If procfs is obstructed.
        """
        mount_infos = []
        with open("/proc/self/mountinfo", "rb") as mountinfo_f:
```

## Snippet 133
Lines 1707-1709

```Python
if not line:
                    continue
                mount_components = line.split(" ")
```

## Snippet 134
Lines 1710-1712

```Python
if len(mount_components) < 10:
                    continue
                hyphen_index = mount_components.index("-")
```

## Snippet 135
Lines 1713-1720

```Python
if hyphen_index < 6:
                    continue
                mount_info = {
                    "mount_path": mount_components[4],
                    "path_within_mount": mount_components[3],
                    "fs_type": mount_components[hyphen_index + 1],
                }
                mount_infos.append(mount_info)
```

## Snippet 136
Lines 1726-1730

```Python
if len(procfs_mounts) == 0:
            raise cls.EnvironmentNeedsSetupException(
                "procfs is not mounted; please mount it"
            )
        obstructed_procfs_mounts = set()
```

## Snippet 137
Lines 1744-1750

```Python
def unshare(cls, flags):
        """
        Implementation of `os.unshare` that works on Python < 3.12.

        :param flags: Flags to pass to the `unshare(2)` system call.
        :raises OSError: If something goes wrong.
        """
```

## Snippet 138
Lines 1751-1756

```Python
if "unshare" in os.__dict__:  # Python >= 3.12.
            return os.unshare(flags)

        # Python <= 3.11:
        return cls._libc().unshare(flags)
```

## Snippet 139
Lines 1758-1768

```Python
def check_unshare(cls):
        """
        Verifies that the `unshare(2)` system call is available.

        :return: Nothing.
        :raises EnvironmentNeedsSetupException: If `unshare(2)` is not available.
        """
        try:
            cls.unshare(0)
        except OSError:
            raise cls.EnvironmentNeedsSetupException(
```

## Snippet 140
Lines 1773-1776

```Python
def get_runsc_path(cls):
        """
        Returns the absolute path where the `runsc` binary is installed.
```

## Snippet 141
Lines 1777-1779

```Python
:return: Absolute path to `runsc` binary, or `None` if not installed.
        """
        runsc_path = shutil.which("runsc")
```

## Snippet 142
Lines 1782-1785

```Python
if os.path.exists(cls.AUTO_INSTALLATION_PATH):
            return cls.AUTO_INSTALLATION_PATH
        return None
```

## Snippet 143
Lines 1787-1794

```Python
def runsc_needs_installation(cls):
        """
        Checks whether the `runsc` binary is installed.

        :return: Whether the `runsc` binary is installed.
        """
        return cls.get_runsc_path() is None
```

## Snippet 144
Lines 1798-1802

```Python
Download and install the `runsc` binary if not already present.

        :return: Nothing.
        :raises CorruptDownloadException: If the download resulted in a hash mismatch.
        """
```

## Snippet 145
Lines 1803-1823

```Python
if not cls.runsc_needs_installation():
            return
        uname = platform.uname()
        release_url_dir = f"https://storage.googleapis.com/gvisor/releases/release/latest/{uname.machine}"
        os.makedirs(
            os.path.dirname(cls.AUTO_INSTALLATION_PATH), mode=0o755, exist_ok=True
        )
        with tempfile.TemporaryDirectory(
            prefix="sandbox_download_"
        ) as download_tmp_dir:
            download_path = os.path.join(download_tmp_dir, "runsc")
            urllib.request.urlretrieve(
                url=f"{release_url_dir}/runsc",
                filename=download_path,
            )
            sha512_raw = urllib.request.urlopen(
                f"{release_url_dir}/runsc.sha512"
            ).read()
            want_sha512 = sha512_raw.decode("ascii").split(" ")[0]
            runsc_hash = hashlib.sha512()
            with open(download_path, "rb") as runsc_f:
```

## Snippet 146
Lines 1826-1828

```Python
if not chunk:
                        break
                    runsc_hash.update(chunk)
```

## Snippet 147
Lines 1830-1836

```Python
if runsc_sha512 != want_sha512:
                raise cls.CorruptDownloadException(
                    "gVisor hash mismatch when auto-installing; please install gVisor manually"
                )
            os.chmod(download_path, mode=0o755)
            os.rename(download_path, cls.AUTO_INSTALLATION_PATH)
```

## Snippet 148
Lines 1838-1855

```Python
def check_setup(
        cls,
        language: str,
        auto_install_allowed: bool,
        require_resource_limiting: bool,
    ):
        """
        Verifies that the environment is compatible with running sandboxes.

        :param language: The programming language to run.
        :param auto_install_allowed: Whether auto-installation of `runsc` is allowed.
        :param require_resource_limiting: Check that the host supports resource limiting via cgroups.

        :return: Nothing.
        :raises ValueError: If provided an invalid language name.
        :raises PlatformNotSupportedException: If running on an unsupported platform.
        :raises FixableException: If another issue occurs but that can be fixed by the user.
        """
```

## Snippet 149
Lines 1858-1861

```Python
if shutil.which("bash") is None:
            raise cls.EnvironmentNeedsSetupException(
                "bash is not installed (`bash` binary not found in $PATH); please install it"
            )
```

## Snippet 150
Lines 1862-1867

```Python
if shutil.which("unshare") is None:
            raise cls.EnvironmentNeedsSetupException(
                "unshare is not installed (`unshare` binary not found in $PATH); please install it"
            )
        cls.check_platform()
        cls.check_unshare()
```

## Snippet 151
Lines 1868-1870

```Python
if require_resource_limiting:
            cls.check_cgroups()
        cls.check_procfs()
```

## Snippet 152
Lines 1878-1881

```Python
if cls._LIBC is None:
            cls._LIBC = cls._Libc()
        return cls._LIBC
```

## Snippet 153
Lines 1890-1899

```Python
if cls._MARKER_ENVIRONMENT_VARIABLE not in os.environ:
            return
        directives = json.load(sys.stdin)
        try:
            result = cls(**directives["settings"])._run()
        except Exception as e:
            exception_info = {
                "name": e.__class__.__name__,
                "str": str(e),
            }
```

## Snippet 154
Lines 1900-1908

```Python
if isinstance(e, cls.SandboxException) or isinstance(e, cls.ExecutionError):
                exception_info["args"] = e._sandbox_exception_args
                exception_info["kwargs"] = e._sandbox_exception_kwargs
            json.dump(
                {
                    "exception": exception_info,
                },
                sys.stdout,
            )
```

## Snippet 155
Lines 1914-1926

```Python
if type(stderr) is not type(b""):
                stderr = stderr.encode("utf-8", errors="replace")
            json.dump(
                {
                    "result": {
                        "args": result.args,
                        "returncode": result.returncode,
                        "stdout": base64.b64encode(stdout).decode("utf-8"),
                        "stderr": base64.b64encode(stderr).decode("utf-8"),
                    },
                },
                sys.stdout,
            )
```

## Snippet 156
Lines 1927-1930

```Python
finally:
            sys.stdout.flush()
            sys.exit(0)
```

## Snippet 157
Lines 1931-1948

```Python
def __init__(
        self,
        tmp_dir: str,
        language: str,
        code: str,
        debug: bool,
        networking_allowed: bool,
        max_runtime_seconds: int,
        max_ram_bytes: typing.Optional[int] = None,
        require_resource_limiting: bool = False,
        persistent_home_dir: typing.Optional[str] = None,
    ):
        """
        Constructor.

        :param tmp_dir: Temporary directory exclusive to this sandbox. Must outlive the Sandbox object.
        :param language: The language of the code; must be one of `SUPPORTED_LANGUAGES`.
        :param code: Arbitrary code that needs to run in the sandbox.
```

## Snippet 158
Lines 1949-1951

```Python
:param debug: Whether or not to enable debug-level logging for the sandbox.
        :param networking_allowed: Whether the code should be given access to the network.
        :param max_runtime_seconds: How long the code should be allowed to run, in seconds.
```

## Snippet 159
Lines 1953-1969

```Python
:param require_resource_limiting: If true, refuse to launch a sandbox if the host doesn't support resource limiting via cgroups.
        :param persistent_home_dir: Optional directory which will be mapped read-write to this real host directory.
        """
        self._init(
            {
                "tmp_dir": tmp_dir,
                "language": language,
                "code": code,
                "debug": debug,
                "networking_allowed": networking_allowed,
                "max_runtime_seconds": max_runtime_seconds,
                "max_ram_bytes": max_ram_bytes,
                "require_resource_limiting": require_resource_limiting,
                "persistent_home_dir": persistent_home_dir,
            }
        )
```

## Snippet 160
Lines 1970-1990

```Python
def _init(self, settings):
        self._settings = settings
        self._tmp_dir = self._settings["tmp_dir"]
        self._bundle_path = os.path.join(self._tmp_dir, "bundle")
        self._runtime_root_path = os.path.join(self._tmp_dir, "runtime")
        self._logs_path = os.path.join(self._tmp_dir, "logs")
        self._gotmp_dir = os.path.join(self._tmp_dir, "gotmp")
        self._sandbox_shared_path = os.path.join(self._tmp_dir, "sandbox")
        self._language = self._settings["language"]
        self._code = self._settings["code"]
        self._debug = self._settings["debug"]
        self._networking_allowed = self._settings["networking_allowed"]
        self._max_runtime_seconds = self._settings["max_runtime_seconds"]
        self._max_ram_bytes = self._settings["max_ram_bytes"]
        self._require_resource_limiting = self._settings[
            "require_resource_limiting"
        ] or all((self._max_ram_bytes is None,))
        self._persistent_home_dir = self._settings["persistent_home_dir"]
        self._sandboxed_command = None
        self._switcheroo = None
```

## Snippet 161
Lines 1991-1999

```Python
def _setup_sandbox(self):
        """
        Set up the sandbox's root filesystem and OCI config prior to execution.
        Runs in separate forked process. Performs the switcheroo.

        :raises FixableException: If an issue occurs but that can be fixed by the user.
        """
        # Set up basic configuration options.
        oci_config = copy.deepcopy(self.OCI_CONFIG_SKELETON)
```

## Snippet 162
Lines 2000-2009

```Python
if self._max_ram_bytes:
            oci_config["linux"]["resources"]["memory"]["limit"] = self._max_ram_bytes
        os.makedirs(self._bundle_path, mode=0o711)
        os.makedirs(self._runtime_root_path, mode=0o711)
        os.makedirs(self._logs_path, mode=0o711)
        os.makedirs(self._sandbox_shared_path, mode=0o777)
        os.makedirs(self._gotmp_dir, mode=0o711)
        os.chmod(self._sandbox_shared_path, mode=0o777, follow_symlinks=False)
        rootfs_path = os.path.join(self._tmp_dir, "rootfs")
        os.makedirs(rootfs_path, mode=0o755)
```

## Snippet 163
Lines 2017-2039

```Python
if not self._require_resource_limiting:
            try:
                self.check_cgroups()
            except self.EnvironmentNeedsSetupException:
                do_resource_limiting = False
        self._switcheroo = self._Switcheroo(
            libc=self._libc(),
            log_path=os.path.join(self._logs_path, "switcheroo.txt"),
            max_sandbox_ram_bytes=self._max_ram_bytes,
            do_resource_limiting=do_resource_limiting,
        )
        try:
            self._switcheroo.do()
        except Exception as e:
            try:
                switcheroo_status = self._switcheroo._status()
            except Exception:
                raise e
            else:
                raise e.__class__(f"{e}; {switcheroo_status}")

        # Locate the interpreter to use.
        interpreter_path = sys.executable
```

## Snippet 164
Lines 2042-2055

```Python
if interpreter_path is None:
            raise RuntimeError("Interpreter not found")
        oci_config["mounts"].append(
            {
                "type": "bind",
                "source": interpreter_path,
                "destination": interpreter_path,
                "options": ["ro"],
            }
        )

        # Populate rootfs. This is a multi-step process.

        # Create writable empty directories.
```

## Snippet 165
Lines 2056-2067

```Python
for d in self.EMPTY_WRITABLE_DIRECTORIES:
            rootfs_subdir = os.path.join(rootfs_path, d.removeprefix(os.path.sep))
            os.makedirs(rootfs_subdir, mode=0o755, exist_ok=True)
            oci_config["mounts"].append(
                {
                    "type": "tmpfs",
                    "destination": d,
                    "options": [],
                }
            )

        # Create read-only empty directories.
```

## Snippet 166
Lines 2068-2075

```Python
for d in self.EMPTY_READ_ONLY_DIRECTORIES + [os.path.dirname(interpreter_path)]:
            rootfs_subdir = os.path.join(rootfs_path, d.removeprefix(os.path.sep))
            os.makedirs(rootfs_subdir, mode=0o755, exist_ok=True)

        # Handle exposed host symlinks. These will show up as symlinks with the same
        # target path in the sandbox, so they do not expose the host's view of the
        # directory they point to.
        symlinks = set()
```

## Snippet 167
Lines 2077-2083

```Python
if not os.path.islink(p):
                continue
            rootfs_subpath = os.path.join(rootfs_path, p.removeprefix(os.path.sep))
            os.makedirs(os.path.dirname(rootfs_subpath), mode=0o755, exist_ok=True)
            os.symlink(src=os.readlink(p), dst=rootfs_subpath)
            symlinks.add(p)
```

## Snippet 168
Lines 2088-2100

```Python
if not os.path.isdir(d):
                continue  # The host does not have a directory at this path.
            rootfs_subdir = os.path.join(rootfs_path, d.removeprefix(os.path.sep))
            os.makedirs(rootfs_subdir, mode=0o755, exist_ok=True)
            oci_config["mounts"].append(
                {
                    "type": "bind",
                    "source": d,
                    "destination": d,
                    "options": ["ro", "rbind"],
                }
            )
```

## Snippet 169
Lines 2105-2118

```Python
if not os.path.isfile(f):
                continue  # The host does not have a file at this path.
            rootfs_subpath = os.path.join(rootfs_path, f.removeprefix(os.path.sep))
            rootfs_subdir = os.path.dirname(rootfs_subpath)
            os.makedirs(rootfs_subdir, mode=0o755, exist_ok=True)
            oci_config["mounts"].append(
                {
                    "type": "bind",
                    "source": f,
                    "destination": f,
                    "options": ["ro"],
                }
            )
```

## Snippet 170
Lines 2119-2127

```Python
# Shared sandbox directory to propagate exit code and persistent files.
        oci_config["mounts"].append(
            {
                "type": "bind",
                "source": self._sandbox_shared_path,
                "destination": "/sandbox",
                "options": ["rw"],
            }
        )
```

## Snippet 171
Lines 2128-2153

```Python
if self._persistent_home_dir is not None:
            oci_config["mounts"].append(
                {
                    "type": "bind",
                    "source": self._persistent_home_dir,
                    "destination": "/sandbox/persistent",
                    "options": ["rw"],
                }
            )

        # Sort mounts to ensure proper overlay order.
        oci_config["mounts"].sort(key=lambda m: m["destination"])

        # Generate some /etc files that look normal.
        with open(os.path.join(rootfs_path, "etc/hostname"), "w") as hostname_f:
            hostname_f.write("sandbox\n")
        with open(os.path.join(rootfs_path, "etc/passwd"), "w") as passwd_f:
            passwd_f.write("user:x:1000:1000:user:/home/user:/bin/bash\n")

        # Generate command line to run in the sandbox.
        self._sandboxed_command = [
            shutil.which("bash"),
            "-c",
            "; ".join(
                (
                    "echo OK > /sandbox/started",
```

## Snippet 172
Lines 2161-2177

```Python
]

        # Work around issue that gVisor does not preserve correct UID mappings when running as non-root user in the sandbox.
        # So map current user to 0:0, then create a new user namespace immediately before running command and remap to
        # correct UID/GID.
        oci_config["process"]["user"]["uid"] = 0
        oci_config["process"]["user"]["gid"] = 0
        oci_config["process"]["args"] = [
            shutil.which("unshare"),
            "--map-user=1000",
            "--map-group=1000",
        ] + self._sandboxed_command

        # We are done. Write OCI config to bundle directory.
        with open(os.path.join(self._bundle_path, "config.json"), "w") as bundle_f:
            json.dump(oci_config, bundle_f, indent=2, sort_keys=True)
```

## Snippet 173
Lines 2180-2183

```Python
Spawn and wait for the sandbox. Runs in separate forked process.

        :return: A `CompletedProcess` object representing the return code and stdout/stderr of the code interpreter.
        :raises Sandbox.SandboxRuntimeException: If the sandbox failed to start or behaved incorrectly regardless of the code being evaluated.
```

## Snippet 174
Lines 2184-2190

```Python
:raises Sandbox.ExecutionTimeoutError: If the code interpreter ran for longer than configured.
        :raises Sandbox.InterruptedExecutionError: If the code interpreter died without providing a return code; usually due to running over resource limits.
        :raises sandbox.CodeExecutionError: If the code interpreter failed to execute the given code. This does not represent a sandbox failure.
        """
        try:
            self._setup_sandbox()
```

## Snippet 175
Lines 2191-2227

```Python
network_mode = "host" if self._networking_allowed else "none"
            runsc_argv = [
                self.get_runsc_path(),
                "--rootless=true",
                "--directfs=false",
                f"--network={network_mode}",
                "--ignore-cgroups=true",  # We already took care of cgroups manually.
                f"--root={self._runtime_root_path}",
                f"--debug-log={self._logs_path}/",
                "run",
                f"--bundle={self._bundle_path}",
                "sandbox",
            ]
            runsc_env = os.environ.copy()
            runsc_env["TMPDIR"] = self._gotmp_dir
            started_marker_path = os.path.join(self._sandbox_shared_path, "started")
            resource_monitor_cancel = self._switcheroo.monitor_cgroup_resources()
            try:
                result = subprocess.run(
                    runsc_argv,
                    env=runsc_env,
                    preexec_fn=self._switcheroo.move_process_to_sandbox_leaf_cgroup_lambda(),
                    input=self._code + "\n",
                    text=True,
                    capture_output=True,
                    timeout=self._max_runtime_seconds,
                    check=True,
                )
            except subprocess.TimeoutExpired as e:
                raise self.ExecutionTimeoutError(
                    code=self._code,
                    returncode=126,
                    cmd=self._sandboxed_command,
                    output=e.stdout,
                    stderr=e.stderr,
                )
            except subprocess.CalledProcessError as e:
```

## Snippet 176
Lines 2228-2237

```Python
if os.path.isfile(started_marker_path):
                    raise self.InterruptedExecutionError(
                        code=self._code,
                        returncode=127,
                        cmd=self._sandboxed_command,
                        output=e.stdout,
                        stderr=e.stderr,
                    )
                logs = {}
```

## Snippet 177
Lines 2242-2245

```Python
if filename not in logs:
                            logs[filename] = []
                        logs[filename].append(log_line)
```

## Snippet 178
Lines 2249-2253

```Python
if self._debug:
                    raise self.SandboxRuntimeException(
                        f"Sandbox failed to start: {e}; stderr: {stderr}; logs: {json_logs}"
                    )
                raise self.SandboxRuntimeException(
```

## Snippet 179
Lines 2258-2262

```Python
if not os.path.isfile(started_marker_path):
                raise self.SandboxRuntimeException(
                    "Sandbox failed to start up properly"
                )
            exit_code_path = os.path.join(self._sandbox_shared_path, "exit_code")
```

## Snippet 180
Lines 2263-2274

```Python
if not os.path.isfile(exit_code_path):
                raise self.SandboxRuntimeException(
                    "Sandbox failed to record an exit code"
                )
            with open(exit_code_path, "r") as exit_code_f:
                exit_code_str = exit_code_f.read()
            try:
                exit_code = int(exit_code_str.strip())
            except ValueError as e:
                raise self.SandboxRuntimeException(
                    f"Sandbox recorded non-integer exit code: {e}"
                )
```

## Snippet 181
Lines 2275-2283

```Python
if exit_code != 0:
                raise self.CodeExecutionError(
                    code=self._code,
                    returncode=exit_code,
                    cmd=self._sandboxed_command,
                    output=result.stdout,
                    stderr=result.stderr,
                )
            return result
```

## Snippet 182
Lines 2288-2294

```Python
def run(self) -> subprocess.CompletedProcess:
        """
        Set up and run the sandbox in a separate process.

        :return: A `CompletedProcess` object representing the return code and stdout/stderr of the code interpreter.
        :raises FixableException: If an issue occurs but that can be fixed by the user.
        :raises Sandbox.SandboxRuntimeException: If the sandbox failed to start or behaved incorrectly regardless of the code being evaluated.
```

## Snippet 183
Lines 2295-2314

```Python
:raises Sandbox.ExecutionTimeoutError: If the code interpreter ran for longer than configured.
        :raises Sandbox.InterruptedExecutionError: If the code interpreter died without providing a return code; usually due to running over resource limits.
        :raises sandbox.CodeExecutionError: If the code interpreter failed to execute the given code. This does not represent a sandbox failure.
        """
        reexec_path = os.path.join(self._tmp_dir, "self.py")
        with open(reexec_path, "w") as reexec_f:
            reexec_f.write(self._SelfFile.contents())
        new_env = os.environ.copy()
        new_env[self._MARKER_ENVIRONMENT_VARIABLE] = "1"
        data = json.dumps({"settings": self._settings})
        try:
            result = subprocess.run(
                (sys.executable, reexec_path),
                env=new_env,
                input=data,
                text=True,
                capture_output=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
```

## Snippet 184
Lines 2317-2326

```Python
if not result.stdout:
                raise self.SandboxRuntimeException(
                    f"Subprocess interpreter did not produce any output (stderr: {result.stderr})"
                )
            try:
                output = json.loads(result.stdout)
            except json.decoder.JSONDecodeError as e:
                raise self.SandboxRuntimeException(
                    f"Subprocess interpreter produced invalid JSON (stdout: {result.stdout}): {e}"
                )
```

## Snippet 185
Lines 2330-2341

```Python
for ex_class in (
                    self.PlatformNotSupportedException,
                    self.SandboxRuntimeException,
                    self.CodeExecutionError,
                    self.ExecutionTimeoutError,
                    self.InterruptedExecutionError,
                    self.GVisorNotInstalledException,
                    self.CorruptDownloadException,
                    self.EnvironmentNeedsSetupException,
                    self.ExecutionError,
                    self.SandboxException,
                ):
```

## Snippet 186
Lines 2345-2350

```Python
if found_class is None:
                    exception_str = output["exception"]["str"]
                    raise self.SandboxException(f"{class_name}: {exception_str}")
                raise found_class(
                    *output["exception"]["args"], **output["exception"]["kwargs"]
                )
```

## Snippet 187
Lines 2351-2365

```Python
if "result" not in output:
                raise self.SandboxException(
                    f"Invalid response from subprocess: {output}"
                )
            return subprocess.CompletedProcess(
                args=output["result"]["args"],
                returncode=output["result"]["returncode"],
                stdout=base64.b64decode(output["result"]["stdout"]).decode(
                    "utf-8", errors="replace"
                ),
                stderr=base64.b64decode(output["result"]["stderr"]).decode(
                    "utf-8", errors="replace"
                ),
            )
```

## Snippet 188
Lines 2366-2372

```Python
def debug_logs(self, write_fn: typing.Callable[[str, str], typing.Any]):
        """
        Write debug logs and other system information to the given function.

        May only be called after `run` returns, but may be called even when
        `run` fails.
```

## Snippet 189
Lines 2373-2376

```Python
:param write_fn: A function that takes (filename, log line) as arguments.
        """
        log_paths = []
        all_logs = []
```

## Snippet 190
Lines 2382-2385

```Python
else:
            all_logs.append(
                (
                    "[meta]",
```

## Snippet 191
Lines 2399-2401

```Python
while f"{log_filename}.{runsc_filename_suffix}" in runsc_filenames:
                        runsc_filename_suffix += 1
                    log_filename = f"{log_filename}.{runsc_filename_suffix}"
```

## Snippet 192
Lines 2415-2420

```Python
for cmd in self._EXTRA_DEBUG_LOG_COMMANDS:
            cmd_str = "`" + " ".join(cmd) + "`"
            try:
                result = subprocess.run(cmd, capture_output=True, timeout=1, check=True)
            except subprocess.CalledProcessError as e:
                all_logs.append(
```

## Snippet 193
Lines 2423-2425

```Python
except Exception as e:
                all_logs.append((cmd_str, f"Failed: {e}"))
            else:
```

## Snippet 194
Lines 2428-2430

```Python
if not line:
                        continue
                    all_logs.append((cmd_str, line.decode("utf-8", errors="replace")))
```

## Snippet 195
Lines 2440-2451

```Python
Check for updates.
    """

    RELEASES_URL = "https://github.com/EtiennePerot/safe-code-execution/releases.atom"
    USER_URL = "https://github.com/EtiennePerot/safe-code-execution/"
    ENABLED = True
    SELF_VERSION = None
    LAST_UPDATE_CHECK = None
    LAST_UPDATE_CACHE = None
    UPDATE_CHECK_INTERVAL = datetime.timedelta(days=3)
    VERSION_REGEX = re.compile(r"<title>\s*(v?\d+(?:\.\d+)+)\s*</title>")
```

## Snippet 196
Lines 2481-2484

```Python
if not cls.ENABLED:
            return
        with open(file_with_frontmatter, "rb") as f:
            contents = f.read().decode("ascii").strip()
```

## Snippet 197
Lines 2485-2490

```Python
if not contents.startswith('"""'):
            raise cls.VersionCheckError(
                f"Malformed file contents: {contents[:min(8, len(contents))]}[...]"
            )
        contents = contents[len('"""') :].strip()
        version = None
```

## Snippet 198
Lines 2501-2504

```Python
if version is None:
            raise cls.VersionCheckError("Version metadata not found")
        cls.SELF_VERSION = cls._parse_version(version)
```

## Snippet 199
Lines 2506-2511

```Python
def _get_current_version(cls):
        assert (
            cls.SELF_VERSION is not None
        ), "UpdateCheck.init_from_frontmatter must be called first."
        return cls.SELF_VERSION
```

## Snippet 200
Lines 2514-2519

```Python
if cls.LAST_UPDATE_CHECK is None:
            return True
        return (
            datetime.datetime.now() - cls.LAST_UPDATE_CHECK >= cls.UPDATE_CHECK_INTERVAL
        )
```

## Snippet 201
Lines 2523-2525

```Python
if type(cls.LAST_UPDATE_CACHE) is type(()):
                return cls.LAST_UPDATE_CACHE
            raise cls.LAST_UPDATE_CACHE
```

## Snippet 202
Lines 2526-2530

```Python
try:
            try:
                releases_xml = urllib.request.urlopen(url=cls.RELEASES_URL).read()
            except urllib.error.HTTPError as e:
                cls.LAST_UPDATE_CACHE = cls.VersionCheckError(
```

## Snippet 203
Lines 2539-2545

```Python
if latest_version is None:
                cls.LAST_UPDATE_CACHE = cls.VersionCheckError(
                    f"Failed to retrieve latest version: no release found (URL: {cls.RELEASES_URL})"
                )
                raise cls.LAST_UPDATE_CACHE
            cls.LAST_UPDATE_CACHE = latest_version
            return latest_version
```

## Snippet 204
Lines 2557-2566

```Python
if not cls.ENABLED:
            return None
        try:
            current_version = cls._get_current_version()
        except cls.VersionCheckError as e:
            raise e.__class__(f"Checking current version: {e}")
        try:
            latest_version = cls._get_latest_version()
        except cls.VersionCheckError as e:
            raise e.__class__(f"Checking latest version: {e}")
```

## Snippet 205
Lines 2567-2569

```Python
if cls._compare(current_version, latest_version) == -1:
            return cls._format_version(latest_version)
        return None
```

## Snippet 206
Lines 2575-2590

```Python
_SAMPLE_BASH_INSTRUCTIONS = (
    "echo 'Hello from the sandbox!'",
    "date",
    "dmesg",
    "echo 'Bye from the sandbox!'",
)

_SAMPLE_PYTHON_INSTRUCTIONS = (
    "print('Hello from the sandbox!')",
    "import datetime, sys",
    "print('Current date and time:', datetime.datetime.now())",
    "sys.stdout.flush()",
    "import shutil, subprocess",
    "subprocess.run([shutil.which('dmesg')], check=True)",
    "print('Bye from the sandbox!')",
)
```

## Snippet 207
Lines 2593-2628

```Python
def _do_self_tests(debug):
    _self_tests = (
        {
            "name": "simple_python",
            "language": "python",
            "code": _SAMPLE_PYTHON_INSTRUCTIONS,
            "debug": True,
            "status": "OK",
        },
        {
            "name": "simple_bash",
            "language": "bash",
            "code": _SAMPLE_BASH_INSTRUCTIONS,
            "debug": True,
            "status": "OK",
        },
        {
            "name": "bad_syntax_python",
            "language": "python",
            "code": ("print('foo",),
            "debug": True,
            "status": "ERROR",
        },
        {
            "name": "bad_syntax_bash",
            "language": "bash",
            "code": ("echo 'foo",),
            "debug": True,
            "status": "ERROR",
        },
        {
            "name": "long_running_code",
            "language": "python",
            "code": (
                "import time",
                "time.sleep(15)",
```

## Snippet 208
Lines 2630-2634

```Python
),
            "valves": {
                "MAX_RUNTIME_SECONDS": 5,
            },
            "status": "TIMEOUT",
```

## Snippet 209
Lines 2635-2642

```Python
},
        {
            "name": "ram_hog",
            "language": "python",
            "code": (
                "import time",
                "f = open('/dev/urandom', 'rb')",
                "s = []",
```

## Snippet 210
Lines 2647-2651

```Python
),
            "valves": {
                "MAX_RAM_MEGABYTES": 128,
            },
            "status": "INTERRUPTED",
```

## Snippet 211
Lines 2666-2672

```Python
for self_test in _self_tests:
        name = self_test["name"]
        language = self_test["language"]
        code = "\n".join(self_test["code"]) + "\n"
        want_status = self_test["status"]
        valves = self_test.get("valves", {})
        test_env = os.environ.copy()
```

## Snippet 212
Lines 2673-2682

```Python
for valve_name, valve_value in valves.items():
            test_env[
                _Tools.Valves()._VALVE_OVERRIDE_ENVIRONMENT_VARIABLE_NAME_PREFIX
                + valve_name
            ] = str(valve_value)
        test_argv = [
            sys.executable,
            os.path.abspath(__file__),
            f"--language={language}",
        ]
```

## Snippet 213
Lines 2683-2699

```Python
if debug or self_test.get("debug", False):
            test_argv.append("--debug")
        print(f"\u23f3 Running self-test: {name}", file=sys.stderr)
        try:
            result = subprocess.run(
                test_argv,
                env=test_env,
                input=code,
                text=True,
                capture_output=True,
                timeout=20,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            success = False
            _print_output(e)
            print(
```

## Snippet 214
Lines 2709-2715

```Python
else:
            try:
                result_data = json.loads(result.stdout)
            except json.decoder.JSONDecodeError as e:
                _print_output(result)
                success = False
                print(
```

## Snippet 215
Lines 2721-2724

```Python
if got_status != want_status:
                    _print_output(result)
                    success = False
                    print(
```

## Snippet 216
Lines 2732-2738

```Python
if success:
        print("\u2705 All tool self-tests passed, good go to!", file=sys.stderr)
        sys.exit(0)
    else:
        print("\u2620 One or more tool self-tests failed.", file=sys.stderr)
        sys.exit(1)
    assert False, "Unreachable"
```

## Snippet 217
Lines 2742-2755

```Python
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run arbitrary code in a gVisor sandbox."
    )
    parser.add_argument(
        "--language",
        choices=("python", "bash"),
        default="python",
        help="Language of the code to run.",
    )
    parser.add_argument(
        "--use_sample_code",
        action="store_true",
        default=False,
```

## Snippet 218
Lines 2757-2774

```Python
)
    parser.add_argument(
        "--self_test",
        action="store_true",
        default=False,
        help="Run series of self-tests.",
    )
    parser.add_argument(
        "--debug", action="store_true", default=False, help="Enable debug mode."
    )
    parser.add_argument(
        "--want_status",
        type=str,
        default="",
        help="If set, verify that the code evaluation status matches this or exit with error code.",
    )
    args = parser.parse_args()
```

## Snippet 219
Lines 2775-2779

```Python
if args.debug:
        os.environ[
            _Tools.Valves()._VALVE_OVERRIDE_ENVIRONMENT_VARIABLE_NAME_PREFIX + "DEBUG"
        ] = "true"
```

## Snippet 220
Lines 2784-2787

```Python
if args.language == "bash":
            code = "\n".join(_SAMPLE_BASH_INSTRUCTIONS) + "\n"
        else:
            code = "\n".join(_SAMPLE_PYTHON_INSTRUCTIONS) + "\n"
```

## Snippet 221
Lines 2797-2804

```Python
if args.language == "bash":
            output_str = await tools.run_bash_command(
                bash_command=code, __event_emitter__=_dummy_emitter
            )
        else:
            output_str = await tools.run_python_code(
                python_code=code, __event_emitter__=_dummy_emitter
            )
```

## Snippet 222
Lines 2805-2807

```Python
if args.want_status:
            output = json.loads(output_str)
            got_status = output["status"]
```

