# Code Snippets from toollama/API/api-tools/tools/time/calculator.py

File: `toollama/API/api-tools/tools/time/calculator.py`  
Language: Python  
Extracted: 2025-06-07 05:19:27  

## Snippet 1
Lines 1-7

```Python
"""Time calculation tool for the MoE system."""

from datetime import datetime, timedelta
import pytz
from typing import Dict, Any, Optional, Callable, Awaitable, List, Union
from ..base import BaseTool
```

## Snippet 2
Lines 11-14

```Python
def __init__(self, credentials: Dict[str, str] = None):
        super().__init__(credentials)  # No credentials needed
        self.timezones = pytz.all_timezones
```

## Snippet 3
Lines 15-34

```Python
async def execute(
        self,
        operation: str,
        time1: str,
        time2: Optional[str] = None,
        timezone1: Optional[str] = "UTC",
        timezone2: Optional[str] = None,
        __user__: dict = {},
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None
    ) -> str:
        """
        Execute time calculations.

        Args:
            operation: Operation to perform (convert, difference, add, subtract)
            time1: First time value
            time2: Second time value (optional)
            timezone1: First timezone
            timezone2: Second timezone (optional)
            __user__: User context
```

## Snippet 4
Lines 37-41

```Python
Returns:
            Calculation result
        """
        await self.emit_event(
            "status",
```

## Snippet 5
Lines 54-67

```Python
elif operation == "subtract":
                result = self._subtract_time(time1, time2, timezone1)
            else:
                raise ValueError(f"Unknown operation: {operation}")

            await self.emit_event(
                "status",
                "Calculation completed",
                True,
                __event_emitter__
            )

            return result
```

## Snippet 6
Lines 68-77

```Python
except Exception as e:
            error_msg = f"Error in time calculation: {str(e)}"
            await self.emit_event(
                "status",
                error_msg,
                True,
                __event_emitter__
            )
            return error_msg
```

## Snippet 7
Lines 78-91

```Python
def _convert_timezone(self, time_str: str, from_tz: str, to_tz: str) -> str:
        """Convert time between timezones."""
        try:
            # Parse input time
            dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")

            # Add source timezone
            source_tz = pytz.timezone(from_tz)
            dt = source_tz.localize(dt)

            # Convert to target timezone
            target_tz = pytz.timezone(to_tz)
            converted = dt.astimezone(target_tz)
```

## Snippet 8
Lines 94-98

```Python
except ValueError:
            raise ValueError("Invalid time format. Use YYYY-MM-DD HH:MM:SS")
        except pytz.exceptions.UnknownTimeZoneError:
            raise ValueError("Invalid timezone")
```

## Snippet 9
Lines 99-118

```Python
def _calculate_difference(self, time1: str, time2: str, timezone: str) -> str:
        """Calculate time difference."""
        try:
            # Parse times
            dt1 = datetime.strptime(time1, "%Y-%m-%d %H:%M:%S")
            dt2 = datetime.strptime(time2, "%Y-%m-%d %H:%M:%S")

            # Add timezone
            tz = pytz.timezone(timezone)
            dt1 = tz.localize(dt1)
            dt2 = tz.localize(dt2)

            # Calculate difference
            diff = abs(dt2 - dt1)

            days = diff.days
            hours = diff.seconds // 3600
            minutes = (diff.seconds % 3600) // 60
            seconds = diff.seconds % 60
```

## Snippet 10
Lines 124-134

```Python
def _add_time(self, time_str: str, duration: str, timezone: str) -> str:
        """Add duration to time."""
        try:
            # Parse base time
            dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            tz = pytz.timezone(timezone)
            dt = tz.localize(dt)

            # Parse duration (format: XdYhZm)
            days = hours = minutes = 0
```

## Snippet 11
Lines 135-137

```Python
if 'd' in duration:
                days = int(duration.split('d')[0])
                duration = duration.split('d')[1]
```

## Snippet 12
Lines 138-140

```Python
if 'h' in duration:
                hours = int(duration.split('h')[0])
                duration = duration.split('h')[1]
```

## Snippet 13
Lines 141-146

```Python
if 'm' in duration:
                minutes = int(duration.split('m')[0])

            # Add duration
            result = dt + timedelta(days=days, hours=hours, minutes=minutes)
```

## Snippet 14
Lines 152-162

```Python
def _subtract_time(self, time_str: str, duration: str, timezone: str) -> str:
        """Subtract duration from time."""
        try:
            # Parse base time
            dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            tz = pytz.timezone(timezone)
            dt = tz.localize(dt)

            # Parse duration (format: XdYhZm)
            days = hours = minutes = 0
```

## Snippet 15
Lines 163-165

```Python
if 'd' in duration:
                days = int(duration.split('d')[0])
                duration = duration.split('d')[1]
```

## Snippet 16
Lines 166-168

```Python
if 'h' in duration:
                hours = int(duration.split('h')[0])
                duration = duration.split('h')[1]
```

## Snippet 17
Lines 169-174

```Python
if 'm' in duration:
                minutes = int(duration.split('m')[0])

            # Subtract duration
            result = dt - timedelta(days=days, hours=hours, minutes=minutes)
```

