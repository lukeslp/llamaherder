#!/usr/bin/env python3
import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from tabulate import tabulate

@dataclass
class PatreonCredentials:
    client_id: str = "mrqWf4Kz2qZ4UkMxUlkT5F8fCq5lJQBIo5UZnrMzrh6v4xan7Ssx1SzE0PVhdD9J"
    client_secret: str = "96l1mu67Oy3w3OrN5gv4cjZjLFZ7J-eDbVzYeI_lVnWvIWz0qwGHhDbE7rwQBNue"
    access_token: str = "IjkcOLwTs7-IUcKF4r-F1x8tgQP_cPNAUkc8EVVzdL8"
    refresh_token: str = "nXmPAs6IGfhVds5cRT5z2RoiT64pFWBo5njNyJQOVpE"
    redirect_uri: str = "https://ai.assisted.space/oauth/callback"

class PatreonAPI:
    """A Python interface for the Patreon API v2"""
    
    BASE_URL = "https://www.patreon.com/api/oauth2/v2"
    
    def __init__(self, credentials: PatreonCredentials = None):
        self.credentials = credentials or PatreonCredentials()
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.credentials.access_token}",
            "Content-Type": "application/json"
        })

    def _make_request(self, endpoint: str, method: str = "GET", params: Dict = None, data: Dict = None) -> Dict:
        """Make a request to the Patreon API"""
        url = f"{self.BASE_URL}/{endpoint}"
        try:
            response = self.session.request(method, url, params=params, json=data, timeout=120)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {endpoint}: {str(e)}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            return {"success": False, "error": str(e)}

    def get_identity(self) -> Dict:
        """Get the identity of the authenticated user"""
        params = {
            'include': 'memberships,memberships.currently_entitled_tiers',
            'fields[user]': 'full_name,email,about,created,url',
            'fields[tier]': 'title,amount_cents,description'
        }
        return self._make_request("identity", params=params)

    def get_campaigns(self) -> Dict:
        """Get the user's campaigns"""
        params = {
            'include': 'tiers,benefits,goals,creator',
            'fields[campaign]': 'summary,creation_name,pay_per_name,is_monthly,is_nsfw,url,creation_count,discord_server_id,google_analytics_id,has_rss,has_sent_rss_notify,image_small_url,image_url,is_charged_immediately,is_monthly,is_nsfw,main_video_embed,main_video_url,one_liner,patron_count,pay_per_name,pledge_url,published_at,rss_artwork_url,rss_feed_title,show_earnings,summary,thanks_embed,thanks_msg,thanks_video_url',
            'fields[tier]': 'title,amount_cents,description,patron_count,created_at,edited_at,published,published_at,requires_shipping,url,user_limit',
            'fields[benefit]': 'title,description,rule_type,created_at,delivered_deliverables_count,tiers_count,deliverables_count,is_deleted,is_ended,is_published',
            'fields[goal]': 'title,amount_cents,description,completed_percentage,created_at,reached_at'
        }
        return self._make_request("campaigns", params=params)

    def get_campaign_posts(self, campaign_id: str) -> List[Dict]:
        """Get all posts from a campaign with pagination support"""
        all_posts = []
        cursor = None
        
        while True:
            params = {
                'include': 'campaign,user,attachments,audio,images,media,poll.choices,poll.current_user_responses.choice,poll.current_user_responses.user,access_rules.tier.null,comments.on_behalf_of_campaign,comments.parent,comments.post,comments.replies.parent,comments.replies.post,comments.replies.user,comments.user,likes.user',
                'fields[post]': 'title,content,is_paid,is_public,published_at,url,embed_data,embed_url,app_id,app_status,edit_url,thumbnail_url,teaser_text,content_teaser_text,post_type,post_file,post_file_name,min_cents_pledged_to_view,like_count,comment_count,view_count,read_time_minutes,created_at,published_at,edited_at,deleted_at,scheduled_for,is_automated_monthly_charge_post,is_paid,is_public,pledge_url,patreon_url,current_user_has_liked,current_user_can_view,current_user_can_delete,current_user_can_comment,current_user_can_edit',
                'fields[media]': 'id,image_urls,download_url,metadata,file_name',
                'fields[user]': 'full_name,url',
                'page[size]': 100
            }
            
            if cursor:
                params['page[cursor]'] = cursor
                
            response = self._make_request(f"campaigns/{campaign_id}/posts", params=params)
            
            if not response.get('data'):
                break
                
            all_posts.extend(response.get('data', []))
            
            # Get the next page cursor from the links
            links = response.get('links', {})
            if not links.get('next'):
                break
                
            # Extract cursor from next link
            cursor = links['next'].split('cursor=')[-1].split('&')[0]
            
        return all_posts

    def get_post_details(self, post_id: str) -> Dict:
        """Get detailed information about a specific post"""
        params = {
            'include': 'campaign,user,attachments,audio,images,media,poll.choices,poll.current_user_responses.choice,poll.current_user_responses.user,access_rules.tier.null,comments.on_behalf_of_campaign,comments.parent,comments.post,comments.replies.parent,comments.replies.post,comments.replies.user,comments.user,likes.user',
            'fields[post]': 'title,content,is_paid,is_public,published_at,url,embed_data,embed_url,app_id,app_status,edit_url,thumbnail_url,teaser_text,content_teaser_text,post_type,post_file,post_file_name,min_cents_pledged_to_view,like_count,comment_count,view_count,read_time_minutes,created_at,published_at,edited_at,deleted_at,scheduled_for,is_automated_monthly_charge_post,is_paid,is_public,pledge_url,patreon_url',
            'fields[media]': 'id,image_urls,download_url,metadata,file_name',
            'fields[user]': 'full_name,url'
        }
        return self._make_request(f"posts/{post_id}", params=params)

    def get_campaign_members(self, campaign_id: str) -> List[Dict]:
        """Get all members of a campaign with pagination support"""
        all_members = []
        cursor = None
        
        while True:
            params = {
                'include': 'currently_entitled_tiers,address,user',
                'fields[member]': 'full_name,email,patron_status,lifetime_support_cents,last_charge_date,next_charge_date,pledge_relationship_start,will_pay_amount_cents,is_follower,last_charge_status,last_charge_date,next_charge_date,note,pledge_cadence,patron_status,is_deleted,has_shipping_address,is_fraud,is_paused',
                'fields[tier]': 'title,amount_cents,description,patron_count,created_at,edited_at,published,published_at,requires_shipping,url,user_limit',
                'fields[user]': 'full_name,email,about,created,url,like_count,comment_count,is_suspended,is_nuked,is_deleted,facebook,twitter,youtube,discord_id,twitch,vimeo,spotify',
                'page[size]': 100
            }
            
            if cursor:
                params['page[cursor]'] = cursor
                
            response = self._make_request(f"campaigns/{campaign_id}/members", params=params)
            
            if not response.get('data'):
                break
                
            all_members.extend(response.get('data', []))
            
            # Get the next page cursor from the links
            links = response.get('links', {})
            if not links.get('next'):
                break
                
            # Extract cursor from next link
            cursor = links['next'].split('cursor=')[-1].split('&')[0]
            
        return all_members

    def format_campaign_table(self, campaign_data: Dict) -> str:
        """Format campaign data as a pretty table"""
        if not campaign_data.get('data'):
            return "No campaign data available"
            
        campaigns = []
        for campaign in campaign_data.get('data', []):
            attrs = campaign.get('attributes', {})
            row = {
                'Name': attrs.get('creation_name', 'N/A'),
                'Summary': attrs.get('summary', 'N/A')[:50] + '...',
                'Type': 'Monthly' if attrs.get('is_monthly') else 'Per Creation',
                'Patron Count': attrs.get('patron_count', 'N/A'),
                'URL': attrs.get('url', 'N/A')
            }
            campaigns.append(row)
            
        return tabulate(
            campaigns,
            headers="keys",
            tablefmt="grid",
            numalign="left",
            stralign="left"
        )

    def format_members_table(self, members: List[Dict]) -> str:
        """Format members data as a pretty table"""
        if not members:
            return "No members data available"
            
        table_data = []
        for member in members:
            attrs = member.get('attributes', {})
            row = {
                'Name': attrs.get('full_name', 'N/A'),
                'Status': attrs.get('patron_status', 'N/A'),
                'Lifetime Support': f"${attrs.get('lifetime_support_cents', 0)/100:.2f}",
                'Last Charge': attrs.get('last_charge_date', 'N/A'),
                'Next Charge': attrs.get('next_charge_date', 'N/A'),
                'Pledge Start': attrs.get('pledge_relationship_start', 'N/A')
            }
            table_data.append(row)
            
        return tabulate(
            table_data,
            headers="keys",
            tablefmt="grid",
            numalign="left",
            stralign="left"
        )

    def format_posts_table(self, posts: List[Dict]) -> str:
        """Format posts data as a pretty table"""
        if not posts:
            return "No posts data available"
            
        table_data = []
        for post in posts:
            attrs = post.get('attributes', {})
            row = {
                'Title': attrs.get('title', 'N/A'),
                'Published': attrs.get('published_at', 'N/A'),
                'Type': attrs.get('post_type', 'N/A'),
                'Is Public': 'Yes' if attrs.get('is_public') else 'No',
                'Comments': attrs.get('comment_count', 0),
                'Likes': attrs.get('like_count', 0)
            }
            table_data.append(row)
            
        return tabulate(
            table_data,
            headers="keys",
            tablefmt="grid",
            numalign="left",
            stralign="left"
        )

def main():
    """Main CLI interface"""
    api = PatreonAPI()
    
    while True:
        print("\nPatreon API Interface")
        print("1) Get Identity Information")
        print("2) List Campaigns")
        print("3) List Campaign Members")
        print("4) List Campaign Posts")
        print("5) Get Post Details")
        print("6) Exit")
        
        choice = input("\nChoose an option: ").strip()
        
        if choice == "1":
            identity = api.get_identity()
            if identity.get('data'):
                print("\nIdentity Information:")
                print(json.dumps(identity, indent=2))
            else:
                print("Failed to fetch identity information")
                
        elif choice == "2":
            campaigns = api.get_campaigns()
            if campaigns.get('data'):
                print("\nCampaigns:")
                print(api.format_campaign_table(campaigns))
                print("\nFull Campaign Data:")
                print(json.dumps(campaigns, indent=2))
            else:
                print("Failed to fetch campaigns")
                
        elif choice == "3":
            campaign_id = input("Enter Campaign ID: ").strip()
            if campaign_id:
                members = api.get_campaign_members(campaign_id)
                print("\nCampaign Members:")
                print(api.format_members_table(members))
                print("\nFull Member Data:")
                print(json.dumps(members, indent=2))
            else:
                print("Please provide a campaign ID")
                
        elif choice == "4":
            campaign_id = input("Enter Campaign ID: ").strip()
            if campaign_id:
                posts = api.get_campaign_posts(campaign_id)
                print("\nCampaign Posts:")
                print(api.format_posts_table(posts))
                print("\nDetailed Post Content:")
                for post in posts:
                    attrs = post.get('attributes', {})
                    print("\n" + "="*80)
                    print(f"Title: {attrs.get('title', 'N/A')}")
                    print(f"Published: {attrs.get('published_at', 'N/A')}")
                    print("-"*80)
                    print("Content:")
                    print(attrs.get('content', 'No content available'))
                    if attrs.get('embed_data'):
                        print("\nEmbed Data:")
                        print(json.dumps(attrs['embed_data'], indent=2))
            else:
                print("Please provide a campaign ID")
                
        elif choice == "5":
            post_id = input("Enter Post ID: ").strip()
            if post_id:
                post = api.get_post_details(post_id)
                if post.get('data'):
                    attrs = post['data'].get('attributes', {})
                    print("\nPost Details:")
                    print("="*80)
                    print(f"Title: {attrs.get('title', 'N/A')}")
                    print(f"Published: {attrs.get('published_at', 'N/A')}")
                    print(f"URL: {attrs.get('url', 'N/A')}")
                    print("-"*80)
                    print("Content:")
                    print(attrs.get('content', 'No content available'))
                    if attrs.get('embed_data'):
                        print("\nEmbed Data:")
                        print(json.dumps(attrs['embed_data'], indent=2))
                    print("\nFull Post Data:")
                    print(json.dumps(post, indent=2))
                else:
                    print("Failed to fetch post details")
            else:
                print("Please provide a post ID")
                
        elif choice == "6":
            print("Goodbye!")
            break
            
        else:
            print("Invalid option, please try again")

if __name__ == "__main__":
    main() 