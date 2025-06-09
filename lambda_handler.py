"""
Gotchas I Encountered
1. Moved imports into lambda_handler to reduce init (not sure if this was the actual reason, we can try moving back out)
2. Updated memory to 600MB in lambda. Max memory used was around 440MB from previous rounds
3. Updated Lambda architecture to use ARM to match my docker image and local development
4. Update timeout to 15mins. Default timeout is too short.
5. By default, AWS Lambda's filesystem is read-only, except for the /tmp directory. Updated output_directories to use /tmp instead of /data.
6. You need to update your lambda's docker image every time you push a new docker image to ECR. Seems obvious, but it's easy to forget.
Just add this step as part of your automation script or CI/CD pipeline
7. public.ecr.aws/lambda/python:3.11 doesn't come with ffmpeg. You need to install ffmpeg for the podcast generation to work.
8. Make sure to download the right ffmpeg binary for the architecture you are using (arm64 vs amd64)
"""

import json


def get_podcast_id(event):
    """
    Extract podcast_id from the event payload.
    Returns a tuple of (podcast_id, error_response).
    If podcast_id is found, error_response will be None.
    If there's an error, podcast_id will be None and error_response will contain the error details.
    """
    if isinstance(event.get("body"), str):
        try:
            body = json.loads(event["body"])
            podcast_id = body.get("podcast_id")
        except json.JSONDecodeError:
            return None, {
                "statusCode": 400,
                "body": json.dumps(
                    {
                        "message": "Invalid JSON body",
                        "error": "The request body must be valid JSON",
                    }
                ),
            }
    else:
        podcast_id = event.get("podcast_id")

    if not podcast_id:
        return None, {
            "statusCode": 400,
            "body": json.dumps(
                {
                    "message": "Missing required parameter",
                    "error": "podcast_id is required",
                }
            ),
        }

    return podcast_id, None


def lambda_handler(event, context):
    import time
    import json
    import os

    from dotenv import load_dotenv
    from supabase import Client, create_client
    from utils.podcast_generation_utils import generate_research_data
    from podcastfy.client import generate_podcast

    import logging

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.info("Handler Event Received " + str(event))

    logger.info("Lambda Handler Event Received")
    podcast_id, error_response = get_podcast_id(event)
    if error_response:
        return error_response

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
            # By default, AWS Lambda's filesystem is read-only, except for the /tmp  directory https://cloudcasts.io/article/lambda-limitations
            "text_to_speech": {
                "output_directories": {
                    "transcripts": "/tmp/transcripts",
                    "audio": "/tmp/audio",
                },
                "temp_audio_dir": "/tmp/audio/tmp",
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
