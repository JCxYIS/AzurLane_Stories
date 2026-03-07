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

    print(f"Initializing StoryReader with data dir: {args.data_dir}")
    try:
        reader = StoryReader(data_dir=args.data_dir)
        parsed_stories = reader.get_parsed_stories()
        print(f"Successfully loaded and parsed {len(parsed_stories)} story groups.")
    except Exception as e:
        print("Failed to read story data.")
        traceback.print_exc()
        sys.exit(1)

    print(f"Initializing MarkdownWriter with output dir: {args.out_dir}")
    try:
        writer = MarkdownWriter(output_dir=args.out_dir)
        writer.generate_stories(
            parsed_stories=parsed_stories,
            story_reader=reader,
            overwrite=args.overwrite
        )
        print("Done generating markdown stories.")
    except Exception as e:
        print("Failed to write markdown stories.")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
