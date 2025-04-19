#!/usr/bin/env python3

import argparse


def main():
    # Create argument parser
    parser = argparse.ArgumentParser(description="Process user ID and prompt")

    # Add required arguments
    parser.add_argument("--userId", required=True, help="User ID")
    parser.add_argument("--prompt", required=True, help="User prompt")

    # Parse arguments
    args = parser.parse_args()

    # Access the arguments
    user_id = args.userId
    user_prompt = args.prompt

    # Print the received values (you can replace this with your actual logic)
    print(f"User ID: {user_id}")
    print(f"User Prompt: {user_prompt}")


if __name__ == "__main__":
    main()
