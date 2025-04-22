"""
Gotchas I Encountered
1. Moved imports into lambda_handler to reduce init (not sure if this was the actual reason, we can try moving back out)
2. Updated memory to 900MB in lambda. This was the reason why i was running into init issues,
since the dependencies is 600mb+ but default lambda memory is like way under that
3. Updated architecture to use ARM
4. Update timeout to 2mins, need to extend to like 10mins or longer
5. Updated output_directories to use
TODO: Figure out optimal memory and ephemeral storage to use. Memory should be consistent for all, storage can vary.
"""


def lambda_handler(event, context):
    import time
    import json
    import os

    from dotenv import load_dotenv
    from supabase import Client, create_client
    from podcastfy.client import generate_podcast
    from utils.podcast_generation_utils import generate_research_data
    import logging

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    logger.info("Lambda Handler Event Received")
    podcast_id = event.get("podcast_id", "No podcast_id provided")
    logger.info(f"Processing podcast_id: {podcast_id}")

    try:
        start_time = time.time()
        load_dotenv()
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")

        supabase: Client = create_client(supabase_url, supabase_key)
        logger.info(f"Starting podcast generation for podcast_id: {podcast_id}")

        response = supabase.table("podcasts").select("*").eq("id", podcast_id).execute()
        podcast = response.data[0]
        user_id = podcast["user_id"]
        user_description = podcast["user_description"]
        logger.info(f"Retrieved podcast data - ID: {podcast_id}, User ID: {user_id}")
        logger.debug(f"User description: {user_description}")

        logger.info("Generating research data from user description")
        research_data = generate_research_data(user_description)
        logger.debug("Research data generation completed")

        custom_config = {
            "conversation_style": ["informative", "analytical", "critical"],
            "podcast_name": "InstaPod",
            "podcast_tagline": "Your AI powered podcast",
            "creativity": 0,
            "text_to_speech": {
                "output_directories": {
                    "transcripts": "./tmp/transcripts",
                    "audio": "./tmp/audio",
                }
            },
        }
        logger.info("Starting podcast audio generation")
        audio_file = generate_podcast(
            text=research_data,
            tts_model="gemini",
            conversation_config=custom_config,
            longform=True,
        )
        logger.info(f"Podcast audio generated successfully: {audio_file}")

        logger.info(f"Uploading podcast to file storage: {audio_file}")
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
        logger.info("Podcast uploaded successfully to storage")

        logger.info("Updating podcast status to READY")
        response = (
            supabase.table("podcasts")
            .update({"status": "READY"})
            .eq("id", podcast_id)
            .execute()
        )
        logger.info("Podcast status updated successfully")

        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(
            f"Podcast generation completed successfully in {execution_time:.2f} seconds"
        )

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "Podcast generation completed successfully",
                    "podcast_id": podcast_id,
                }
            ),
        }
    except Exception as e:
        logger.error(f"Lambda execution failed: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps(
                {"message": "Podcast generation failed", "error": str(e)}
            ),
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Process user ID and prompt")
    parser.add_argument("--podcastId", required=True, help="Podcast ID")
    args = parser.parse_args()
    podcast_id = args.podcastId

    try:
        # Create a mock event for local testing
        event = {"podcast_id": podcast_id}
        lambda_handler(event, None)
    except Exception as e:
        print(f"Script execution failed: {str(e)}", exc_info=True)
        raise
