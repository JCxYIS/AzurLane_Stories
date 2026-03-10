import argparse
import sys
import traceback
from story_reader import StoryReader
from markdown_writer import MarkdownWriter

def main():
    parser = argparse.ArgumentParser(description="Parse AzureLane JP story data to Markdown.")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing markdown files. If not set, existing files are skipped."
    )
    # Allows specifying a different data directory if needed, defaulting to the structure requested
    parser.add_argument(
        "--data-dir",
        type=str,
        default="f:/AZL_ScriptSite/AzurLaneData",
        help="Path to the AzurLaneData directory."
    )
    parser.add_argument(
        "--out-dir",
        type=str,
        default="f:/AZL_ScriptSite/output/stories",
        help="Path to the output stories directory."
    )

    args = parser.parse_args()

    regions = ["CN", "EN", "JP", "KR", "TW"]
    print(f"Initializing MarkdownWriter with output dir: {args.out_dir}")
    writer = MarkdownWriter(output_dir=args.out_dir)

    for region in regions:
        print(f"\n--- Processing Region: {region} ---")
        try:
            reader = StoryReader(data_dir=args.data_dir, region=region)
            parsed_stories = reader.get_parsed_stories()
            print(f"Successfully loaded and parsed {len(parsed_stories)} story groups for {region}.")
        except Exception as e:
            print(f"Failed to read story data for {region}.")
            traceback.print_exc()
            continue

        try:
            writer.generate_stories(
                parsed_stories=parsed_stories,
                story_reader=reader,
                overwrite=args.overwrite
            )
            print(f"Done generating markdown stories for {region}.")
        except Exception as e:
            print(f"Failed to write markdown stories for {region}.")
            traceback.print_exc()
            continue

    print("\nDone generating markdown stories for all regions.")

if __name__ == "__main__":
    main()
