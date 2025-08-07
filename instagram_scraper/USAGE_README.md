# Instagram Scraper - Usage Guide

A powerful Instagram scraper with anti-detection features that can extract data from profiles, posts, and reels with just one line of code.

## Quick Start

### Basic Usage (One Line)

```python
import asyncio
from main import scrape_instagram_urls

# Your Instagram URLs
urls = [
    "https://www.instagram.com/username/",
    "https://www.instagram.com/p/post_id/",
    "https://www.instagram.com/reel/reel_id/"
]

# Scrape with one line
result = await scrape_instagram_urls(urls)
```

### Advanced Usage

```python
import asyncio
from main import InstagramScraper

# Create scraper with custom options
scraper = InstagramScraper(
    headless=False,  # Show browser window
    enable_anti_detection=True,
    is_mobile=True,  # Use mobile mode
    output_file="my_results.json"
)

# Scrape URLs
result = await scraper.scrape(urls)
```

## Installation

1. Install dependencies:
```bash
pip install playwright beautifulsoup4 asyncio
playwright install chromium
```

2. Run the scraper:
```bash
python main.py
```

## Features

- ✅ **Anti-Detection**: Advanced fingerprint evasion and behavioral mimicking
- ✅ **Multiple Content Types**: Profiles, posts, and reels
- ✅ **Clean Output**: Structured JSON data
- ✅ **Error Handling**: Robust error handling and reporting
- ✅ **Batch Processing**: Process multiple URLs efficiently
- ✅ **Mobile/Desktop**: Support for both mobile and desktop modes

## Output Format

The scraper returns a dictionary with the following structure:

```python
{
    'success': True,  # Overall success status
    'data': [        # List of scraped data objects
        {
            'url': 'https://www.instagram.com/username/',
            'content_type': 'profile',
            'username': 'username',
            'full_name': 'Full Name',
            'followers_count': '1.2K',
            'following_count': '500',
            'biography': 'Bio text...',
            'is_verified': True,
            'is_business_account': False,
            'business_email': 'email@example.com',
            'business_phone_number': None,
            'business_category_name': None
        },
        {
            'url': 'https://www.instagram.com/p/post_id/',
            'content_type': 'article',
            'username': 'username',
            'likes_count': '1.5K',
            'comments_count': '123',
            'caption': 'Post caption...',
            'post_date': 'January 1, 2024'
        }
    ],
    'summary': {     # Summary statistics
        'total_original_urls': 2,
        'additional_profiles_extracted': 1,
        'total_extractions': 3,
        'successful_extractions': 3,
        'failed_extractions': 0,
        'success_rate': 100.0,
        'total_time_seconds': 15.5,
        'average_time_per_url': 7.75,
        'content_type_breakdown': {'profile': 2, 'article': 1}
    },
    'errors': [],    # List of any errors encountered
    'output_file': 'results.json',  # Path to saved file (if specified)
    'stealth_report': {...}  # Anti-detection status report
}
```

## Content Types

### Profile Data
- Username and full name
- Follower and following counts
- Biography and bio links
- Verification status
- Business account information
- Business contact details

### Post/Reel Data
- Username of author
- Like and comment counts
- Caption text
- Post date
- Content type (article/video)

## Configuration Options

### InstagramScraper Class

```python
scraper = InstagramScraper(
    headless=True,              # Run browser in background
    enable_anti_detection=True, # Enable anti-detection features
    is_mobile=False,           # Use mobile user agent
    output_file=None           # Optional file to save results
)
```

### scrape_instagram_urls Function

```python
result = await scrape_instagram_urls(
    urls,                      # List of Instagram URLs
    headless=True,             # Run browser in background
    enable_anti_detection=True, # Enable anti-detection features
    is_mobile=False,           # Use mobile user agent
    output_file=None           # Optional file to save results
)
```

## Examples

### Example 1: Simple Scraping
```python
import asyncio
from main import scrape_instagram_urls

async def main():
    urls = ["https://www.instagram.com/username/"]
    result = await scrape_instagram_urls(urls)
    
    if result['success']:
        for entry in result['data']:
            print(f"Username: @{entry['username']}")
            print(f"Followers: {entry['followers_count']}")

asyncio.run(main())
```

### Example 2: Batch Processing
```python
import asyncio
from main import scrape_instagram_urls

async def main():
    urls = [
        "https://www.instagram.com/user1/",
        "https://www.instagram.com/user2/",
        "https://www.instagram.com/p/post1/",
        "https://www.instagram.com/reel/reel1/"
    ]
    
    result = await scrape_instagram_urls(
        urls=urls,
        output_file="batch_results.json"
    )
    
    print(f"Processed {result['summary']['total_original_urls']} URLs")
    print(f"Additional profiles extracted: {result['summary']['additional_profiles_extracted']}")
    print(f"Total extractions: {result['summary']['total_extractions']}")
    print(f"Success rate: {result['summary']['success_rate']:.1f}%")

asyncio.run(main())
```

### Example 3: Mobile Mode
```python
import asyncio
from main import scrape_instagram_urls

async def main():
    urls = ["https://www.instagram.com/username/"]
    
    result = await scrape_instagram_urls(
        urls=urls,
        is_mobile=True,  # Use mobile user agent
        headless=False   # Show browser window
    )

asyncio.run(main())
```

## Error Handling

The scraper includes comprehensive error handling:

```python
result = await scrape_instagram_urls(urls)

if not result['success']:
    print("Some URLs failed to scrape")
    
for error in result['errors']:
    print(f"Error with {error['url']}: {error['error']}")
```

## Anti-Detection Features

The scraper includes advanced anti-detection measures:

- **Fingerprint Evasion**: Randomizes browser fingerprints
- **Behavioral Mimicking**: Simulates human-like behavior
- **Network Obfuscation**: Varies request timing and patterns
- **User Agent Rotation**: Uses realistic browser user agents
- **Geographic Logic**: Matches timezones to platforms

## Command Line Usage

Run the scraper interactively:

```bash
python main.py
```

This will prompt you for:
- Instagram URLs to scrape
- Scraper options (headless, anti-detection, mobile mode)
- Output file name

## File Structure

```
insta-scraper/
├── main.py                    # Main entry point
├── example_usage.py          # Usage examples
├── src/
│   ├── advanced_graphql_extractor.py  # Core extraction logic
│   ├── anti_detection.py             # Anti-detection features
│   └── browser_manager.py            # Browser management
└── USAGE_README.md           # This file
```

## Troubleshooting

### Common Issues

1. **Browser not found**: Run `playwright install chromium`
2. **Rate limiting**: Enable anti-detection features
3. **Invalid URLs**: Ensure URLs are valid Instagram links
4. **Permission errors**: Run with appropriate file permissions

### Performance Tips

- Use `headless=True` for faster execution
- Process URLs in batches for better performance
- Enable anti-detection to avoid rate limiting
- Use mobile mode if desktop mode fails

## License

This scraper is for educational purposes only. Please respect Instagram's terms of service and rate limits. 