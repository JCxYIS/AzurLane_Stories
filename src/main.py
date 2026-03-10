import argparse
import sys
import traceback
from story_reader import StoryReader
from markdown_writer import MarkdownWriter
from html_writer import HtmlWriter

def main():
    parser = argparse.ArgumentParser(description="Parse AzureLane JP story data to Markdown or HTML.")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing markdown/html files. If not set, existing files are skipped."
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
    parser.add_argument(
        "--format",
        type=str,
        default="html",
        choices=["html", "markdown"],
        help="Format to output: 'html' (default) or 'markdown'."
    )

    args = parser.parse_args()

    regions = ["CN", "EN", "JP", "KR", "TW"]
    
    if args.format == "markdown":
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
    
    elif args.format == "html":
        print(f"Initializing HtmlWriter with output dir: {args.out_dir}")
        writer = HtmlWriter(output_dir=args.out_dir)
        
        aggregated_stories = {}
        story_readers_by_region = {}
        
        for region in regions:
            print(f"\n--- Processing Region: {region} ---")
            try:
                reader = StoryReader(data_dir=args.data_dir, region=region)
                parsed_stories = reader.get_parsed_stories()
                story_readers_by_region[region] = reader
                print(f"Successfully loaded and parsed {len(parsed_stories)} story groups for {region}.")
                
                for group, chapters in parsed_stories.items():
                    if group not in aggregated_stories:
                        aggregated_stories[group] = {}
                    aggregated_stories[group][region] = chapters
                    
            except Exception as e:
                print(f"Failed to read story data for {region}.")
                traceback.print_exc()
                continue
                
        # Generate all html pages
        try:
            writer.generate_stories(
                aggregated_stories=aggregated_stories,
                story_readers_by_region=story_readers_by_region,
                overwrite=args.overwrite
            )
            print("\nDone generating html stories for all regions.")
        except Exception as e:
            print(f"Failed to write html stories.")
            traceback.print_exc()

if __name__ == "__main__":
    main()
