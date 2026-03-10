import argparse
import sys
import traceback
import traceback
from story_reader import StoryReader
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

    args = parser.parse_args()

    regions = ["CN", "EN", "JP", "KR", "TW"]
    
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
            
            for group_id, data in parsed_stories.items():
                if group_id not in aggregated_stories:
                    aggregated_stories[group_id] = {"titles": {}, "regions": {}, "type": data.get("type", 0)}
                
                aggregated_stories[group_id]["regions"][region] = data["chapters"]
                aggregated_stories[group_id]["titles"][region] = data["title"]
                
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
