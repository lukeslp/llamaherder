# Code Snippets from toollama/API/api-tools/tools/time/time_calculator.py

File: `toollama/API/api-tools/tools/time/time_calculator.py`  
Language: Python  
Extracted: 2025-06-07 05:19:05  

## Snippet 1
Lines 1-12

```Python
"""
Time and Calculation tools combining timezone conversion and mathematical operations
Enhanced with accessibility features and improved formatting
"""

import pytz
import dateparser
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union, List
from pydantic import BaseModel, Field
```

## Snippet 2
Lines 13-15

```Python
def _parse_time(time_str: str, source_tz: Optional[str] = None) -> datetime:
    """Parse time string with timezone support"""
    settings = {}
```

## Snippet 3
Lines 16-19

```Python
if source_tz:
        settings['TIMEZONE'] = source_tz

    parsed = dateparser.parse(time_str, settings=settings)
```

## Snippet 4
Lines 20-23

```Python
if not parsed:
        raise ValueError(f"Could not parse time string: {time_str}")
    return parsed
```

## Snippet 5
Lines 26-29

```Python
if format_str:
        return dt.strftime(format_str)
    return dt.strftime("%Y-%m-%d %H:%M:%S %Z")
```

## Snippet 6
Lines 30-32

```Python
def _convert_timezone(dt: datetime, target_tz: str) -> datetime:
    """Convert datetime to target timezone"""
    target_timezone = pytz.timezone(target_tz)
```

## Snippet 7
Lines 33-36

```Python
if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    return dt.astimezone(target_timezone)
```

## Snippet 8
Lines 37-44

```Python
def _calculate_time_difference(
    time1: datetime,
    time2: datetime,
    unit: str = "seconds"
) -> float:
    """Calculate time difference in specified unit"""
    diff = abs(time2 - time1)
```

## Snippet 9
Lines 51-55

```Python
elif unit == "days":
        return diff.days + (diff.seconds / 86400)
    else:
        raise ValueError(f"Unsupported time unit: {unit}")
```

## Snippet 10
Lines 56-78

```Python
def _evaluate_expression(expression: str) -> float:
    """Safely evaluate mathematical expression"""
    # Define allowed mathematical functions
    safe_dict = {
        'abs': abs,
        'round': round,
        'min': min,
        'max': max,
        'pow': pow,
        'sum': sum,
        'len': len,
        # NumPy functions
        'sin': np.sin,
        'cos': np.cos,
        'tan': np.tan,
        'exp': np.exp,
        'log': np.log,
        'sqrt': np.sqrt,
        'pi': np.pi,
        'e': np.e
    }

    try:
```

## Snippet 11
Lines 79-82

```Python
# Replace '^' with '**' for exponentiation
        expression = expression.replace('^', '**')
        # Evaluate the expression using the safe dictionary
        return float(eval(expression, {"__builtins__": {}}, safe_dict))
```

## Snippet 12
Lines 89-91

```Python
class Valves(BaseModel):
        DEFAULT_TIMEZONE: str = Field(
            default="UTC",
```

## Snippet 13
Lines 93-99

```Python
)
        TIME_FORMAT: str = Field(
            default="%Y-%m-%d %H:%M:%S %Z",
            description="Default time format string"
        )
        ROUND_DIGITS: int = Field(
            default=6,
```

## Snippet 14
Lines 106-145

```Python
def convert_time(
        self,
        time: str,
        source_timezone: Optional[str] = None,
        target_timezone: str = "UTC",
        format: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Convert time between timezones with enhanced formatting options.

        :param time: Time string to convert
        :param source_timezone: Source timezone (optional)
        :param target_timezone: Target timezone
        :param format: Output format string (optional)
        :return: Dictionary with conversion results
        """
        try:
            # Parse input time
            dt = _parse_time(time, source_timezone)

            # Convert to target timezone
            converted = _convert_timezone(dt, target_timezone)

            # Format output
            format_str = format or self.valves.TIME_FORMAT
            return {
                "status": "success",
                "data": {
                    "original": _format_time(dt, format_str),
                    "converted": _format_time(converted, format_str),
                    "source_timezone": str(dt.tzinfo),
                    "target_timezone": target_timezone
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
```

## Snippet 15
Lines 146-157

```Python
def calculate_time_difference(
        self,
        time1: str,
        time2: str,
        unit: str = "seconds",
        timezone: Optional[str] = None
    ) -> Dict[str, Union[str, float]]:
        """
        Calculate time difference between two timestamps.

        :param time1: First time string
        :param time2: Second time string
```

## Snippet 16
Lines 159-184

```Python
:param timezone: Timezone for parsing times (optional)
        :return: Dictionary with calculation results
        """
        try:
            # Parse input times
            dt1 = _parse_time(time1, timezone)
            dt2 = _parse_time(time2, timezone)

            # Calculate difference
            difference = _calculate_time_difference(dt1, dt2, unit)

            return {
                "status": "success",
                "data": {
                    "time1": _format_time(dt1),
                    "time2": _format_time(dt2),
                    "difference": round(difference, self.valves.ROUND_DIGITS),
                    "unit": unit
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
```

## Snippet 17
Lines 185-190

```Python
def evaluate_math(
        self,
        expression: str,
        variables: Optional[Dict[str, float]] = None
    ) -> Dict[str, Union[str, float]]:
        """
```

## Snippet 18
Lines 191-197

```Python
Evaluate mathematical expression with support for variables and functions.

        :param expression: Mathematical expression to evaluate
        :param variables: Dictionary of variable values (optional)
        :return: Dictionary with evaluation results
        """
        try:
```

## Snippet 19
Lines 203-213

```Python
# Evaluate expression
            result = _evaluate_expression(expression)

            return {
                "status": "success",
                "data": {
                    "expression": expression,
                    "result": round(result, self.valves.ROUND_DIGITS),
                    "variables": variables or {}
                }
            }
```

## Snippet 20
Lines 214-219

```Python
except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
```

## Snippet 21
Lines 220-233

```Python
def get_current_time(
        self,
        timezone: Optional[str] = None,
        format: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Get current time in specified timezone and format.

        :param timezone: Target timezone (optional)
        :param format: Output format string (optional)
        :return: Dictionary with current time
        """
        try:
            now = datetime.now(pytz.UTC)
```

## Snippet 22
Lines 234-244

```Python
if timezone:
                now = _convert_timezone(now, timezone)

            format_str = format or self.valves.TIME_FORMAT
            return {
                "status": "success",
                "data": {
                    "current_time": _format_time(now, format_str),
                    "timezone": str(now.tzinfo)
                }
            }
```

## Snippet 23
Lines 245-250

```Python
except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
```

## Snippet 24
Lines 251-254

```Python
def list_timezones(self, filter: Optional[str] = None) -> Dict[str, List[str]]:
        """
        List available timezones with optional filtering.
```

## Snippet 25
Lines 255-259

```Python
:param filter: Filter string for timezone names (optional)
        :return: Dictionary with matching timezone names
        """
        try:
            zones = pytz.all_timezones
```

## Snippet 26
Lines 263-268

```Python
return {
                "status": "success",
                "data": {
                    "timezones": zones
                }
            }
```

## Snippet 27
Lines 269-273

```Python
except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
```

