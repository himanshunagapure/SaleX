# Advanced GraphQL Extractor - Complete System Flow Documentation

## Overview

The `advanced_graphql_extractor.py` is a sophisticated Instagram data extraction tool that uses browser automation with network request interception to capture and parse GraphQL API responses. This document provides a comprehensive technical breakdown of how the entire system works, from initialization to cleanup, including all anti-detection features and data processing capabilities.

## Complete System Flow

### 1. System Architecture Overview

The system follows a layered architecture with three main components working together:

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                        │
│  test_complete_flow_anti_detection.py                          │
│  - Entry point for testing and usage                           │
│  - Configures extraction parameters                            │
│  - Manages test scenarios (desktop/mobile modes)               │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                 EXTRACTION LAYER                               │
│  AdvancedGraphQLExtractor (advanced_graphql_extractor.py)      │
│  - Orchestrates the entire extraction process                  │
│  - Manages network request monitoring                          │
│  - Handles data parsing and formatting                         │
│  - Provides clean output generation                            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                 BROWSER MANAGEMENT LAYER                       │
│  BrowserManager (browser_manager.py)                           │
│  - Manages Playwright browser automation                       │
│  - Handles page navigation and popup management                │
│  - Integrates with anti-detection features                     │
│  - Provides human-like behavior simulation                     │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                 ANTI-DETECTION LAYER                           │
│  AntiDetectionManager (anti_detection.py)                      │
│  - Manages fingerprint evasion                                 │
│  - Handles behavioral mimicking                                │
│  - Controls network obfuscation                                │
│  - Provides stealth reporting                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Detailed System Flow

#### Phase 1: Initialization and Setup

**Step 1.1: User Input Processing**
```python
# From test_complete_flow_anti_detection.py
urls = [
    "https://www.instagram.com/90svogue.__",  # Profile
    "https://www.instagram.com/codehype_",    # Profile
    "https://www.instagram.com/p/DMsercXMVeZ/",    # Post
    "https://www.instagram.com/reel/CSb6-Rap2Ip/"  # Reel
]

# Mode selection (Desktop/Mobile)
test_modes = [
    {"name": "Desktop Mode", "is_mobile": False},
    {"name": "Mobile Mode", "is_mobile": True}
]
```

**Step 1.2: AdvancedGraphQLExtractor Initialization**
```python
# From advanced_graphql_extractor.py
extractor = AdvancedGraphQLExtractor(
    headless=True,
    enable_anti_detection=True,
    is_mobile=mode['is_mobile']
)
```

**Step 1.3: BrowserManager Initialization**
```python
# From browser_manager.py
class BrowserManager:
    def __init__(self, headless: bool = True, enable_anti_detection: bool = True, is_mobile: bool = False):
        self.headless = headless
        self.enable_anti_detection = enable_anti_detection
        self.is_mobile = is_mobile
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.ua = UserAgent()
        
        # Initialize anti-detection manager
        if self.enable_anti_detection:
            self.anti_detection = AntiDetectionManager(
                enable_fingerprint_evasion=True,
                enable_behavioral_mimicking=True,
                enable_network_obfuscation=True
            )
```

**Step 1.4: AntiDetectionManager Initialization**
```python
# From anti_detection.py
class AntiDetectionManager:
    def __init__(self, 
                 enable_fingerprint_evasion: bool = True,
                 enable_behavioral_mimicking: bool = True,
                 enable_network_obfuscation: bool = True):
        
        self.enable_fingerprint_evasion = enable_fingerprint_evasion
        self.enable_behavioral_mimicking = enable_behavioral_mimicking
        self.enable_network_obfuscation = enable_network_obfuscation
        
        # Initialize fingerprint data
        self.fingerprint_data = self._initialize_fingerprint_data()
        
        # Initialize behavioral state
        self.behavioral_state = {
            'last_action_time': time.time(),
            'total_actions': 0,
            'current_session_duration': 0,
            'mouse_positions': [],
            'scroll_positions': [],
            'click_positions': []
        }
        
        # Initialize network state
        self.network_state = {
            'request_count': 0,
            'last_request_time': time.time(),
            'request_spacing': [],
            'connection_errors': 0
        }
```

#### Phase 2: Browser Startup and Anti-Detection Setup

**Step 2.1: Playwright Initialization**
```python
# From browser_manager.py
async def start(self) -> None:
    self.playwright = await async_playwright().start()
```

**Step 2.2: Stealth Browser Context Creation**
```python
# From browser_manager.py
if self.enable_anti_detection and self.anti_detection:
    # Use advanced anti-detection configuration
    self.browser, self.context = await create_stealth_browser_context(
        self.playwright, self.anti_detection, is_mobile=self.is_mobile
    )
```

**Step 2.3: Anti-Detection Context Setup**
```python
# From anti_detection.py
async def create_stealth_browser_context(playwright, anti_detection_manager: AntiDetectionManager, is_mobile: bool = False):
    # Generate stealth context options
    context_options = await anti_detection_manager.generate_stealth_context_options(is_mobile)
    
    # Launch browser with stealth arguments
    browser = await playwright.chromium.launch(
        headless=context_options.get('headless', True),
        args=context_options.get('browser_args', [])
    )
    
    # Create context with stealth configuration
    context = await browser.new_context(**context_options.get('context_options', {}))
    
    # Add stealth scripts
    stealth_scripts = await anti_detection_manager.generate_stealth_scripts()
    for script in stealth_scripts:
        await context.add_init_script(script)
    
    return browser, context
```

**Step 2.4: Network Monitoring Setup**
```python
# From advanced_graphql_extractor.py
async def _setup_network_monitoring(self) -> None:
    # Listen for network requests using proper event handling
    self.browser_manager.page.on("request", self._on_request)
    self.browser_manager.page.on("response", self._on_response)
```

#### Phase 3: URL Processing and Navigation

**Step 3.1: URL Processing Loop**
```python
# From advanced_graphql_extractor.py
async def extract_and_save_clean_data_from_urls(self, urls: List[str], filename: str = "instagram_final_output.json") -> None:
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Processing: {url}")
        
        try:
            # Extract data from the URL
            extracted_data = await self.extract_graphql_data(url)
```

**Step 3.2: Navigation with Anti-Detection**
```python
# From browser_manager.py
async def navigate_to_with_popup_close(self, url: str, wait_time: int = 3) -> bool:
    # Navigate to URL
    await self.navigate_to(url, wait_time)
    
    # Try to close popup
    popup_closed = await self.close_instagram_popup()
    
    return popup_closed
```

**Step 3.3: Anti-Detection Navigation Delays**
```python
# From browser_manager.py
async def navigate_to(self, url: str, wait_time: int = 3) -> None:
    # Apply network obfuscation delay
    if self.enable_anti_detection and self.anti_detection:
        delay = await self.anti_detection.calculate_request_delay()
        await asyncio.sleep(delay)
    else:
        # Random delay to mimic human behavior
        await asyncio.sleep(random.uniform(1, 3))
    
    await self.page.goto(url, wait_until='domcontentloaded')
```

#### Phase 4: Network Request Monitoring and Data Capture

**Step 4.1: Request Interception**
```python
# From advanced_graphql_extractor.py
async def _on_request(self, request) -> None:
    url = request.url
    
    # Filter for GraphQL and API requests
    if any(keyword in url for keyword in [
        '/graphql/', '/api/', 'graphql.instagram.com', 'graphql/query',
        'instagram.com/api/v1', 'instagram.com/api/v2',
        'instagram.com/graphql/query', 'instagram.com/graphql/ig_app_id'
    ]):
        req_data = {
            'type': 'request',
            'url': url,
            'method': request.method,
            'headers': dict(request.headers),
            'post_data': request.post_data,
            'timestamp': time.time()
        }
        self.network_requests.append(req_data)
```

**Step 4.2: Response Processing**
```python
# From advanced_graphql_extractor.py
async def _on_response(self, response) -> None:
    url = response.url
    
    # Filter for GraphQL and API responses
    if any(keyword in url for keyword in [
        '/graphql/', '/api/', 'graphql.instagram.com', 'graphql/query',
        'instagram.com/api/v1', 'instagram.com/api/v2',
        'instagram.com/graphql/query', 'instagram.com/graphql/ig_app_id'
    ]):
        try:
            # Try to get response body
            body = await response.body()
            content_type = response.headers.get('content-type', '')
            
            # Process JSON responses
            if 'application/json' in content_type or 'text/javascript' in content_type:
                try:
                    if body:
                        # Handle potential zstd compression
                        if 'zstd' in content_type:
                            import zstandard as zstd
                            dctx = zstd.ZstdDecompressor()
                            decompressed = dctx.decompress(body)
                            text_body = decompressed.decode('utf-8')
                        else:
                            text_body = body.decode('utf-8')
                        
                        # Remove potential "for (;;);" prefix
                        if text_body.startswith('for (;;);'):
                            text_body = text_body[9:]
                        
                        json_data = json.loads(text_body)
                        
                        # Store GraphQL responses
                        if any(keyword in url for keyword in ['/graphql/', 'graphql.instagram.com']):
                            self.graphql_responses[url] = json_data
                        
                        # Store API responses
                        if '/api/v1/' in url:
                            self.api_responses = getattr(self, 'api_responses', {})
                            self.api_responses[url] = json_data
```

#### Phase 5: Data Extraction and Processing

**Step 5.1: Multi-Source Data Extraction**
```python
# From advanced_graphql_extractor.py
async def extract_graphql_data(self, url: str) -> Dict[str, Any]:
    # Extract data from different sources
    extracted_data = {
        'url': url,
        'popup_closed': popup_closed,
        'html_length': len(html_content),
        'text_length': len(rendered_text),
        'network_requests': len(self.network_requests),
        'graphql_responses': len(self.graphql_responses),
        'api_responses': len(getattr(self, 'api_responses', {})),
        'graphql_data': {},
        'api_data': {},
        'user_data': {},
        'meta_data': {},
        'script_data': {},
        'page_analysis': {}
    }
    
    # 1. Extract GraphQL data from network responses
    extracted_data['graphql_data'] = self.graphql_responses
    
    # 2. Extract API data from network responses
    extracted_data['api_data'] = getattr(self, 'api_responses', {})
    
    # 3. Extract user data from successful API responses
    user_data = await self._extract_user_data_from_api()
    extracted_data['user_data'] = user_data
    
    # 4. Extract meta data
    meta_data = await self._extract_meta_data(html_content)
    extracted_data['meta_data'] = meta_data
    
    # 5. Extract data from scripts
    script_data = await self._extract_script_data(html_content)
    extracted_data['script_data'] = script_data
    
    # 6. Analyze page content
    page_analysis = await self._analyze_page_content(rendered_text, html_content)
    extracted_data['page_analysis'] = page_analysis
    
    # 7. Analyze network requests
    network_analysis = await self._analyze_network_requests()
    extracted_data['network_analysis'] = network_analysis
```

**Step 5.2: API Data Extraction**
```python
# From advanced_graphql_extractor.py
async def _extract_user_data_from_api(self) -> Dict[str, Any]:
    user_data = {}
    
    # Look for web_profile_info API response
    for url, response in getattr(self, 'api_responses', {}).items():
        if 'web_profile_info' in url and 'data' in response:
            user_info = response.get('data', {}).get('user', {})
            if user_info:
                user_data.update({
                    'username': user_info.get('username'),
                    'full_name': user_info.get('full_name'),
                    'biography': user_info.get('biography'),
                    'profile_pic_url': user_info.get('profile_pic_url'),
                    'profile_pic_url_hd': user_info.get('profile_pic_url_hd'),
                    'is_private': user_info.get('is_private'),
                    'is_verified': user_info.get('is_verified'),
                    'is_business_account': user_info.get('is_business_account'),
                    'followers_count': user_info.get('edge_followed_by', {}).get('count'),
                    'following_count': user_info.get('edge_follow', {}).get('count'),
                    'posts_count': user_info.get('edge_owner_to_timeline_media', {}).get('count'),
                    'user_id': user_info.get('id'),
                    'external_url': user_info.get('external_url'),
                    'has_public_story': user_info.get('has_public_story'),
                    'is_live': user_info.get('is_live'),
                    # Business-related fields
                    'business_email': user_info.get('business_email'),
                    'business_phone_number': user_info.get('business_phone_number'),
                    'business_category_name': user_info.get('business_category_name'),
                    'is_professional_account': user_info.get('is_professional_account'),
                    'bio_links': user_info.get('bio_links', [])
                })
                break
```

**Step 5.3: Meta Data Extraction**
```python
# From advanced_graphql_extractor.py
async def _extract_meta_data(self, html_content: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html_content, 'html.parser')
    meta_data = {}
    
    # Extract all meta tags
    meta_tags = soup.find_all('meta')
    for meta in meta_tags:
        name = meta.get('name') or meta.get('property')
        content = meta.get('content')
        if name and content:
            meta_data[name] = content
    
    # Extract Open Graph data
    og_meta = {}
    og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
    for og_tag in og_tags:
        property_name = og_tag.get('property')
        content = og_tag.get('content')
        if property_name and content:
            og_meta[property_name] = content
    meta_data['open_graph'] = og_meta
    
    # Enhanced parsing for Instagram-specific data
    enhanced_data = self._parse_instagram_meta_data(meta_data)
    meta_data.update(enhanced_data)
    
    return meta_data
```

**Step 5.4: Script Data Extraction**
```python
# From advanced_graphql_extractor.py
async def _extract_script_data(self, html_content: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html_content, 'html.parser')
    script_data = {}
    
    scripts = soup.find_all('script')
    
    for i, script in enumerate(scripts):
        if script.string:
            script_content = script.string
            
            # Look for various data patterns with more specific matching
            patterns = [
                # Profile-specific patterns
                (r'"username"\s*:\s*"([^"]+)"', 'username'),
                (r'"full_name"\s*:\s*"([^"]+)"', 'full_name'),
                (r'"biography"\s*:\s*"([^"]+)"', 'biography'),
                # Business-related patterns
                (r'"business_email"\s*:\s*"([^"]*)"', 'business_email'),
                (r'"business_phone_number"\s*:\s*"([^"]*)"', 'business_phone_number'),
                (r'"business_category_name"\s*:\s*"([^"]*)"', 'business_category_name'),
                # Post-specific patterns
                (r'"shortcode"\s*:\s*"([^"]+)"', 'shortcode'),
                (r'"caption"\s*:\s*"([^"]+)"', 'caption'),
                (r'"edge_media_preview_like"\s*:\s*{\s*"count"\s*:\s*(\d+)', 'likes'),
                (r'"edge_media_to_comment"\s*:\s*{\s*"count"\s*:\s*(\d+)', 'comments'),
            ]
            
            for pattern, key in patterns:
                matches = re.findall(pattern, script_content)
                if matches:
                    # Process matches based on field type
                    if key in ['username', 'full_name', 'biography', 'business_email', 'business_phone_number', 'business_category_name']:
                        script_data[key] = matches[0]
                    elif key in ['is_private', 'is_verified', 'is_business_account', 'is_professional_account']:
                        script_data[key] = matches[0].lower() == 'true'
                    elif key in ['followers', 'following', 'posts', 'likes', 'comments']:
                        try:
                            script_data[key] = int(matches[0])
                        except ValueError:
                            continue
```

#### Phase 6: Data Processing and Clean Output Generation

**Step 6.1: Content Type Determination**
```python
# From advanced_graphql_extractor.py
def _determine_content_type_from_url(self, url: str, data: Dict[str, Any]) -> str:
    """Determine content type from URL and data"""
    if '/reel/' in url:
        return "video"
    elif '/p/' in url:
        # Check if it's actually a video post
        if (data.get('meta_data', {}).get('content_type') == 'video' or
            data.get('script_data', {}).get('is_video') or
            data.get('script_data', {}).get('video_url')):
            return "video"
        else:
            return "article"
    else:
        return "profile"
```

**Step 6.2: Clean Entry Creation**
```python
# From advanced_graphql_extractor.py
# Add data based on content type
if content_type == "profile":
    user_data = extracted_data.get('user_data', {})
    clean_entry.update({
        "full_name": user_data.get('full_name'),
        "username": user_data.get('username'),
        "followers_count": self._format_count(user_data.get('followers_count')),
        "following_count": self._format_count(user_data.get('following_count')),
        "biography": user_data.get('biography', ''),
        "bio_links": user_data.get('bio_links', []),
        "is_private": user_data.get('is_private', False),
        "is_verified": user_data.get('is_verified', False),
        "is_business_account": user_data.get('is_business_account', False),
        "is_professional_account": user_data.get('is_professional_account', True),
        "business_email": user_data.get('business_email'),
        "business_phone_number": user_data.get('business_phone_number'),
        "business_category_name": user_data.get('business_category_name')
    })
    
elif content_type in ["article", "video"]:
    meta_data = extracted_data.get('meta_data', {})
    script_data = extracted_data.get('script_data', {})
    
    clean_entry.update({
        "likes_count": self._format_count(meta_data.get('likes_count') or script_data.get('likes')),
        "comments_count": self._format_count(meta_data.get('comments_count') or script_data.get('comments')),
        "username": (script_data.get('username') or
                   meta_data.get('username_from_twitter') or
                   meta_data.get('username') or 
                   meta_data.get('username_from_title')),
        "post_date": meta_data.get('post_date'),
        "caption": (meta_data.get('caption') or script_data.get('caption'))
    })
```

**Step 6.3: Business Fields Processing**
```python
# From advanced_graphql_extractor.py
# Always include business fields, even if null
business_fields = ['business_email', 'business_phone_number', 'business_category_name']
for field in business_fields:
    if field not in clean_entry:
        clean_entry[field] = None
    elif clean_entry[field] == '':
        clean_entry[field] = None

# Try to extract business email from biography if not found
if not clean_entry.get('business_email') and clean_entry.get('biography'):
    import re
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', clean_entry['biography'])
    if email_match:
        clean_entry['business_email'] = email_match.group(0)

# Remove None values for non-business fields
clean_entry = {k: v for k, v in clean_entry.items() if v is not None or k in business_fields}
```

**Step 6.4: Data Formatting**
```python
# From advanced_graphql_extractor.py
def _format_count(self, count) -> str:
    """Format count numbers to readable format (e.g., 16000 -> 16K)"""
    if count is None:
        return None
    
    try:
        count = int(count)
        if count >= 1000000:
            return f"{count/1000000:.1f}M".replace('.0', '')
        elif count >= 1000:
            return f"{count/1000:.1f}K".replace('.0', '')
        else:
            return str(count)
    except (ValueError, TypeError):
        return str(count) if count else None
```

#### Phase 7: Output Generation and File Storage

**Step 7.1: JSON File Creation**
```python
# From advanced_graphql_extractor.py
# Save to JSON file
try:
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(all_extracted_data, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n✅ Clean final output saved to: {filename}")
    print(f"   - File size: {len(json.dumps(all_extracted_data, indent=2, ensure_ascii=False, default=str)):,} characters")
    print(f"   - Total entries: {len(all_extracted_data)}")
    
    # Print summary
    print(f"\n📊 EXTRACTION SUMMARY:")
    content_types = {}
    for entry in all_extracted_data:
        content_type = entry.get('content_type', 'unknown')
        content_types[content_type] = content_types.get(content_type, 0) + 1
    
    for content_type, count in content_types.items():
        print(f"   {content_type.title()}: {count} entries")
    
except Exception as e:
    print(f"❌ Error saving clean output to JSON: {e}")
```

#### Phase 8: Anti-Detection Monitoring and Reporting

**Step 8.1: Stealth Report Generation**
```python
# From anti_detection.py
async def get_stealth_report(self) -> Dict[str, Any]:
    """Get comprehensive stealth report"""
    report = {
        'fingerprint_evasion': {
            'enabled': self.enable_fingerprint_evasion,
            'user_agent': self.fingerprint_data.get('user_agent'),
            'platform': self.fingerprint_data.get('platform'),
            'screen_resolution': self.fingerprint_data.get('screen_resolution'),
            'hardware_concurrency': self.fingerprint_data.get('hardware_concurrency'),
            'memory': self.fingerprint_data.get('memory'),
            'timezone': self.fingerprint_data.get('timezone'),
            'locale': self.fingerprint_data.get('locale')
        },
        'behavioral_mimicking': {
            'enabled': self.enable_behavioral_mimicking,
            'total_actions': self.behavioral_state.get('total_actions', 0),
            'current_session_duration': self.behavioral_state.get('current_session_duration', 0),
            'mouse_positions_count': len(self.behavioral_state.get('mouse_positions', [])),
            'scroll_positions_count': len(self.behavioral_state.get('scroll_positions', [])),
            'click_positions_count': len(self.behavioral_state.get('click_positions', []))
        },
        'network_obfuscation': {
            'enabled': self.enable_network_obfuscation,
            'request_count': self.network_state.get('request_count', 0),
            'last_request_time': self.network_state.get('last_request_time', 0),
            'avg_spacing': self._calculate_avg_request_spacing(),
            'connection_errors': self.network_state.get('connection_errors', 0)
        }
    }
    
    return report
```

**Step 8.2: Fingerprint Rotation Check**
```python
# From anti_detection.py
async def should_rotate_fingerprint(self) -> bool:
    """Determine if fingerprint should be rotated"""
    current_time = time.time()
    session_duration = current_time - self.behavioral_state.get('last_action_time', current_time)
    
    # Rotate if session is too long or too many requests
    if (session_duration > 300 or  # 5 minutes
        self.network_state.get('request_count', 0) > 50 or  # 50 requests
        self.network_state.get('connection_errors', 0) > 5):  # 5 errors
        return True
    
    return False
```

#### Phase 9: Cleanup and Resource Management

**Step 9.1: Browser Cleanup**
```python
# From browser_manager.py
async def stop(self) -> None:
    """Clean up browser resources"""
    if self.page:
        await self.page.close()
    if self.context:
        await self.context.close()
    if self.browser:
        await self.browser.close()
    if hasattr(self, 'playwright'):
        await self.playwright.stop()
```

**Step 9.2: Extractor Cleanup**
```python
# From advanced_graphql_extractor.py
async def stop(self) -> None:
    """Clean up browser resources"""
    await self.browser_manager.stop()
```

### 3. Anti-Detection Features Integration

#### 3.1 Fingerprint Evasion
- **User Agent Rotation**: Random user agents for each session
- **Platform Spoofing**: Mimics different operating systems
- **Screen Resolution**: Varies screen dimensions
- **Hardware Concurrency**: Randomizes CPU core count
- **Memory**: Varies available memory
- **Timezone**: Rotates timezone settings
- **Locale**: Changes language settings

#### 3.2 Behavioral Mimicking
- **Human-like Scrolling**: Natural scroll patterns with pauses
- **Mouse Movement**: Realistic mouse trajectories
- **Click Behavior**: Human-like click timing and positioning
- **Session Duration**: Varies session lengths
- **Action Spacing**: Natural delays between actions

#### 3.3 Network Obfuscation
- **Request Spacing**: Random delays between requests
- **Jitter Factor**: Adds randomness to timing
- **Backoff Strategy**: Exponential backoff on errors
- **Connection Management**: Proper connection handling
- **Header Rotation**: Varies request headers

### 4. Data Flow Summary

1. **Input**: URLs are provided to the system
2. **Initialization**: Browser and anti-detection systems are set up
3. **Navigation**: Each URL is navigated to with anti-detection measures
4. **Monitoring**: Network requests and responses are captured
5. **Extraction**: Data is extracted from multiple sources (API, GraphQL, HTML, Scripts)
6. **Processing**: Data is cleaned, formatted, and structured
7. **Output**: Clean JSON files are generated
8. **Cleanup**: Resources are properly released

### 5. Error Handling and Resilience

- **Network Errors**: Graceful handling of connection issues
- **Data Extraction Errors**: Fallback mechanisms for missing data
- **Anti-Detection Failures**: Automatic fingerprint rotation
- **File I/O Errors**: Simplified output generation on failure
- **Browser Crashes**: Automatic restart and recovery

This comprehensive flow ensures robust, stealthy, and efficient Instagram data extraction while maintaining high data quality and system reliability.

## System Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Input    │───▶│ AdvancedGraphQL  │───▶│ BrowserManager  │
│  (URL/Username) │    │   Extractor      │    │   (Playwright)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │ Network Monitor  │    │ Instagram Page  │
                       │ (Request/Response)│    │ (DOM + JS)      │
                       └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │ Data Parser      │    │ Popup Handler   │
                       │ (JSON/HTML/Text) │    │ (Login/Signup)  │
                       └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ Data Storage     │
                       │ (JSON Files)     │
                       └──────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ Clean Output     │
                       │ (Structured JSON)│
                       └──────────────────┘
```

## Data Processing and Output Generation

### 1. Multi-Source Data Extraction

The system extracts data from multiple sources to ensure comprehensive coverage:

**API Responses**: Primary source for structured user data
**GraphQL Responses**: Fallback for API data and additional metadata
**HTML Meta Tags**: Open Graph and Twitter Card data
**Script Tags**: Embedded JavaScript data with user information
**Page Analysis**: Content analysis for Instagram-specific elements

### 2. Data Processing Pipeline

**Step 1: Raw Data Collection**
- Network requests and responses are captured
- HTML content is parsed for meta tags and scripts
- Page content is analyzed for Instagram-specific elements

**Step 2: Data Extraction**
- API responses are parsed for user profile data
- GraphQL responses are processed for additional metadata
- Script tags are searched for embedded data patterns
- Meta tags are extracted for social media data

**Step 3: Data Cleaning**
- Null values are handled appropriately
- Business fields are always included (even if null)
- Data types are converted (strings to integers, booleans)
- Counts are formatted for readability (16000 → "16K")

**Step 4: Content Type Determination**
- URL patterns are analyzed (/reel/, /p/, profile)
- Content indicators are checked (video, article, profile)
- Data validation ensures accurate classification

### 3. Output Generation

**Clean JSON Structure**:
- Consistent field naming and data types
- Business fields always present (even if null)
- Formatted counts for better readability
- Content type classification for each entry

**Error Handling**:
- Graceful handling of missing data
- Fallback mechanisms for failed extractions
- Progress tracking for batch processing
- Detailed error logging and reporting

## Anti-Detection System Integration

### 1. Fingerprint Evasion

**User Agent Rotation**: Random user agents for each session
**Platform Spoofing**: Mimics different operating systems
**Screen Resolution**: Varies screen dimensions
**Hardware Concurrency**: Randomizes CPU core count
**Memory**: Varies available memory
**Timezone**: Rotates timezone settings
**Locale**: Changes language settings

### 2. Behavioral Mimicking

**Human-like Scrolling**: Natural scroll patterns with pauses
**Mouse Movement**: Realistic mouse trajectories
**Click Behavior**: Human-like click timing and positioning
**Session Duration**: Varies session lengths
**Action Spacing**: Natural delays between actions

### 3. Network Obfuscation

**Request Spacing**: Random delays between requests
**Jitter Factor**: Adds randomness to timing
**Backoff Strategy**: Exponential backoff on errors
**Connection Management**: Proper connection handling
**Header Rotation**: Varies request headers

## System Integration Points

### 1. Component Communication

**AdvancedGraphQLExtractor ↔ BrowserManager**:
- Browser initialization and management
- Page navigation and popup handling
- Human-like behavior execution

**BrowserManager ↔ AntiDetectionManager**:
- Stealth context creation
- Fingerprint evasion implementation
- Behavioral mimicking coordination

**AdvancedGraphQLExtractor ↔ Network Monitoring**:
- Request/response interception
- Data capture and storage
- Error handling and recovery

### 2. Data Flow Integration

**Input Processing**: URLs are validated and categorized
**Browser Setup**: Anti-detection features are configured
**Navigation**: Each URL is processed with stealth measures
**Data Capture**: Multiple sources are monitored simultaneously
**Processing**: Data is extracted, cleaned, and formatted
**Output**: Clean JSON files are generated with comprehensive metadata

## Error Handling and Resilience

### 1. Network Error Handling

**Connection Failures**: Automatic retry with exponential backoff
**Rate Limiting**: Intelligent delays and request spacing
**Timeout Handling**: Configurable timeouts with fallback strategies
**DNS Issues**: Robust error recovery and logging

### 2. Data Extraction Errors

**Missing API Responses**: Fallback to GraphQL and script data
**Parsing Failures**: Graceful handling with error logging
**Content Changes**: Adaptive pattern matching and validation
**Format Variations**: Flexible data type handling

### 3. Anti-Detection Failures

**Fingerprint Detection**: Automatic rotation and regeneration
**Behavioral Analysis**: Dynamic pattern adjustment
**Session Blocking**: Clean session restart and recovery
**IP Blocking**: Proxy rotation and session management

## Performance Optimization

### 1. Memory Management

**Data Clearing**: Previous extraction data is cleared before new processing
**Resource Cleanup**: Proper browser and context cleanup
**Memory Monitoring**: Track memory usage and optimize accordingly
**Garbage Collection**: Efficient memory deallocation

### 2. Processing Efficiency

**Batch Processing**: Multiple URLs processed sequentially with error handling
**Parallel Processing**: Network monitoring runs concurrently with page processing
**Smart Extraction**: Only relevant data is extracted and processed
**Caching**: Temporary data storage for repeated access

### 3. Network Optimization

**Request Batching**: Efficient request grouping and spacing
**Connection Reuse**: Maintain persistent connections where possible
**Compression Handling**: Support for zstd and other compression formats
**Bandwidth Management**: Optimize data transfer and processing

## Security Considerations

### 1. Data Privacy

**Local Processing**: All data processing occurs locally
**No Data Transmission**: Extracted data is not sent to external services
**Secure Storage**: Data is stored securely in local JSON files
**Access Control**: Proper file permissions and access management

### 2. Rate Limiting Compliance

**Respectful Scraping**: Built-in delays and request spacing
**Instagram ToS**: Compliance with Instagram's Terms of Service
**Ethical Usage**: Responsible data extraction practices
**Legal Considerations**: Awareness of applicable laws and regulations

### 3. Anti-Detection Security

**Fingerprint Protection**: Comprehensive browser fingerprint evasion
**Behavioral Security**: Human-like interaction patterns
**Network Security**: Secure connection handling and header management
**Session Security**: Proper session management and cleanup

## System Monitoring and Reporting

### 1. Stealth Reporting

**Fingerprint Metrics**: Track evasion effectiveness
**Behavioral Statistics**: Monitor human-like behavior patterns
**Network Analysis**: Analyze request patterns and timing
**Session Monitoring**: Track session duration and activity

### 2. Performance Monitoring

**Extraction Success Rates**: Track successful data extraction
**Processing Times**: Monitor extraction and processing performance
**Memory Usage**: Track resource consumption
**Error Rates**: Monitor and analyze error patterns

### 3. Data Quality Assessment

**Completeness Metrics**: Assess data extraction completeness
**Accuracy Validation**: Verify extracted data accuracy
**Format Consistency**: Ensure consistent output formatting
**Field Coverage**: Track field extraction success rates

## Recent System Enhancements

### 1. Username Extraction Improvements

**Enhanced Priority System**:
```python
# New username extraction priority order
"username": (script_data.get('username') or
           meta_data.get('username_from_twitter') or
           meta_data.get('username') or 
           meta_data.get('username_from_title'))
```

**Improved Regex Patterns**:
```python
# Enhanced regex for international formats
username_match = re.search(r'- ([a-zA-Z0-9._]+)\s+(?:el|on)\s+', description)

# Twitter title extraction
username_match = re.search(r'\(@([a-zA-Z0-9._]+)\)\s*•\s*Instagram', twitter_title)

# OG title extraction (more specific)
username_match = re.search(r'\(@([a-zA-Z0-9._]+)\)\s*•\s*Instagram', og_title)
```

**Multi-Source Fallback**:
- **Primary**: Script data username (most reliable)
- **Secondary**: Twitter title username (consistent format)
- **Tertiary**: OG description username (international support)
- **Quaternary**: OG title username (least reliable)

### 2. Data Processing Enhancements

**URL Construction Fixes**:
```python
# Improved shortcode extraction
shortcode = post_data.get('meta_data', {}).get('shortcode')
if not shortcode and post_data.get('url'):
    import re
    url_match = re.search(r'instagram\.com/p/([^/?]+)', post_data.get('url'))
    if url_match:
        shortcode = url_match.group(1)
```

**Content Type Detection**:
```python
def _determine_content_type_from_url(self, url: str, data: Dict[str, Any]) -> str:
    if '/reel/' in url:
        return "video"
    elif '/p/' in url:
        # Check if it's actually a video post
        if (data.get('meta_data', {}).get('content_type') == 'video' or
            data.get('script_data', {}).get('is_video') or
            data.get('script_data', {}).get('video_url')):
            return "video"
        else:
            return "article"
    else:
        return "profile"
```

**Business Field Handling**:
```python
# Always include business fields, even if null
business_fields = ['business_email', 'business_phone_number', 'business_category_name']
for field in business_fields:
    if field not in clean_entry:
        clean_entry[field] = None
    elif clean_entry[field] == '':
        clean_entry[field] = None
```

### 3. Anti-Detection Improvements

**Enhanced Fingerprint Rotation**:
```python
async def should_rotate_fingerprint(self) -> bool:
    current_time = time.time()
    session_duration = current_time - self.behavioral_state.get('last_action_time', current_time)
    
    # Rotate if session is too long or too many requests
    if (session_duration > 300 or  # 5 minutes
        self.network_state.get('request_count', 0) > 50 or  # 50 requests
        self.network_state.get('connection_errors', 0) > 5):  # 5 errors
        return True
    
    return False
```

**Improved Behavioral Patterns**:
- More realistic human-like interactions
- Enhanced scroll patterns with acceleration/deceleration
- Better mouse movement trajectories
- Improved click timing variations

**Advanced Network Obfuscation**:
- Variable request spacing with jitter
- Exponential backoff for high request counts
- Geographic header consistency
- Connection pooling and reuse

### 4. Data Validation and Error Handling

**Enhanced Error Recovery**:
```python
# Graceful handling of missing data
if extracted_data.get('error'):
    print(f"❌ Failed to extract data from {url}: {extracted_data['error']}")
    continue

# Fallback mechanisms for failed extractions
if not user_data.get('username'):
    # Fallback to GraphQL responses
    for url, response in getattr(self, 'graphql_responses', {}).items():
        if 'data' in response and 'user' in response.get('data', {}):
            user_info = response.get('data', {}).get('user', {})
            if user_info and user_info.get('username'):
                user_data.update({...})
                break
```

**Data Quality Assessment**:
- Success indicators for each data type
- Missing data analysis and reporting
- Field coverage tracking
- Accuracy validation metrics

## Conclusion

The Advanced GraphQL Extractor provides a comprehensive, robust, and stealthy solution for Instagram data extraction. The system's layered architecture ensures efficient data processing while maintaining high security and anti-detection standards. The integration of multiple data sources, advanced anti-detection features, and comprehensive error handling makes it a reliable tool for extracting Instagram data in a clean, structured format suitable for further processing and analysis.

The recent enhancements have significantly improved:
- **Username extraction accuracy** through multi-source prioritization
- **Data processing reliability** with enhanced fallback mechanisms
- **Anti-detection effectiveness** with improved behavioral patterns
- **System resilience** through better error handling and recovery

These improvements ensure the system remains effective and reliable for Instagram data extraction while maintaining high standards of stealth and data quality. 