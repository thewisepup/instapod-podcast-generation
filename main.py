from podcastfy.client import generate_podcast
import google.generativeai as genai

urls = ["https://www.youtube.com/watch?v=YE4ra6U0ca4&t=23s"]
topic = "Latest news on the Trump tarrifs and how it affects the stock market. I am a software engineer an start up founder and I want to know how it affects my job."

text = open("mock_text.txt", "r").read()
transcript = "data/transcripts/transcript_e63c4c6457be4cfbb035f265a3c870df.txt"
custom_config = {
    "conversation_style": ["informative", "analytical", "critical"],
    "podcast_name": "InstaPod",
    "podcast_tagline": "Your AI powered podcast",
    "creativity": 0,
}


# generate_podcast(
#     text=text,
#     tts_model="elevenlabs",
#     conversation_config=custom_config,
#     transcript_only=True,
#     longform=True,
# )
# Generate podcast from existing transcript file
audio_file_from_transcript = generate_podcast(
    transcript_file="./data/transcripts/transcript_019ce6311dfa424dbd65d906dded55ca.txt",
    tts_model="elevenlabs",
)
print(audio_file_from_transcript)
