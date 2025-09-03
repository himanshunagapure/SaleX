"""
Example Usage of Instagram Scraper
Demonstrates how to use the scraper with simple one-line calls
"""

import asyncio
from instagram_scraper.main import InstagramScraper, scrape_instagram_urls


async def example_1_simple_usage():
    """Example 1: Simple one-line usage"""
    print("=" * 60)
    print("EXAMPLE 1: Simple One-Line Usage")
    print("=" * 60)
    
    # List of Instagram URLs to scrape
    urls = [
        "https://www.instagram.com/90svogue.__",
        "https://www.instagram.com/p/DMQMR4IzyJb/",
        "https://www.instagram.com/reel/CSb6-Rap2Ip/"
    ]
    
    # One-line scraping call
    result = await scrape_instagram_urls(urls)
    
    print(f"✅ Scraping completed!")
    print(f"   Success: {result['success']}")
    print(f"   Data entries: {len(result['data'])}")
    print(f"   Success rate: {result['summary']['success_rate']:.1f}%")
    
    return result


async def example_2_with_options():
    """Example 2: Using with custom options"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Custom Options")
    print("=" * 60)
    
    urls = [
        "https://www.instagram.com/90svogue.__",
        "https://www.instagram.com/codehype_"
    ]
    
    # Scraping with custom options
    result = await scrape_instagram_urls(
        urls=urls,
        headless=False,  # Show browser window
        enable_anti_detection=True,
        is_mobile=True,  # Use mobile mode
        output_file="instagram_scraper/custom_output.json"
    )
    
    print(f"✅ Custom scraping completed!")
    print(f"   Success: {result['success']}")
    print(f"   Data entries: {len(result['data'])}")
    print(f"   Output file: {result['output_file']}")
    
    return result


async def example_3_class_usage():
    """Example 3: Using the InstagramScraper class directly"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Class Usage")
    print("=" * 60)
    
    urls = [
        "https://www.instagram.com/90svogue.__"
    ]
    
    # Create scraper instance
    scraper = InstagramScraper(
        headless=True,
        enable_anti_detection=True,
        is_mobile=False,
        output_file="instagram_scraper/class_output.json"
    )
    
    # Use the scraper
    result = await scraper.scrape(urls)
    
    print(f"✅ Class-based scraping completed!")
    print(f"   Success: {result['success']}")
    print(f"   Data entries: {len(result['data'])}")
    print(f"   Output file: {result['output_file']}")
    
    return result


async def example_4_batch_processing():
    """Example 4: Batch processing with error handling"""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Batch Processing")
    print("=" * 60)
    
    # Large batch of URLs
    # urls = [
    #     "https://www.instagram.com/90svogue.__",
    #     "https://www.instagram.com/p/DMQMR4IzyJb/",
    #     "https://www.instagram.com/reel/CSb6-Rap2Ip/",
    #     "https://www.instagram.com/invalid_url_123/",  # Invalid
    #     "https://about.instagram.com/about-us/careers", # Invalid
    #     "https://www.teitch.com/akira/" # Invalid
    # ]
    urls = [
        "https://www.instagram.com/p/DMQMR4IzyJb/"
    ]
    result = await scrape_instagram_urls(
        urls=urls,
        headless=True,
        enable_anti_detection=True,
        output_file="instagram_scraper/batch_output.json"
    )
    
    print(f"✅ Batch processing completed!")
    print(f"   Total URLs: {result['summary']['total_original_urls']}")
    print(f"   Additional profiles: {result['summary']['additional_profiles_extracted']}")
    print(f"   Total extractions: {result['summary']['total_extractions']}")
    print(f"   Successful: {result['summary']['successful_extractions']}")
    print(f"   Failed: {result['summary']['failed_extractions']}")
    print(f"   Success rate: {result['summary']['success_rate']:.1f}%")
    
    if result['errors']:
        print(f"\n❌ Errors encountered:")
        for error in result['errors']:
            print(f"   - {error['url']}: {error['error']}")
    
    return result


async def example_5_data_access():
    """Example 5: Accessing the scraped data"""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Data Access")
    print("=" * 60)
    
    urls = [
        "https://www.instagram.com/90svogue.__",
        "https://www.instagram.com/p/DMQMR4IzyJb/"
    ]
    
    result = await scrape_instagram_urls(urls)
    
    if result['success'] and result['data']:
        print("📋 Extracted Data:")
        for i, entry in enumerate(result['data'], 1):
            print(f"\n{i}. {entry['url']}")
            print(f"   Content Type: {entry['content_type']}")
            
            if entry['content_type'] == 'profile':
                print(f"   Username: @{entry.get('username', 'N/A')}")
                print(f"   Full Name: {entry.get('full_name', 'N/A')}")
                print(f"   Followers: {entry.get('followers_count', 'N/A')}")
                print(f"   Following: {entry.get('following_count', 'N/A')}")
                print(f"   Verified: {entry.get('is_verified', 'N/A')}")
                print(f"   Business Account: {entry.get('is_business_account', 'N/A')}")
                if entry.get('business_email'):
                    print(f"   Business Email: {entry['business_email']}")
                
            elif entry['content_type'] in ['article', 'video']:
                print(f"   Username: @{entry.get('username', 'N/A')}")
                print(f"   Likes: {entry.get('likes_count', 'N/A')}")
                print(f"   Comments: {entry.get('comments_count', 'N/A')}")
                if entry.get('caption'):
                    caption = entry['caption'][:100] + "..." if len(entry['caption']) > 100 else entry['caption']
                    print(f"   Caption: {caption}")
    
    return result


async def main():
    """Run all examples"""
    print("Instagram Scraper - Example Usage")
    print("=" * 80)
    
    # Run all examples
    #await example_1_simple_usage()
    #await example_2_with_options()
    #await example_3_class_usage()
    await example_4_batch_processing()
    #wait example_5_data_access()
    
    print("\n" + "=" * 80)
    print("ALL EXAMPLES COMPLETED!")
    print("=" * 80)
    print("\n📝 Usage Summary:")
    print("   1. Simple: result = await scrape_instagram_urls(urls)")
    print("   2. With options: result = await scrape_instagram_urls(urls, headless=False, is_mobile=True)")
    print("   3. Class-based: scraper = InstagramScraper(); result = await scraper.scrape(urls)")
    print("   4. The result contains: data, summary, errors, success status")
    print("   5. Data is automatically saved if output_file is specified")


if __name__ == "__main__":
    asyncio.run(main()) 