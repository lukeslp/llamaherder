import requests
import json

# API Details
API_URL = "https://api.coze.com/v1/space/published_bots_list"
API_TOKEN = "pat_JF8Lre4IgXOABlmf383x7GyLF6cj6yn6E4ElRKtvYP3DXpYmB9gJpoMyw2qfwjX4"
SPACE_ID = "7345427862138912773"
PAGE_SIZE = 100
OUTPUT_FILE = "agents_list.json"

def fetch_agents():
    print("\n=== Starting agent fetch process ===")
    print(f"API URL: {API_URL}")
    print(f"Space ID: {SPACE_ID}")
    
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    print("Headers configured:", headers)

    params = {
        "space_id": SPACE_ID,
    }
    print("Initial params:", params)

    all_agents = []
    page = 1
    
    print("\n=== Beginning pagination loop ===")
    while True:
        print(f"\nFetching page {page}...")
        print("Current params:", params)
        
        response = requests.get(API_URL, headers=headers, params=params)
        print(f"Response status code: {response.status_code}")

        if response.status_code != 200:
            print("ERROR: Failed to fetch agents")
            print(f"Status code: {response.status_code}")
            print("Response text:", response.text)
            return

        data = response.json()
        print("Response data keys:", list(data.keys()))
        
        agents = data.get("bots", [])
        print(f"Found {len(agents)} agents on page {page}")
        
        all_agents.extend(agents)
        print(f"Total agents collected so far: {len(all_agents)}")

        # Check if more pages are available
        if len(agents) < 20:
            print("\nLast page reached (less than 20 agents)")
            break

        params["page_index"] = page + 1  # Fix: Initialize and increment page index
        page += 1
        print(f"Moving to page {page}")

    print("\n=== Writing results to file ===")
    print(f"Writing {len(all_agents)} agents to {OUTPUT_FILE}")
    
    # Write to file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(all_agents, file, ensure_ascii=False, indent=4)

    print(f"Successfully wrote {len(all_agents)} agents to '{OUTPUT_FILE}'")
    print("=== Process complete ===\n")

if __name__ == "__main__":
    fetch_agents()