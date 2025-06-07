# Code Snippets from toollama/soon/tools_pending/unprocessed/dev_eOpenStreetMap.py

File: `toollama/soon/tools_pending/unprocessed/dev_eOpenStreetMap.py`  
Language: Python  
Extracted: 2025-06-07 05:16:00  

## Snippet 1
Lines 1-37

```Python
"""
title: OpenStreetMap Tool
author: projectmoon
author_url: https://git.agnos.is/projectmoon/open-webui-filters
version: 2.2.1
license: AGPL-3.0+
required_open_webui_version: 0.4.3
requirements: openrouteservice, pygments
"""
import itertools
import json
import math
import requests

from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import HtmlFormatter

import openrouteservice
from openrouteservice.directions import directions as ors_directions

from urllib.parse import urljoin
from operator import itemgetter
from typing import List, Optional
from pydantic import BaseModel, Field

# Yoinked from the OpenWebUI CSS
FONTS = ",".join([
    "-apple-system", "BlinkMacSystemFont", "Inter",
    "ui-sans-serif", "system-ui", "Segoe UI",
    "Roboto", "Ubuntu", "Cantarell", "Noto Sans",
    "sans-serif", "Helvetica Neue", "Arial",
    "\"Apple Color Emoji\"", "\"Segoe UI Emoji\"",
    "Segoe UI Symbol", "\"Noto Color Emoji\""
])

FONT_CSS = f"""
```

## Snippet 2
Lines 40-83

```Python
@media (prefers-color-scheme: dark) {{
  html {{
    --tw-text-opacity: 1;
    color: rgb(227 227 227 / var(--tw-text-opacity));
  }}
}}
"""

HIGHLIGHT_CSS = HtmlFormatter().get_style_defs('.highlight')

NOMINATIM_LOOKUP_TYPES = {
    "node": "N",
    "route": "R",
    "way": "W"
}

OLD_VALVE_SETTING = """ Tell the user that you cannot search
OpenStreetMap until the configuration is fixed. The Nominatim URL
valve setting needs to be updated. There has been a breaking change in
1.0 of the OpenStreetMap tool. The valve setting is currently set to:
`{OLD}`.

It shoule be set to the root URL of the Nominatim endpoint, for
example:

`https://nominatim.openstreetmap.org/`

Inform the user they need to fix this configuration setting.
""".replace("\n", " ").strip()

VALVES_NOT_SET = """
Tell the user that the User-Agent and From headers
must be set to comply with the OSM Nominatim terms
of use: https://operations.osmfoundation.org/policies/nominatim/
""".replace("\n", " ").strip()

NO_RESULTS = ("No results found. Tell the user you found no results. "
              "Do not make up answers or hallucinate. Only say you "
              "found no results.")

NO_RESULTS_BAD_ADDRESS = ("No results found. Tell the user you found no results because "
                          "OpenStreetMap could not resolve the address. "
                          "Print the exact address or location you searched for. "
                          "Suggest to the user that they refine their "
```

## Snippet 3
Lines 97-105

```Python
# Give examples of OSM links to help prevent wonky generated links
# with correct GPS coords but incorrect URLs.
EXAMPLE_OSM_LINK = "https://www.openstreetmap.org/#map=19/<lat>/<lon>"
OSM_LINK_INSTRUCTIONS = (
    "Make friendly human-readable OpenStreetMap links when possible, "
    "by using the latitude and longitude of the amenities: "
    f"{EXAMPLE_OSM_LINK}\n\n"
)
```

## Snippet 4
Lines 106-111

```Python
def chunk_list(input_list, chunk_size):
    it = iter(input_list)
    return list(
        itertools.zip_longest(*[iter(it)] * chunk_size, fillvalue=None)
    )
```

## Snippet 5
Lines 117-119

```Python
def specific_place_instructions() -> str:
    return (
        "# Result Instructions\n"
```

## Snippet 6
Lines 120-124

```Python
"These are search results ordered by relevance for the "
        "address, place, landmark, or location the user is asking "
        "about. **IMPORTANT!:** Tell the user all relevant information, "
        "including address, contact information, and the OpenStreetMap link. "
        "Make the map link into a nice human-readable markdown link."
```

## Snippet 7
Lines 127-130

```Python
def navigation_instructions(travel_type) -> str:
    return (
        "# Result Instructions\n"
        "This is the navigation route that the user has requested. "
```

## Snippet 8
Lines 141-145

```Python
Produce detailed instructions for models good at following
    detailed instructions.
    """
    return (
        "# Detailed Search Result Instructions\n"
```

## Snippet 9
Lines 146-166

```Python
f"These are some of the {tag_type_str} points of interest nearby. "
        "These are the results known to be closest to the requested location. "
        "When telling the user about them, make sure to report "
        "all the information (address, contact info, website, etc).\n\n"
        "Tell the user about ALL the results, and give closer results "
        "first. Closer results are higher in the list. When telling the "
        "user the distance, use the TRAVEL DISTANCE. Do not say one "
        "distance is farther away than another. Just say what the "
        "distances are. "
        f"{OSM_LINK_INSTRUCTIONS}"
        "Give map links friendly, contextual labels. Don't just print "
        f"the naked link:\n"
        f' - Example: You can view it on [OpenStreetMap]({EXAMPLE_OSM_LINK})\n'
        f' - Example: Here it is on [OpenStreetMap]({EXAMPLE_OSM_LINK})\n'
        f' - Example: You can find it on [OpenStreetMap]({EXAMPLE_OSM_LINK})\n'
        "\n\nAnd so on.\n\n"
        "Only use relevant results. If there are no relevant results, "
        "say so. Do not make up answers or hallucinate. "
        f"\n\n{NO_CONFUSION}\n\n"
        "Remember that the CLOSEST result is first, and you should use "
        "that result first.\n\n"
```

## Snippet 10
Lines 173-177

```Python
Produce simpler markdown-oriented instructions for models that do
    better with that.
    """
    return (
        "# OpenStreetMap Result Instructions\n"
```

## Snippet 11
Lines 178-192

```Python
f"These are some of the {tag_type_str} points of interest nearby. "
        "These are the results known to be closest to the requested location. "
        "For each result, report the following information: \n"
        " - Name\n"
        " - Address\n"
        " - OpenStreetMap Link (make it a human readable link like 'View on OpenStreetMap')\n"
        " - Contact information (address, phone, website, email, etc)\n\n"
        "Tell the user about ALL the results, and give the CLOSEST result "
        "first. The results are ordered by closeness as the crow flies. "
        "When telling the user about distances, use the TRAVEL DISTANCE only. "
        "Only use relevant results. If there are no relevant results, "
        "say so. Do not make up answers or hallucinate. "
        "Make sure that your results are in the actual location the user is talking about, "
        "and not a place of the same name in a different country."
        "The search results are below."
```

## Snippet 12
Lines 200-211

```Python
if 'address' not in nominatim_result:
        return None

    nominatim_address = nominatim_result['address']

    # prioritize actual name, road name, then display name. display
    # name is often the full address, which is a bit much.
    nominatim_name = nominatim_result.get('name')
    nominatim_road = nominatim_address.get('road')
    nominatim_display_name = nominatim_result.get('display_name')
    thing_name = thing.get('name')
```

## Snippet 13
Lines 216-220

```Python
elif nominatim_display_name and not thing_name:
        thing['name'] = nominatim_display_name.strip()

    tags = thing.get('tags', {})
```

## Snippet 14
Lines 229-234

```Python
def pretty_print_thing_json(thing):
    """Converts an OSM thing to nice JSON HTML."""
    formatted_json_str = json.dumps(thing, indent=2)
    lexer = JsonLexer()
    formatter = HtmlFormatter(style='colorful')
    return highlight(formatted_json_str, lexer, formatter)
```

## Snippet 15
Lines 241-259

```Python
(usually) has at least a name. Some exceptions are made for ways
    that do not have names.
    """
    tags = thing.get('tags', {})
    has_tags = len(tags) > 1
    has_useful_tags = (
        'leisure' in tags or
        'shop' in tags or
        'amenity' in tags or
        'car:rental' in tags or
        'rental' in tags or
        'car_rental' in tags or
        'service:bicycle:rental' in tags or
        'tourism' in tags
    )

    # there can be a lot of artwork in city centers. drop ones that
    # aren't as notable. we define notable by the thing having wiki
    # entries, or by being tagged as historical.
```

## Snippet 16
Lines 260-269

```Python
if tags.get('tourism', '') == 'artwork':
        notable = (
            'wikipedia' in tags or
            'wikimedia_commons' in tags
        )
    else:
        notable = True

    return has_tags and has_useful_tags and notable
```

## Snippet 17
Lines 271-275

```Python
has_name = any('name' in tag for tag in thing['tags'])
    return thing_is_useful(thing) and has_name
    # is_exception = way['tags'].get('leisure', None) is not None
    # return has_tags and (has_name or is_exception)
```

## Snippet 18
Lines 276-281

```Python
def process_way_result(way) -> Optional[dict]:
    """
    Post-process an OSM Way dict to remove the geometry and node
    info, and calculate a single GPS coordinate from its bounding
    box.
    """
```

## Snippet 19
Lines 288-296

```Python
if 'bounds' in way:
        way_center = get_bounding_box_center(way['bounds'])
        way['lat'] = way_center['lat']
        way['lon'] = way_center['lon']
        del way['bounds']
        return way

    return None
```

## Snippet 20
Lines 301-310

```Python
min_lat = convert(bbox, 'minlat')
    min_lon = convert(bbox, 'minlon')
    max_lat = convert(bbox, 'maxlat')
    max_lon = convert(bbox, 'maxlon')

    return {
        'lon': (min_lon + max_lon) / 2,
        'lat': (min_lat + max_lat) / 2
    }
```

## Snippet 21
Lines 311-325

```Python
def haversine_distance(point1, point2):
    R = 6371  # Earth radius in kilometers

    lat1, lon1 = point1['lat'], point1['lon']
    lat2, lon2 = point2['lat'], point2['lon']

    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) * math.sin(d_lat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) * math.sin(d_lon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c
```

## Snippet 22
Lines 329-332

```Python
The origin is a dict with keys of { lat, lon }.
    """
    return sorted(points, key=itemgetter(*keys))
```

## Snippet 23
Lines 355-357

```Python
def get_or_none(tags: dict, *keys: str) -> Optional[str]:
    """
    Try to extract a value from a dict by trying keys in order, or
```

## Snippet 24
Lines 377-381

```Python
if shop_type == "doityourself":
        return "hardware"
    else:
        return shop_type
```

## Snippet 25
Lines 382-386

```Python
def parse_thing_address(thing: dict) -> Optional[str]:
    """
    Parse address from either an Overpass result or Nominatim
    result.
    """
```

## Snippet 26
Lines 387-392

```Python
if 'address' in thing:
        # nominatim result
        return parse_address_from_address_obj(thing['address'])
    else:
        return parse_address_from_tags(thing['tags'])
```

## Snippet 27
Lines 393-400

```Python
def parse_address_from_address_obj(address) -> Optional[str]:
    """Parse address from Nominatim address object."""
    house_number = get_or_none(address, "house_number")
    street = get_or_none(address, "road")
    city = get_or_none(address, "city")
    state = get_or_none(address, "state")
    postal_code = get_or_none(address, "postcode")
```

## Snippet 28
Lines 402-406

```Python
if all_are_none(house_number, street, city, state, postal_code):
        return None

    # Handle missing values to create complete-ish addresses, even if
    # we have missing data. We will get either a partly complete
```

## Snippet 29
Lines 407-413

```Python
# address, or None if all the values are missing.
    line1 = filter(None, [street, house_number])
    line2 = filter(None, [city, state, postal_code])
    line1 = " ".join(line1).strip()
    line2 = " ".join(line2).strip()
    full_address = filter(None, [line1, line2])
    full_address = ", ".join(full_address).strip()
```

## Snippet 30
Lines 416-427

```Python
def parse_address_from_tags(tags: dict) -> Optional[str]:
    """Parse address from Overpass tags object."""
    house_number = get_or_none(tags, "addr:housenumber", "addr:house_number")
    street = get_or_none(tags, "addr:street")
    city = get_or_none(tags, "addr:city")
    state = get_or_none(tags, "addr:state", "addr:province")
    postal_code = get_or_none(
        tags,
        "addr:postcode", "addr:post_code", "addr:postal_code",
        "addr:zipcode", "addr:zip_code"
    )
```

## Snippet 31
Lines 429-433

```Python
if all_are_none(house_number, street, city, state, postal_code):
        return None

    # Handle missing values to create complete-ish addresses, even if
    # we have missing data. We will get either a partly complete
```

## Snippet 32
Lines 434-440

```Python
# address, or None if all the values are missing.
    line1 = filter(None, [street, house_number])
    line2 = filter(None, [city, state, postal_code])
    line1 = " ".join(line1).strip()
    line2 = " ".join(line2).strip()
    full_address = filter(None, [line1, line2])
    full_address = ", ".join(full_address).strip()
```

## Snippet 33
Lines 443-447

```Python
def parse_thing_amenity_type(thing: dict, tags: dict) -> Optional[dict]:
    """
    Extract amenity type or other identifying category from
    Nominatim or Overpass result object.
    """
```

## Snippet 34
Lines 451-454

```Python
if thing.get('class') == 'amenity' or thing.get('class') == 'shop':
        return thing.get('type')

    # fall back to tag categories, like shop=*
```

## Snippet 35
Lines 457-461

```Python
if 'leisure' in tags:
        return friendly_shop_name(tags['leisure'])

    return None
```

## Snippet 36
Lines 462-468

```Python
def parse_and_validate_thing(thing: dict) -> Optional[dict]:
    """
    Parse an OSM result (node or post-processed way) and make it
    more friendly to work with. Helps remove ambiguity of the LLM
    interpreting the raw JSON data. If there is not enough data,
    discard the result.
    """
```

## Snippet 37
Lines 469-471

```Python
tags: dict = thing['tags'] if 'tags' in thing else {}

    # Currently we define "enough data" as at least having lat, lon,
```

## Snippet 38
Lines 473-475

```Python
# class of POIs (leisure).
    has_name = 'name' in tags or 'name' in thing
    is_leisure = 'leisure' in tags or 'leisure' in thing
```

## Snippet 39
Lines 479-482

```Python
if not has_name and not is_leisure:
        return None

    friendly_thing = {}
```

## Snippet 40
Lines 489-497

```Python
address: str = parse_thing_address(thing)
    distance: Optional[float] = thing.get('distance', None)
    nav_distance: Optional[float] = thing.get('nav_distance', None)
    opening_hours: Optional[str] = tags.get('opening_hours', None)

    lat: Optional[float] = thing.get('lat', None)
    lon: Optional[float] = thing.get('lon', None)
    amenity_type: Optional[str] = parse_thing_amenity_type(thing, tags)
```

## Snippet 41
Lines 502-506

```Python
if nav_distance:
        friendly_thing['nav_distance'] = "{:.3f}".format(nav_distance) + " km"
    else:
        friendly_thing['nav_distance'] = f"a bit more than {friendly_thing['distance']}km"
```

## Snippet 42
Lines 518-531

```Python
def convert_and_validate_results(
    original_location: str,
    things_nearby: List[dict],
    sort_message: str="closeness",
    use_distance: bool=True
) -> Optional[str]:
    """
    Converts the things_nearby JSON into Markdown-ish results to
    (hopefully) improve model understanding of the results. Intended
    to stop misinterpretation of GPS coordinates when creating map
    links. Also drops incomplete results. Supports Overpass and
    Nominatim results.
    """
    entries = []
```

## Snippet 43
Lines 544-559

```Python
map_link = create_osm_link(friendly_thing['lat'], friendly_thing['lon'])
        entry = (f"## {friendly_thing['name']}\n"
                 f" - Latitude: {friendly_thing['lat']}\n"
                 f" - Longitude: {friendly_thing['lon']}\n"
                 f" - Address: {friendly_thing['address']}\n"
                 f" - Amenity Type: {friendly_thing['amenity_type']}\n"
                 f"{distance}"
                 f"{travel_distance}"
                 f" - OpenStreetMap link: {map_link}\n\n"
                 f"Raw JSON data:\n"
                 "```json\n"
                 f"{str(thing)}\n"
                 "```")

        entries.append(entry)
```

## Snippet 44
Lines 560-564

```Python
if len(entries) == 0:
        return None

    result_text = "\n\n".join(entries)
    header = ("# Search Results\n"
```

## Snippet 45
Lines 570-573

```Python
def __init__(self, filename="/tmp/osm.json"):
        self.filename = filename
        self.data = {}
```

## Snippet 46
Lines 574-580

```Python
# Load existing cache if it exists
        try:
            with open(self.filename, 'r') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            pass
```

## Snippet 47
Lines 584-588

```Python
def set(self, key, value):
        self.data[key] = value
        with open(self.filename, 'w') as f:
            json.dump(self.data, f)
```

## Snippet 48
Lines 591-594

```Python
Retrieve the value from the cache for a given key. If the key is not found,
        call `func_to_call` to generate the value and store it in the cache.

        :param key: The key to look up or set in the cache
```

## Snippet 49
Lines 595-597

```Python
:param func_to_call: A callable function that returns the value if key is missing
        :return: The cached or generated value
        """
```

## Snippet 50
Lines 598-602

```Python
if key not in self.data:
            value = func_to_call()
            self.set(key, value)
        return self.data[key]
```

## Snippet 51
Lines 603-614

```Python
def clear_cache(self):
        """
        Clear all entries from the cache.
        """
        self.data.clear()
        try:
            # Erase contents of the cache file.
            with open(self.filename, 'w'):
                pass
        except FileNotFoundError:
            pass
```

## Snippet 52
Lines 616-623

```Python
def __init__(
            self, valves, user_valves: Optional[dict], event_emitter=None,
    ):
        self.cache = OsmCache()
        self.valves = valves
        self.event_emitter = event_emitter
        self.user_valves = user_valves
```

## Snippet 53
Lines 625-631

```Python
if self.valves.ors_instance is not None:
                self._client = openrouteservice.Client(
                    base_url=self.valves.ors_instance,
                    key=self.valves.ors_api_key
                )
            else:
                self._client = openrouteservice.Client(key=self.valves.ors_api_key)
```

## Snippet 54
Lines 636-640

```Python
def calculate_route(
            self, from_thing: dict, to_thing: dict
    ) -> Optional[dict]:
        """
        Calculate route between A and B. Returns the route,
```

## Snippet 55
Lines 651-661

```Python
if to_thing.get('distance', 9000) <= 1.5:
            profile = "foot-walking"
        else:
            profile = "driving-car"

        coords = ((from_thing['lon'], from_thing['lat']),
                  (to_thing['lon'], to_thing['lat']))

        # check cache first.
        cache_key = f"ors_route_{str(coords)}"
        cached_route = self.cache.get(cache_key)
```

## Snippet 56
Lines 662-669

```Python
if cached_route:
            print("[OSM] Got route from cache!")
            return cached_route

        resp = ors_directions(self._client, coords, profile=profile,
                              preference="fastest", units="km")

        routes = resp.get('routes', [])
```

## Snippet 57
Lines 670-675

```Python
if len(routes) > 0:
            self.cache.set(cache_key, routes[0])
            return routes[0]
        else:
            return None
```

## Snippet 58
Lines 676-680

```Python
def calculate_distance(
            self, from_thing: dict, to_thing: dict
    ) -> Optional[float]:
        """
        Calculate navigation distance between A and B. Returns the
```

## Snippet 59
Lines 684-687

```Python
if not self._client:
            return None

        route = self.calculate_route(from_thing, to_thing)
```

## Snippet 60
Lines 691-696

```Python
def __init__(self, valves, user_valves: Optional[dict], event_emitter=None):
        self.valves = valves
        self.event_emitter = event_emitter
        self.user_valves = user_valves
        self._ors = OrsRouter(valves, user_valves, event_emitter)
```

## Snippet 61
Lines 698-705

```Python
if len(self.valves.user_agent) == 0 or len(self.valves.from_header) == 0:
            return None

        return {
            'User-Agent': self.valves.user_agent,
            'From': self.valves.from_header
        }
```

## Snippet 62
Lines 710-723

```Python
if done:
            message = "OpenStreetMap: resolution complete."
        else:
            message = "OpenStreetMap: resolving..."

        await self.event_emitter({
            "type": "status",
            "data": {
                "status": "in_progress",
                "description": message,
                "done": done,
            },
        })
```

## Snippet 63
Lines 725-736

```Python
if not self.event_emitter or not self.valves.status_indicators:
            return

        await self.event_emitter({
            "type": "status",
            "data": {
                "status": "in_progress",
                "description": message,
                "done": done,
            },
        })
```

## Snippet 64
Lines 737-740

```Python
async def event_searching(
            self, category: str, place: str,
            status: str="in_progress", done: bool=False
    ):
```

## Snippet 65
Lines 741-747

```Python
if not self.event_emitter or not self.valves.status_indicators:
            return

        await self.event_emitter({
            "type": "status",
            "data": {
                "status": status,
```

## Snippet 66
Lines 754-760

```Python
if not self.event_emitter or not self.valves.status_indicators:
            return

        await self.event_emitter({
            "type": "status",
            "data": {
                "status": "complete",
```

## Snippet 67
Lines 766-769

```Python
def create_result_document(self, thing) -> Optional[dict]:
        original_thing = thing
        thing = parse_and_validate_thing(thing)
```

## Snippet 68
Lines 773-777

```Python
if 'address' in original_thing:
            street = get_or_none(original_thing['address'], "road")
        else:
            street = get_or_none(original_thing['tags'], "addr:street")
```

## Snippet 69
Lines 783-787

```Python
addr = f"at {thing['address']}" if thing['address'] != 'unknown' else 'nearby'

        document = (f"<style>{HIGHLIGHT_CSS}</style>"
                    f"<style>{FONT_CSS}</style>"
                    f"<div>"
```

## Snippet 70
Lines 788-797

```Python
f"<p>{thing['name']} is located {addr}.</p>"
                    f"<ul>"
                    f"<li>"
                    f"  <strong>Opening Hours:</strong> {thing['opening_hours']}"
                    f"</li>"
                    f"</ul>"
                    f"<p>Raw JSON data:</p>"
                    f"{json_data}"
                    f"</div>")
```

## Snippet 71
Lines 801-804

```Python
if not self.event_emitter or not self.valves.status_indicators:
            return

        converted = self.create_result_document(thing)
```

## Snippet 72
Lines 805-820

```Python
if not converted:
            return

        source_name = converted["source_name"]
        document = converted["document"]
        osm_link = converted["osm_link"]

        await self.event_emitter({
            "type": "source",
            "data": {
                "document": [document],
                "metadata": [{"source": source_name, "html": True }],
                "source": {"name": source_name, "url": osm_link},
            }
        })
```

## Snippet 73
Lines 822-833

```Python
if not self.event_emitter or not self.valves.status_indicators:
            return

        await self.event_emitter({
            "type": "status",
            "data": {
                "status": "error",
                "description": f"Error searching OpenStreetMap: {str(exception)}",
                "done": True,
            },
        })
```

## Snippet 74
Lines 834-837

```Python
def calculate_navigation_distance(self, start, destination) -> float:
        """Calculate real distance from A to B, instead of Haversine."""
        return self._ors.calculate_distance(start, destination)
```

## Snippet 75
Lines 842-845

```Python
for thing in things_nearby:
            cache_key = f"ors_{origin}_{thing['id']}"
            nav_distance = cache.get(cache_key)
```

## Snippet 76
Lines 849-856

```Python
print(f"[OSM] Checking ORS for {thing['id']}")
                try:
                    nav_distance = self.calculate_navigation_distance(origin, thing)
                except Exception as e:
                    print(f"[OSM] Error querying ORS: {e}")
                    print(f"[OSM] Falling back to regular distance due to ORS error!")
                    nav_distance = thing['distance']
```

## Snippet 77
Lines 857-861

```Python
if nav_distance:
                used_ors = True
                cache.set(cache_key, nav_distance)
                thing['nav_distance'] = round(nav_distance, 3)
```

## Snippet 78
Lines 872-876

```Python
if self.user_valves:
            return self.user_valves.instruction_oriented_interpretation
        else:
            return self.valves.instruction_oriented_interpretation
```

## Snippet 79
Lines 878-882

```Python
if self.use_detailed_interpretation_mode():
            return detailed_instructions(tag_type_str)
        else:
            return simple_instructions(tag_type_str)
```

## Snippet 80
Lines 888-890

```Python
if key not in result:
                result[key] = []
            result[key].append(value)
```

## Snippet 81
Lines 894-898

```Python
def fallback(nominatim_result):
        """
        If we do not have Overpass Turbo results, attempt to use the
        Nominatim result instead.
        """
```

## Snippet 82
Lines 899-904

```Python
return ([nominatim_result] if 'type' in nominatim_result
                and (nominatim_result['type'] == 'amenity'
                     or nominatim_result['type'] == 'shop'
                     or nominatim_result['type'] == 'leisure'
                     or nominatim_result['type'] == 'tourism')
                else [])
```

## Snippet 83
Lines 907-912

```Python
async def nominatim_lookup_by_id(self, things, format="json"):
        await self.event_fetching(done=False)
        updated_things = [] # the things with merged info.

        # handle last chunk, which can have nones in order due to the
        # way chunking is done.
```

## Snippet 84
Lines 917-919

```Python
if thing is None:
                continue
            lookup = to_lookup(thing)
```

## Snippet 85
Lines 928-931

```Python
if from_cache is not None:
                updated_things.append(from_cache)
                lookups_to_remove.append(lookup_id)
```

## Snippet 86
Lines 935-939

```Python
if len(lookups) == 0:
            print("[OSM] Got all Nominatim info from cache!")
            await self.event_fetching(done=True)
            return updated_things
        else:
```

## Snippet 87
Lines 943-949

```Python
url = urljoin(self.valves.nominatim_url, "lookup")
        params = {
            'osm_ids': ",".join(lookups),
            'format': format
        }

        headers = self.create_headers()
```

## Snippet 88
Lines 950-953

```Python
if not headers:
            raise ValueError("Headers not set")

        response = requests.get(url, params=params, headers=headers)
```

## Snippet 89
Lines 958-961

```Python
print("[OSM] No results found for lookup")
                await self.event_fetching(done=True)
                return []
```

## Snippet 90
Lines 968-972

```Python
if updated is not None:
                        lookup = to_lookup(thing)
                        cache.set(lookup, updated)
                        updated_things.append(updated)
```

## Snippet 91
Lines 975-978

```Python
else:
            await self.event_error(Exception(response.text))
            print(response.text)
            return []
```

## Snippet 92
Lines 981-986

```Python
async def nominatim_search(self, query, format="json", limit: int=1) -> Optional[dict]:
        await self.event_resolving(done=False)
        cache_key = f"nominatim_search_{query}"
        cache = OsmCache()
        data = cache.get(cache_key)
```

## Snippet 93
Lines 988-991

```Python
print(f"[OSM] Got nominatim search data for {query} from cache!")
            await self.event_resolving(done=True)
            return data[:limit]
```

## Snippet 94
Lines 992-1002

```Python
print(f"[OSM] Searching Nominatim for: {query}")

        url = urljoin(self.valves.nominatim_url, "search")
        params = {
            'q': query,
            'format': format,
            'addressdetails': 1,
            'limit': limit,
        }

        headers = self.create_headers()
```

## Snippet 95
Lines 1003-1007

```Python
if not headers:
            await self.event_error("Headers not set")
            raise ValueError("Headers not set")

        response = requests.get(url, params=params, headers=headers)
```

## Snippet 96
Lines 1008-1011

```Python
if response.status_code == 200:
            await self.event_resolving(done=True)
            data = response.json()
```

## Snippet 97
Lines 1015-1017

```Python
print(f"Got result from Nominatim for: {query}")
            cache.set(cache_key, data)
            return data[:limit]
```

## Snippet 98
Lines 1018-1021

```Python
else:
            await self.event_error(Exception(response.text))
            print(response.text)
            return None
```

## Snippet 99
Lines 1024-1033

```Python
async def overpass_search(
            self, place, tags, bbox, limit=5, radius=4000
    ) -> (List[dict], List[dict]):
        """
        Return a list relevant of OSM nodes and ways. Some
        post-processing is done on ways in order to add coordinates to
        them.
        """
        print(f"Searching Overpass Turbo around origin {place}")
        headers = self.create_headers()
```

## Snippet 100
Lines 1034-1042

```Python
if not headers:
            raise ValueError("Headers not set")

        url = self.valves.overpass_turbo_url
        center = get_bounding_box_center(bbox)
        around = f"(around:{radius},{center['lat']},{center['lon']})"

        tag_groups = OsmSearcher.group_tags(tags)
        search_groups = [f'"{tag_type}"~"{"|".join(values)}"'
```

## Snippet 101
Lines 1046-1051

```Python
for search_group in search_groups:
            searches.append(
                f'nwr[{search_group}]{around}'
            )

        search = ";\n".join(searches)
```

## Snippet 102
Lines 1052-1065

```Python
if len(search) > 0:
            search += ";"

        # "out geom;" is needed to get bounding box info of ways,
        # so we can calculate the coordinates.
        query = f"""
            [out:json];
            (
                {search}
            );
            out geom;
        """

        print(query)
```

## Snippet 103
Lines 1084-1087

```Python
if thing_has_info(res):
                        nodes.append(res)
                    else:
                        things_missing_names.append(res)
```

## Snippet 104
Lines 1104-1107

```Python
else:
            print(response.text)
            raise Exception(f"Error calling Overpass API: {response.text}")
```

## Snippet 105
Lines 1111-1114

```Python
# use results from overpass, but if they do not exist,
        # fall back to the nominatim result. this may or may
        # not be a good idea.
        things_nearby = (nodes + ways
```

## Snippet 106
Lines 1118-1129

```Python
# in order to not spam ORS, we first sort by haversine
        # distance and drop number of results to the limit. then, if
        # enabled, we calculate ORS distances. then we sort again.
        origin = get_bounding_box_center(bbox)
        self.calculate_haversine(origin, things_nearby)

        # sort by importance + distance, drop to the liimt, then sort
        # by closeness.
        things_nearby = sort_by_rank(things_nearby)
        things_nearby = things_nearby[:limit] # drop down to requested limit
        things_nearby = sort_by_closeness(origin, things_nearby, 'distance')
```

## Snippet 107
Lines 1130-1133

```Python
if self.attempt_ors(origin, things_nearby):
            things_nearby = sort_by_closeness(origin, things_nearby, 'nav_distance', 'distance')
        return things_nearby
```

## Snippet 108
Lines 1134-1138

```Python
async def search_nearby(
            self, place: str, tags: List[str], limit: int=5, radius: int=4000,
            category: str="POIs"
    ) -> dict:
        headers = self.create_headers()
```

## Snippet 109
Lines 1142-1146

```Python
try:
            nominatim_result = await self.nominatim_search(place, limit=1)
        except ValueError:
            nominatim_result = []
```

## Snippet 110
Lines 1159-1162

```Python
if addr is not None:
                    place_display_name = ",".join(addr.split(",")[:3])
                else:
                    place_display_name = place
```

## Snippet 111
Lines 1167-1175

```Python
await self.event_searching(category, place_display_name, done=False)

            bbox = {
                'minlat': nominatim_result['boundingbox'][0],
                'maxlat': nominatim_result['boundingbox'][1],
                'minlon': nominatim_result['boundingbox'][2],
                'maxlon': nominatim_result['boundingbox'][3]
            }
```

## Snippet 112
Lines 1191-1201

```Python
if search_results:
                result_instructions = self.get_result_instructions(tag_type_str)
            else:
                result_instructions = ("No results found at all. "
                                       "Tell the user there are no results.")

            resp = (
                f"{result_instructions}\n\n"
                f"{search_results}"
            )
```

## Snippet 113
Lines 1211-1216

```Python
except Exception as e:
            print(e)
            await self.event_error(e)
            result = (f"No results were found, because of an error. "
                      f"Tell the user that there was an error finding results. "
                      f"The error was: {e}")
```

## Snippet 114
Lines 1220-1224

```Python
async def do_osm_search(
        valves, user_valves, place, tags,
        category="POIs", event_emitter=None, limit=5, radius=4000
):
    # handle breaking 1.0 change, in case of old Nominatim valve settings.
```

## Snippet 115
Lines 1228-1238

```Python
if valves.status_indicators and event_emitter is not None:
            await event_emitter({
                "type": "status",
                "data": {
                    "status": "error",
                    "description": f"Error searching OpenStreetMap: {message}",
                    "done": True,
                },
            })
        return OLD_VALVE_SETTING.replace("{OLD}", valves.nominatim_url)
```

## Snippet 116
Lines 1239-1243

```Python
print(f"[OSM] Searching for [{category}] ({tags[0]}, etc) near place: {place}")
    searcher = OsmSearcher(valves, user_valves, event_emitter)
    search = await searcher.search_nearby(place, tags, limit=limit, radius=radius, category=category)
    return search["results"]
```

## Snippet 117
Lines 1244-1249

```Python
async def do_osm_search_full(
        valves, user_valves, place, tags,
        category="POIs", event_emitter=None, limit=5, radius=4000
):
    """Like do_osm_search, but return the full result set instead."""
    # handle breaking 1.0 change, in case of old Nominatim valve settings.
```

## Snippet 118
Lines 1253-1263

```Python
if valves.status_indicators and event_emitter is not None:
            await event_emitter({
                "type": "status",
                "data": {
                    "status": "error",
                    "description": f"Error searching OpenStreetMap: {message}",
                    "done": True,
                },
            })
        return OLD_VALVE_SETTING.replace("{OLD}", valves.nominatim_url)
```

## Snippet 119
Lines 1264-1267

```Python
print(f"[OSM] Searching for [{category}] ({tags[0]}, etc) near place: {place}")
    searcher = OsmSearcher(valves, user_valves, event_emitter)
    return await searcher.search_nearby(place, tags, limit=limit, radius=radius, category=category)
```

## Snippet 120
Lines 1269-1275

```Python
def __init__(
        self, valves, user_valves: Optional[dict], event_emitter=None,
    ):
        self.valves = valves
        self.event_emitter = event_emitter
        self.user_valves = user_valves
```

## Snippet 121
Lines 1280-1293

```Python
if done:
            message = "OpenStreetMap: navigation complete"
        else:
            message = "OpenStreetMap: navigating..."

        await self.event_emitter({
            "type": "status",
            "data": {
                "status": "in_progress",
                "description": message,
                "done": done,
            },
        })
```

## Snippet 122
Lines 1295-1306

```Python
if not self.event_emitter or not self.valves.status_indicators:
            return

        await self.event_emitter({
            "type": "status",
            "data": {
                "status": "error",
                "description": f"Error navigating: {str(exception)}",
                "done": True,
            },
        })
```

## Snippet 123
Lines 1307-1315

```Python
async def navigate(self, start_place: str, destination_place: str):
        await self.event_navigating(done=False)
        searcher = OsmSearcher(self.valves, self.user_valves, self.event_emitter)
        router = OrsRouter(self.valves, self.user_valves, self.event_emitter)

        try:
            start = await searcher.nominatim_search(start_place, limit=1)
            destination = await searcher.nominatim_search(destination_place, limit=1)
```

## Snippet 124
Lines 1316-1322

```Python
if not start or not destination:
                await self.event_navigating(done=True)
                return NO_RESULTS

            start, destination = start[0], destination[0]
            route = router.calculate_route(start, destination)
```

## Snippet 125
Lines 1323-1328

```Python
if not route:
                await self.event_navigating(done=True)
                return NO_RESULTS

            total_distance = round(route.get('summary', {}).get('distance', ''), 2)
            travel_time = round(route.get('summary', {}).get('duration', 0) / 60.0, 2)
```

## Snippet 126
Lines 1331-1335

```Python
def create_step_instruction(step):
                instruction = step['instruction']
                duration = round(step.get('duration', 0.0) / 60.0, 2)
                distance = round(step.get('distance', 0.0), 2)
```

## Snippet 127
Lines 1344-1348

```Python
if distance < 1.0:
                    distance = f"{round(distance * 1000.0, 2)}m"
                else:
                    distance = f"{distance}km"
```

## Snippet 128
Lines 1366-1370

```Python
)

            resp = f"{navigation_instructions(travel_type)}\n\n{markdown}"
            await self.event_navigating(done=True)
            return resp
```

## Snippet 129
Lines 1371-1377

```Python
except Exception as e:
            print(e)
            await self.event_error(e)
            return (f"There are no results due to an error. "
                    "Tell the user that there was an error. "
                    f"The error was: {e}. "
                    f"Tell the user the error message.")
```

## Snippet 130
Lines 1381-1389

```Python
class Valves(BaseModel):
        user_agent: str = Field(
            default="", description="Unique user agent to identify your OSM API requests."
        )
        from_header: str = Field(
            default="", description="Email address to identify your OSM requests."
        )
        nominatim_url: str = Field(
            default="https://nominatim.openstreetmap.org/",
```

## Snippet 131
Lines 1391-1393

```Python
)
        overpass_turbo_url: str = Field(
            default="https://overpass-api.de/api/interpreter",
```

## Snippet 132
Lines 1395-1398

```Python
)
        instruction_oriented_interpretation: bool = Field(
            default=True,
            description=("Give detailed result interpretation instructions to the model. "
```

## Snippet 133
Lines 1400-1415

```Python
)
        ors_api_key: Optional[str] = Field(
            default=None,
            description=("Provide an Open Route Service API key to calculate "
                         "more accurate distances (leave default to disable).")
        )
        ors_instance: Optional[str] = Field(
            default=None,
            description="Use a custom ORS instance (leave default to use public ORS instance)."
        )
        status_indicators: bool = Field(
            default=True,
            description=("Emit status update events to the web UI.")
        )
        pass
```

## Snippet 134
Lines 1416-1419

```Python
class UserValves(BaseModel):
        instruction_oriented_interpretation: bool = Field(
            default=True,
            description=("Give detailed result interpretation instructions to the model. "
```

## Snippet 135
Lines 1425-1428

```Python
def __init__(self):
        self.valves = self.Valves()
        self.user_valves = None
```

## Snippet 136
Lines 1429-1438

```Python
async def find_address_for_coordinates(self, latitude: float, longitude: float, __event_emitter__) -> str:
        """
        Resolves GPS coordinates to a specific address or place.
        :param latitude: The latitude portion of the GPS coordinate.
        :param longitude: The longitude portion of the GPS coordinate.
        :return: Information about the address or place at the coordinates.
        """
        print(f"[OSM] Resolving [{latitude}, {longitude}] to address.")
        return await self.find_specific_place(f"{latitude}, {longitude}", __event_emitter__)
```

## Snippet 137
Lines 1439-1443

```Python
async def find_store_or_place_near_coordinates(
            self, store_or_business_name: str, latitude: float, longitude: float, __event_emitter__
    ) -> str:
        """
        Finds specifically named stores, businesses, or landmarks near the given
```

## Snippet 138
Lines 1448-1453

```Python
Use this if the user asks about businesses or places nearby.
        :param store_or_business_name: Name of store or business to look for.
        :param latitude: The latitude portion of the GPS coordinate.
        :param longitude: The longitude portion of the GPS coordinate.
        :return: Information about the address or places near the coordinates.
        """
```

## Snippet 139
Lines 1458-1460

```Python
async def find_specific_place(self, address_or_place: str, __event_emitter__) -> str:
        """
        Looks up details on OpenStreetMap of a specific address, landmark,
```

## Snippet 140
Lines 1461-1464

```Python
place, named building, or location. Used for when the user asks where
        a specific unique entity (like a specific museum, or church, or shopping
        center) is.
        :param address_or_place: The address or place to look up.
```

## Snippet 141
Lines 1467-1470

```Python
print(f"[OSM] Searching for info on [{address_or_place}].")
        searcher = OsmSearcher(self.valves, self.user_valves, __event_emitter__)
        try:
            result = await searcher.nominatim_search(address_or_place, limit=5)
```

## Snippet 142
Lines 1471-1480

```Python
if result:
                results_in_md = convert_and_validate_results(
                    address_or_place, result,
                    sort_message="importance", use_distance=False
                )

                resp = f"{specific_place_instructions()}\n\n{results_in_md}"
                return resp
            else:
                return NO_RESULTS
```

## Snippet 143
Lines 1481-1486

```Python
except Exception as e:
            print(e)
            return (f"There are no results due to an error. "
                    "Tell the user that there was an error. "
                    f"The error was: {e}. "
                    f"Tell the user the error message.")
```

## Snippet 144
Lines 1489-1498

```Python
async def navigate_between_places(
            self,
            start_address_or_place: str,
            destination_address_or_place: str,
            __event_emitter__
    ) -> str:
        """
        Retrieve a navigation route and associated information between two places.
        :param start_address_or_place: The address, place, or coordinates to start from.
        :param destination_address_or_place: The destination address, place, or coordinates to go.
```

## Snippet 145
Lines 1499-1504

```Python
:return: The navigation route and associated info, if found.
        """
        print(f"[OSM] Navigating from [{start_address_or_place}] to [{destination_address_or_place}].")
        navigator = OsmNavigator(self.valves, self.user_valves, __event_emitter__)
        return await navigator.navigate(start_address_or_place, destination_address_or_place)
```

## Snippet 146
Lines 1505-1512

```Python
async def find_grocery_stores_near_place(
            self, place: str, __user__: dict, __event_emitter__
    ) -> str:
        """
        Finds supermarkets, grocery stores, and other food stores on
        OpenStreetMap near a given place or address. The location of the
        address or place is reverse geo-coded, then nearby results
        are fetched from OpenStreetMap.
```

## Snippet 147
Lines 1516-1519

```Python
user_valves = __user__["valves"] if "valves" in __user__ else None
        tags = ["shop=supermarket", "shop=grocery", "shop=convenience", "shop=greengrocer"]
        return await do_osm_search(valves=self.valves, user_valves=user_valves, category="groceries",
                                   place=place, tags=tags, event_emitter=__event_emitter__)
```

## Snippet 148
Lines 1522-1526

```Python
async def find_bakeries_near_place(self, __user__: dict, place: str, __event_emitter__) -> str:
        """
        Finds bakeries on OpenStreetMap near a given place or
        address. The location of the address or place is reverse
        geo-coded, then nearby results are fetched from OpenStreetMap.
```

## Snippet 149
Lines 1530-1534

```Python
user_valves = __user__["valves"] if "valves" in __user__ else None
        tags = ["shop=bakery"]
        return await do_osm_search(valves=self.valves, user_valves=user_valves, category="bakeries",
                             place=place, tags=tags, event_emitter=__event_emitter__)
```

## Snippet 150
Lines 1535-1540

```Python
async def find_food_near_place(self, __user__: dict, place: str, __event_emitter__) -> str:
        """
        Finds restaurants, fast food, bars, breweries, pubs, etc on
        OpenStreetMap near a given place or address. The location of the
        address or place is reverse geo-coded, then nearby results
        are fetched from OpenStreetMap.
```

## Snippet 151
Lines 1544-1556

```Python
user_valves = __user__["valves"] if "valves" in __user__ else None
        tags = [
            "amenity=restaurant",
            "amenity=fast_food",
            "amenity=cafe",
            "amenity=pub",
            "amenity=bar",
            "amenity=eatery",
            "amenity=biergarten",
            "amenity=canteen"
        ]
        return await do_osm_search(valves=self.valves, user_valves=user_valves, category="restaurants and food",
                                   place=place, tags=tags, event_emitter=__event_emitter__)
```

## Snippet 152
Lines 1559-1564

```Python
async def find_swimming_near_place(self, __user__: dict, place: str, __event_emitter__) -> str:
        """
        Finds swimming pools, water parks, swimming areas, and other aquatic
        activities on OpenStreetMap near a given place or address. The location
        of the address or place is reverse geo-coded, then nearby results are fetched
        from OpenStreetMap.
```

## Snippet 153
Lines 1568-1573

```Python
user_valves = __user__["valves"] if "valves" in __user__ else None
        tags = ["leisure=swimming_pool", "leisure=swimming_area",
                "leisure=water_park", "tourism=theme_park"]
        return await do_osm_search(valves=self.valves, user_valves=user_valves, category="swimming",
                                   radius=10000, place=place, tags=tags, event_emitter=__event_emitter__)
```

## Snippet 154
Lines 1574-1578

```Python
async def find_playgrounds_near_place(self, __user__: dict, place: str, __event_emitter__) -> str:
        """
        Finds playgrounds and parks on OpenStreetMap near a given place, address, or coordinates.
        The location of the address or place is reverse geo-coded, then nearby results are fetched
        from OpenStreetMap.
```

## Snippet 155
Lines 1582-1586

```Python
user_valves = __user__["valves"] if "valves" in __user__ else None
        tags = ["leisure=playground"]
        return await do_osm_search(valves=self.valves, user_valves=user_valves, category="playgrounds",
                                   limit=10, place=place, tags=tags, event_emitter=__event_emitter__)
```

## Snippet 156
Lines 1587-1592

```Python
async def find_recreation_near_place(self, __user__: dict, place: str, __event_emitter__) -> str:
        """
        Finds playgrounds, theme parks, parks, frisbee golf, ice skating, and other recreational
        activities on OpenStreetMap near a given place or address. The location
        of the address or place is reverse geo-coded, then nearby results are fetched
        from OpenStreetMap.
```

## Snippet 157
Lines 1596-1601

```Python
user_valves = __user__["valves"] if "valves" in __user__ else None
        tags = ["leisure=horse_riding", "leisure=ice_rink", "leisure=disc_golf_course",
                "leisure=park", "leisure=amusement_arcade", "tourism=theme_park"]
        return await do_osm_search(valves=self.valves, user_valves=user_valves, category="recreational activities",
                                   limit=10, radius=10000, place=place, tags=tags, event_emitter=__event_emitter__)
```

## Snippet 158
Lines 1602-1606

```Python
async def find_tourist_attractions_near_place(self, __user__: dict, place: str, __event_emitter__) -> str:
        """
        Finds museums, landmarks, and other tourist attractions on OpenStreetMap near
        a given place or address. The location of the address or place is reverse geo-coded,
        then nearby results are fetched from OpenStreetMap.
```

## Snippet 159
Lines 1610-1615

```Python
user_valves = __user__["valves"] if "valves" in __user__ else None
        tags = ["tourism=museum", "tourism=aquarium", "tourism=zoo",
                "tourism=attraction", "tourism=gallery", "tourism=artwork"]

        return await do_osm_search(valves=self.valves, user_valves=user_valves, category="tourist attractions",
                                   limit=10, radius=10000, place=place, tags=tags, event_emitter=__event_emitter__)
```

## Snippet 160
Lines 1619-1624

```Python
async def find_place_of_worship_near_place(self, __user__: dict, place: str, __event_emitter__) -> str:
        """
        Finds places of worship (churches, mosques, temples, etc) on
        OpenStreetMap near a given place or address. The location of the
        address or place is reverse geo-coded, then nearby results
        are fetched from OpenStreetMap.
```

## Snippet 161
Lines 1628-1631

```Python
user_valves = __user__["valves"] if "valves" in __user__ else None
        tags = ["amenity=place_of_worship"]
        return await do_osm_search(valves=self.valves, user_valves=user_valves, category="places of worship",
                                   place=place, tags=tags, event_emitter=__event_emitter__)
```

## Snippet 162
Lines 1634-1639

```Python
async def find_accommodation_near_place(self, __user__: dict, place: str, __event_emitter__) -> str:
        """
        Finds accommodation (hotels, guesthouses, hostels, etc) on
        OpenStreetMap near a given place or address. The location of the
        address or place is reverse geo-coded, then nearby results
        are fetched from OpenStreetMap.
```

## Snippet 163
Lines 1643-1650

```Python
user_valves = __user__["valves"] if "valves" in __user__ else None
        tags = [
            "tourism=hotel", "tourism=chalet", "tourism=guest_house", "tourism=guesthouse",
            "tourism=motel", "tourism=hostel"
        ]
        return await do_osm_search(valves=self.valves, user_valves=user_valves, category="accommodation",
                                   radius=10000, place=place, tags=tags, event_emitter=__event_emitter__)
```

## Snippet 164
Lines 1651-1656

```Python
async def find_alcohol_near_place(self, __user__: dict, place: str, __event_emitter__) -> str:
        """
        Finds beer stores, liquor stores, and similar shops on OpenStreetMap
        near a given place or address. The location of the address or place is
        reverse geo-coded, then nearby results
        are fetched from OpenStreetMap.
```

## Snippet 165
Lines 1660-1664

```Python
user_valves = __user__["valves"] if "valves" in __user__ else None
        tags = ["shop=alcohol"]
        return await do_osm_search(valves=self.valves, user_valves=user_valves, category="alcohol stores",
                                   place=place, tags=tags, event_emitter=__event_emitter__)
```

## Snippet 166
Lines 1665-1670

```Python
async def find_drugs_near_place(self, __user__: dict, place: str, __event_emitter__) -> str:
        """
        Finds cannabis dispensaries, coffeeshops, smartshops, and similar stores on OpenStreetMap
        near a given place or address. The location of the address or place is
        reverse geo-coded, then nearby results
        are fetched from OpenStreetMap.
```

## Snippet 167
Lines 1674-1678

```Python
user_valves = __user__["valves"] if "valves" in __user__ else None
        tags = ["shop=coffeeshop", "shop=cannabis", "shop=headshop", "shop=smartshop"]
        return await do_osm_search(valves=self.valves, user_valves=user_valves, category="cannabis and smartshops",
                                   place=place, tags=tags, event_emitter=__event_emitter__)
```

## Snippet 168
Lines 1679-1681

```Python
async def find_schools_near_place(self, __user__: dict, place: str, __event_emitter__) -> str:
        """
        Finds schools (NOT universities) on OpenStreetMap near a given place or address.
```

## Snippet 169
Lines 1683-1685

```Python
:return: A list of nearby schools, if found.
        """
        tags = ["amenity=school"]
```

## Snippet 170
Lines 1686-1689

```Python
user_valves = __user__["valves"] if "valves" in __user__ else None
        return await do_osm_search(valves=self.valves, user_valves=user_valves, category="schools",
                                   limit=10, place=place, tags=tags, event_emitter=__event_emitter__)
```

## Snippet 171
Lines 1690-1692

```Python
async def find_universities_near_place(self, __user__: dict, place: str, __event_emitter__) -> str:
        """
        Finds universities and colleges on OpenStreetMap near a given place or address.
```

## Snippet 172
Lines 1694-1696

```Python
:return: A list of nearby schools, if found.
        """
        tags = ["amenity=university", "amenity=college"]
```

## Snippet 173
Lines 1697-1700

```Python
user_valves = __user__["valves"] if "valves" in __user__ else None
        return await do_osm_search(valves=self.valves, user_valves=user_valves, category="universities",
                                   limit=10, place=place, tags=tags, event_emitter=__event_emitter__)
```

## Snippet 174
Lines 1701-1703

```Python
async def find_libraries_near_place(self, __user__: dict, place: str, __event_emitter__) -> str:
        """
        Finds libraries on OpenStreetMap near a given place or address.
```

## Snippet 175
Lines 1705-1707

```Python
:return: A list of nearby libraries, if found.
        """
        tags = ["amenity=library"]
```

## Snippet 176
Lines 1708-1711

```Python
user_valves = __user__["valves"] if "valves" in __user__ else None
        return await do_osm_search(valves=self.valves, user_valves=user_valves, category="libraries",
                                   place=place, tags=tags, event_emitter=__event_emitter__)
```

## Snippet 177
Lines 1712-1714

```Python
async def find_public_transport_near_place(self, __user__: dict, place: str, __event_emitter__) -> str:
        """
        Finds public transportation stops on OpenStreetMap near a given place or address.
```

## Snippet 178
Lines 1718-1725

```Python
user_valves = __user__["valves"] if "valves" in __user__ else None
        tags = ["highway=bus_stop", "amenity=bus_station",
                "railway=station", "railway=halt", "railway=tram_stop",
                "station=subway", "amenity=ferry_terminal",
                "public_transport=station"]
        return await do_osm_search(valves=self.valves, user_valves=user_valves, category="public transport",
                                   limit=10, place=place, tags=tags, event_emitter=__event_emitter__)
```

## Snippet 179
Lines 1726-1728

```Python
async def find_bike_rentals_near_place(self, __user__: dict, place: str, __event_emitter__) -> str:
        """
        Finds bike rentals on OpenStreetMap near a given place or address.
```

## Snippet 180
Lines 1732-1736

```Python
user_valves = __user__["valves"] if "valves" in __user__ else None
        tags = ["amenity=bicycle_rental", "amenity=bicycle_library", "service:bicycle:rental=yes"]
        return await do_osm_search(valves=self.valves, user_valves=user_valves, category="bike rentals",
                                   place=place, tags=tags, event_emitter=__event_emitter__)
```

## Snippet 181
Lines 1737-1739

```Python
async def find_car_rentals_near_place(self, __user__: dict, place: str, __event_emitter__) -> str:
        """
        Finds bike rentals on OpenStreetMap near a given place or address.
```

## Snippet 182
Lines 1743-1747

```Python
user_valves = __user__["valves"] if "valves" in __user__ else None
        tags = ["amenity=car_rental", "car:rental=yes", "rental=car", "car_rental=yes"]
        return await do_osm_search(valves=self.valves, user_valves=user_valves, category="car rentals",
                                   radius=6000, place=place, tags=tags, event_emitter=__event_emitter__)
```

## Snippet 183
Lines 1748-1751

```Python
async def find_hardware_store_near_place(self, __user__: dict, place: str, __event_emitter__) -> str:
        """
        Finds hardware stores, home improvement stores, and DIY stores
        near given a place or address.
```

## Snippet 184
Lines 1755-1760

```Python
user_valves = __user__["valves"] if "valves" in __user__ else None
        tags = ["shop=doityourself", "shop=hardware", "shop=power_tools",
                "shop=groundskeeping", "shop=trade"]
        return await do_osm_search(valves=self.valves, user_valves=user_valves, category="hardware stores",
                                   place=place, tags=tags, event_emitter=__event_emitter__)
```

## Snippet 185
Lines 1761-1765

```Python
async def find_electrical_store_near_place(self, __user__: dict, place: str, __event_emitter__) -> str:
        """
        Finds electrical stores and lighting stores near a given place
        or address. These are stores that sell lighting and electrical
        equipment like wires, sockets, and so forth.
```

## Snippet 186
Lines 1769-1773

```Python
user_valves = __user__["valves"] if "valves" in __user__ else None
        tags = ["shop=lighting", "shop=electrical"]
        return await do_osm_search(valves=self.valves, user_valves=user_valves, category="electrical stores",
                                   place=place, tags=tags, event_emitter=__event_emitter__)
```

## Snippet 187
Lines 1774-1777

```Python
async def find_electronics_store_near_place(self, __user__: dict, place: str, __event_emitter__) -> str:
        """
        Finds consumer electronics stores near a given place or address.
        These stores sell computers, cell phones, video games, and so on.
```

## Snippet 188
Lines 1781-1786

```Python
user_valves = __user__["valves"] if "valves" in __user__ else None
        tags = ["shop=electronics"]
        return await do_osm_search(valves=self.valves, user_valves=user_valves,
                                   category="consumer electronics stores", place=place,
                                   tags=tags, event_emitter=__event_emitter__)
```

## Snippet 189
Lines 1787-1789

```Python
async def find_doctor_near_place(self, __user__: dict, place: str, __event_emitter__) -> str:
        """
        Finds doctors near a given place or address.
```

## Snippet 190
Lines 1793-1797

```Python
user_valves = __user__["valves"] if "valves" in __user__ else None
        tags = ["amenity=clinic", "amenity=doctors", "healthcare=doctor"]
        return await do_osm_search(valves=self.valves, user_valves=user_valves, category="doctors",
                                   place=place, tags=tags, event_emitter=__event_emitter__)
```

## Snippet 191
Lines 1798-1800

```Python
async def find_hospital_near_place(self, __user__: dict, place: str, __event_emitter__) -> str:
        """
        Finds doctors near a given place or address.
```

## Snippet 192
Lines 1804-1808

```Python
user_valves = __user__["valves"] if "valves" in __user__ else None
        tags = ["healthcare=hospital", "amenity=hospitals"]
        return await do_osm_search(valves=self.valves, user_valves=user_valves, category="hospitals",
                                   place=place, tags=tags, event_emitter=__event_emitter__)
```

## Snippet 193
Lines 1809-1811

```Python
async def find_pharmacy_near_place(self, __user__: dict, place: str, __event_emitter__) -> str:
        """
        Finds pharmacies and health shops near a given place or address
```

## Snippet 194
Lines 1815-1820

```Python
user_valves = __user__["valves"] if "valves" in __user__ else None
        tags = ["amenity=pharmacy", "shop=chemist", "shop=supplements",
                "shop=health_food"]
        return await do_osm_search(valves=self.valves, user_valves=user_valves, category="pharmacies",
                                   radius=6000, place=place, tags=tags, event_emitter=__event_emitter__)
```

## Snippet 195
Lines 1826-1833

```Python
def find_other_things_near_place(
        self,
        __user__: dict,
        place: str,
        category: str
    ) -> str:
        """
        Find shops and other places not covered by a specific
```

## Snippet 196
Lines 1838-1844

```Python
:param place: The name of a place, an address, or GPS coordinates. City and country must be specified, if known.
        :param category: The category of place, shop, etc to look up.
        :return: A list of nearby shops.
        """
        print(f"[OSM] Generic catch handler called with {category}")
        resp = (
            "# No Results Found\n"
```

## Snippet 197
Lines 1845-1865

```Python
f"No results were found. There was an error. Finding {category} points of interest "
            "is not yet supported. Tell the user support will come eventually! "
            "Tell the user that you are only capable of finding specific "
            "categories of stores, amenities, and points of interest:\n"
            " - Car rentals and bike rentals\n"
            " - Public transport, libraries\n"
            " - Education institutions (schools and universities)\n"
            " - Grocery stores, supermarkets, convenience stores\n"
            " - Food and restaurants\n"
            " - Accommodation\n"
            " - Places of Worship\n"
            " - Hardware stores and home improvement centers\n"
            " - Electrical and lighting stores\n"
            " - Consumer electronics stores\n"
            " - Healthcare (doctors, hospitals, pharmacies, and health stores)\n"
            " - Various recreational and leisure activities\n\n"
            "Only mention things from the above list that you think the user "
            "will be interested in, given the conversation so far. Don't mention "
            "things not on the list. "
            "**IMPORTANT**: Tell the user to be specific in their "
            "query in their next message, so you can call the right function!")
```

