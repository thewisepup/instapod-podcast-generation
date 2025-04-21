import argparse
import os
import time
from dotenv import load_dotenv
from supabase import Client, create_client
from podcastfy.client import generate_podcast

from utils.podcast_generation_utils import generate_research_data


load_dotenv()
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(supabase_url, supabase_key)


def genPod(podcast_id):
    start_time = time.time()
    response = supabase.table("podcasts").select("*").eq("id", podcast_id).execute()
    podcast = response.data[0]
    user_id = podcast["user_id"]
    user_description = podcast["user_description"]
    print(f"Podcast ID: {podcast_id}")
    print(f"User ID: {user_id}")
    print(f"User Description: {user_description}")

    research_data = generate_research_data(user_description)

    custom_config = {
        "conversation_style": ["informative", "analytical", "critical"],
        "podcast_name": "InstaPod",
        "podcast_tagline": "Your AI powered podcast",
        "creativity": 0,
    }

    audio_file = generate_podcast(
        text=research_data,
        tts_model="gemini",
        conversation_config=custom_config,
        longform=True,
    )

    print("Uploading podcast to file storage " + audio_file)
    with open(audio_file, "rb") as f:
        supabase.storage.from_("podcasts").upload(
            file=f,
            path=podcast_id,
            file_options={
                "cache-control": "3600",
                "upsert": "false",
                "content-type": "audio/mpeg",
            },
        )

    # # Delete the local audio file after successful upload
    # os.remove(audio_file)
    # print(f"Deleted local audio file: {audio_file}")

    response = (
        supabase.table("podcasts")
        .update({"status": "READY"})
        .eq("id", podcast_id)
        .execute()
    )

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"genPod execution time: {execution_time:.2f} seconds")


def lambda_handler(event, context):
    print("Lambda Handler Event Received")
    podcast_id = event.get("podcast_id", "No podcast_id provided")
    genPod(podcast_id)
    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Hello from Lambda!", "podcast_id": podcast_id}),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process user ID and prompt")

    parser.add_argument("--podcastId", required=True, help="Podcast ID")

    # Parse arguments
    args = parser.parse_args()

    podcast_id = args.podcastId

    genPod(podcast_id)
