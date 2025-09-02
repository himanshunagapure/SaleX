"""
YouTube Scraper Main Interface
Simple 1-2 line interface for YouTube data extraction

Usage Examples:
1. Single URL extraction:
   python main.py --url "https://www.youtube.com/watch?v=VIDEO_ID"

2. Multiple URLs from file:
   python main.py --file urls.txt

3. Quick extraction with custom output:
   python main.py --url "https://www.youtube.com/@channel" --output my_data.json

4. Headless mode (faster):
   python main.py --urls "url1,url2,url3" --headless

5. Interactive mode:
   python main.py --interactive
"""

import asyncio
import argparse
import sys
import os
from typing import List, Optional

# Add parent directory to path to import database module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from yt_scraper.yt_data_extractor import AdvancedYouTubeExtractor
from database.mongodb_manager import get_mongodb_manager

class YouTubeScraperInterface:
    """Simple interface for YouTube data extraction"""
    
    def __init__(self, headless: bool = True, enable_anti_detection: bool = True, use_mongodb: bool = True):
        """Initialize the scraper interface"""
        self.headless = headless
        self.enable_anti_detection = enable_anti_detection
        self.use_mongodb = use_mongodb
        self.extractor = None
        
        # Initialize MongoDB manager if needed
        if self.use_mongodb:
            try:
                self.mongodb_manager = get_mongodb_manager()
                print("✅ MongoDB connection initialized")
            except Exception as e:
                print(f"⚠️ Failed to initialize MongoDB: {e}")
                self.use_mongodb = False
    
    async def scrape_single_url(self, url: str, output_file: str = "youtube_data.json") -> bool:
        """
        Scrape a single YouTube URL and save to file
        
        Args:
            url: YouTube URL to scrape
            output_file: Output file name
            
        Returns:
            bool: Success status
        """
        print(f"🎯 Scraping single URL: {url}")
        
        try:
            self.extractor = AdvancedYouTubeExtractor(
                headless=self.headless, 
                enable_anti_detection=self.enable_anti_detection
            )
            
            await self.extractor.start()
            
            # Extract data
            data = await self.extractor.extract_youtube_data(url)
            
            if data.get('error'):
                print(f"❌ Failed to extract data: {data['error']}")
                return False
            
            # Save to MongoDB if enabled
            if self.use_mongodb:
                try:
                    # Save to original YouTube collection
                    mongodb_stats = self.mongodb_manager.insert_batch_leads([data], 'youtube')
                    print(f"✅ Successfully scraped and saved to MongoDB (youtube_leads):")
                    print(f"   - Successfully inserted: {mongodb_stats['success_count']}")
                    print(f"   - Duplicates skipped: {mongodb_stats['duplicate_count']}")
                    print(f"   - Failed insertions: {mongodb_stats['failure_count']}")
                    
                    # Also save to unified collection
                    unified_stats = self.mongodb_manager.insert_and_transform_to_unified([data], 'youtube')
                    print(f"✅ Results also saved to unified_leads collection:")
                    print(f"   - Successfully transformed & inserted: {unified_stats['success_count']}")
                    print(f"   - Duplicates skipped: {unified_stats['duplicate_count']}")
                    print(f"   - Failed transformations: {unified_stats['failure_count']}")
                    
                except Exception as e:
                    print(f"❌ Error saving to MongoDB: {e}")
            
            # Save clean output to file as backup
            await self.extractor.save_clean_final_output([data], output_file)
            
            print(f"✅ Successfully scraped and saved to {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error scraping URL: {e}")
            return False
        finally:
            if self.extractor:
                await self.extractor.stop()
    
    async def scrape_multiple_urls(self, urls: List[str], output_file: str = "youtube_batch_data.json") -> bool:
        """
        Scrape multiple YouTube URLs and save to file
        
        Args:
            urls: List of YouTube URLs to scrape
            output_file: Output file name
            
        Returns:
            bool: Success status
        """
        print(f"🎯 Scraping {len(urls)} URLs...")
        
        try:
            self.extractor = AdvancedYouTubeExtractor(
                headless=self.headless, 
                enable_anti_detection=self.enable_anti_detection
            )
            
            await self.extractor.start()
            
            # Extract data first
            all_data = []
            for url in urls:
                try:
                    data = await self.extractor.extract_youtube_data(url)
                    if not data.get('error'):
                        all_data.append(data)
                except Exception as e:
                    print(f"❌ Error extracting data from {url}: {e}")
            
            # Save to file as backup
            final_output = await self.extractor.save_clean_final_output(all_data, output_file)
            
            # Save to MongoDB if enabled
            if self.use_mongodb and final_output:
                try:
                    mongodb_stats = self.mongodb_manager.insert_batch_leads(final_output, 'youtube')
                    print(f"✅ Successfully saved to MongoDB:")
                    print(f"   - Successfully inserted: {mongodb_stats['success_count']}")
                    print(f"   - Duplicates skipped: {mongodb_stats['duplicate_count']}")
                    print(f"   - Failed insertions: {mongodb_stats['failure_count']}")

                    # Also save to unified collection
                    unified_stats = self.mongodb_manager.insert_and_transform_to_unified(final_output, 'youtube')
                    print(f"✅ Results also saved to unified_leads collection:")
                    print(f"   - Successfully transformed & inserted: {unified_stats['success_count']}")
                    print(f"   - Duplicates skipped: {unified_stats['duplicate_count']}")
                    print(f"   - Failed transformations: {unified_stats['failure_count']}")
                except Exception as e:
                    print(f"❌ Error saving to MongoDB: {e}")
            

            
            print(f"✅ Successfully scraped {len(all_data)} URLs and saved to {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error scraping URLs: {e}")
            return False
        finally:
            if self.extractor:
                await self.extractor.stop()
    
    async def scrape_from_file(self, file_path: str, output_file: str = "youtube_file_data.json") -> bool:
        """
        Scrape URLs from a text file
        
        Args:
            file_path: Path to file containing URLs (one per line)
            output_file: Output file name
            
        Returns:
            bool: Success status
        """
        try:
            if not os.path.exists(file_path):
                print(f"❌ File not found: {file_path}")
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f.readlines() if line.strip() and line.strip().startswith('http')]
            
            if not urls:
                print(f"❌ No valid YouTube URLs found in {file_path}")
                return False
            
            print(f"📄 Found {len(urls)} URLs in {file_path}")
            return await self.scrape_multiple_urls(urls, output_file)
            
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return False
    
    async def interactive_mode(self):
        """Interactive mode for easy URL input"""
        print("🔥 YouTube Scraper - Interactive Mode")
        print("=" * 50)
        
        while True:
            print("\nOptions:")
            print("1. Scrape single URL")
            print("2. Scrape multiple URLs (comma-separated)")
            print("3. Scrape from file")
            print("4. Exit")
            
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == '1':
                url = input("Enter YouTube URL: ").strip()
                if url:
                    output = input("Output file name (press Enter for default): ").strip() or "youtube_data.json"
                    await self.scrape_single_url(url, output)
                
            elif choice == '2':
                urls_input = input("Enter URLs (comma-separated): ").strip()
                if urls_input:
                    urls = [url.strip() for url in urls_input.split(',') if url.strip()]
                    output = input("Output file name (press Enter for default): ").strip() or "youtube_batch_data.json"
                    await self.scrape_multiple_urls(urls, output)
                
            elif choice == '3':
                file_path = input("Enter file path: ").strip()
                if file_path:
                    output = input("Output file name (press Enter for default): ").strip() or "youtube_file_data.json"
                    await self.scrape_from_file(file_path, output)
                
            elif choice == '4':
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please enter 1-4.")


# Convenience functions for 1-2 line usage
async def quick_scrape(url: str, output: str = "yt_scraper/youtube_data.json", headless: bool = True) -> bool:
    """
    Quick single URL scraping in 1 line
    
    Usage:
        await quick_scrape("https://youtube.com/watch?v=VIDEO_ID")
    """
    scraper = YouTubeScraperInterface(headless=headless)
    return await scraper.scrape_single_url(url, output)

async def quick_batch_scrape(urls: List[str], output: str = "yt_scraper/youtube_batch_data.json", headless: bool = True) -> bool:
    """
    Quick multiple URLs scraping in 1 line
    
    Usage:
        await quick_batch_scrape(["url1", "url2", "url3"])
    """
    scraper = YouTubeScraperInterface(headless=headless)
    return await scraper.scrape_multiple_urls(urls, output)

async def quick_file_scrape(file_path: str, output: str = "yt_scraper/youtube_file_data.json", headless: bool = True) -> bool:
    """
    Quick file-based scraping in 1 line
    
    Usage:
        await quick_file_scrape("urls.txt")
    """
    scraper = YouTubeScraperInterface(headless=headless)
    return await scraper.scrape_from_file(file_path, output)


def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(
        description="YouTube Data Scraper - Extract data from YouTube videos, shorts, and channels",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --url "https://www.youtube.com/watch?v=VIDEO_ID"
  python main.py --urls "url1,url2,url3" --output my_data.json
  python main.py --file urls.txt --headless
  python main.py --interactive
        """
    )
    
    # Mutually exclusive group for input methods
    input_group = parser.add_mutually_exclusive_group(required=False)
    input_group.add_argument('--url', help='Single YouTube URL to scrape')
    input_group.add_argument('--urls', help='Multiple YouTube URLs (comma-separated)')
    input_group.add_argument('--file', help='File containing YouTube URLs (one per line)')
    input_group.add_argument('--interactive', action='store_true', help='Start interactive mode')
    
    # Optional arguments
    parser.add_argument('--output', '-o', default='youtube_scraped_data.json', 
                       help='Output file name (default: youtube_scraped_data.json)')
    parser.add_argument('--headless', action='store_true', default=True,
                       help='Run in headless mode (default: True)')
    parser.add_argument('--show-browser', action='store_true',
                       help='Show browser window (opposite of headless)')
    parser.add_argument('--no-anti-detection', action='store_true',
                       help='Disable anti-detection features')
    
    args = parser.parse_args()
    
    # Handle show-browser flag
    headless_mode = args.headless and not args.show_browser
    anti_detection = not args.no_anti_detection
    
    async def run_scraper():
        scraper = YouTubeScraperInterface(headless=headless_mode, enable_anti_detection=anti_detection)
        
        if args.interactive:
            await scraper.interactive_mode()
        elif args.url:
            success = await scraper.scrape_single_url(args.url, args.output)
            sys.exit(0 if success else 1)
        elif args.urls:
            urls = [url.strip() for url in args.urls.split(',') if url.strip()]
            success = await scraper.scrape_multiple_urls(urls, args.output)
            sys.exit(0 if success else 1)
        elif args.file:
            success = await scraper.scrape_from_file(args.file, args.output)
            sys.exit(0 if success else 1)
        else:
            # No arguments provided, show help and start interactive mode
            parser.print_help()
            print("\n🔥 Starting interactive mode...")
            await scraper.interactive_mode()
    
    # Run the async function
    try:
        asyncio.run(run_scraper())
    except KeyboardInterrupt:
        print("\n👋 Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()