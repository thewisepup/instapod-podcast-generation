#!/usr/bin/env python3

import argparse
import os
from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")


supabase: Client = create_client(supabase_url, supabase_key)


def parse_args():
    # Create argument parser
    parser = argparse.ArgumentParser(description="Process user ID and prompt")

    parser.add_argument("--podcastId", required=True, help="Podcast ID")

    # Parse arguments
    args = parser.parse_args()

    podcast_id = args.podcastId

    return podcast_id


def generate_podcast(podcast_id):
    response = supabase.table("podcasts").select("*").eq("id", podcast_id).execute()
    podcast = response.data[0]
    user_id = podcast["user_id"]
    user_description = podcast["user_description"]
    print(f"Generating podcast for user {user_id} with prompt {user_description}")
    # TODO: generate podcast
    # TODO: upload podcast to s3/supabase

    response = (
        supabase.table("podcasts")
        .update({"status": "READY"})
        .eq("id", podcast_id)
        .execute()
    )  # update_location with s3 location


if __name__ == "__main__":
    podcast_id = parse_args()
    # Print the received values (you can replace this with your actual logic)

    print(f"Podcast ID: {podcast_id}")

    generate_podcast(podcast_id)
