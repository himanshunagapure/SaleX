# Filter Web Lead Integration

This document describes the integration of the `filter_web_lead.py` functionality into the main lead generation pipeline.

## Overview

The `filter_web_lead.py` module has been integrated into both `main.py` and `app.py` to automatically filter and process leads after all scrapers have completed their work. This ensures that only high-quality leads with valid contact information are stored in the final `leadgen_leads` collection.

## Integration Points

### 1. Main Pipeline (`main.py`)

The filter is integrated as **Step 6** in the orchestration pipeline:

```python
# Step 6: Filter and process leads using MongoDBLeadProcessor
logger.info("🧹 Step 6: Filtering and processing leads...")
try:
    lead_processor = MongoDBLeadProcessor()
    
    # Create indexes for the target collection
    lead_processor.create_indexes()
    
    # Process all leads from web_leads collection to leadgen_leads collection
    filtering_results = lead_processor.process_leads(batch_size=50)
    
    # Get processing statistics
    processing_stats = lead_processor.get_processing_stats()
    
    # Add filtering results to the main results
    results['lead_filtering'] = {
        'filtering_stats': filtering_results,
        'processing_stats': processing_stats
    }
    
    lead_processor.close_connection()
    
except Exception as e:
    logger.error(f"❌ Error in lead filtering: {e}")
    results['lead_filtering'] = {'error': str(e)}
```

### 2. API Pipeline (`app.py`)

The filter is integrated as **Step 4** in the API pipeline:

```python
# Step 4: Filter and process leads using MongoDBLeadProcessor
logger.info("🧹 Step 4: Filtering and processing leads...")
lead_filtering_results = {}
try:
    lead_processor = MongoDBLeadProcessor()
    
    # Create indexes for the target collection
    lead_processor.create_indexes()
    
    # Process all leads from web_leads collection to leadgen_leads collection
    filtering_results = lead_processor.process_leads(batch_size=50)
    
    # Get processing statistics
    processing_stats = lead_processor.get_processing_stats()
    
    lead_filtering_results = {
        'filtering_stats': filtering_results,
        'processing_stats': processing_stats
    }
    
    lead_processor.close_connection()
    
except Exception as e:
    logger.error(f"❌ Error in lead filtering: {e}")
    lead_filtering_results = {'error': str(e)}

# Add filtering results to scraper results
scraper_results['lead_filtering'] = lead_filtering_results
```

## What the Filter Does

The `MongoDBLeadProcessor` performs the following operations:

1. **Filters leads** from the `web_leads` collection that have valid email addresses or phone numbers
2. **Extracts structured data** from the filtered leads into a standardized format
3. **Handles duplicates** by keeping the lead with more information
4. **Stores processed leads** in the `leadgen_leads` collection
5. **Creates indexes** for efficient querying
6. **Provides statistics** about the processing results

## Data Flow

```
web_leads collection → MongoDBLeadProcessor → leadgen_leads collection
```

### Input Data Structure (`web_leads`)
- Raw scraped data from various sources
- May contain emails, phones, company info, etc.
- Mixed quality and completeness

### Output Data Structure (`leadgen_leads`)
- Standardized lead format with fields like:
  - Company Name
  - Industry
  - Contact Name
  - Email Address
  - Phone Number
  - Lead Category
  - Lead Sub Category
  - etc.

## New API Endpoints

### 1. Standalone Lead Filtering

**Endpoint:** `POST /api/lead-filtering/run`

**Purpose:** Run only the lead filtering process without running scrapers

**Request Body:**
```json
{
    "query_filter": {},  // Optional MongoDB query filter
    "batch_size": 50     // Optional batch size (default: 50)
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "filtering_results": {
            "total": 100,
            "filtered": 75,
            "extracted": 150,
            "inserted": 150,
            "email_based": 120,
            "phone_based": 30
        },
        "processing_stats": {
            "total_web_leads": 100,
            "total_extracted_leads": 150,
            "unique_companies": 45,
            "unique_industries": 12,
            "email_based_leads": 120,
            "phone_based_leads": 30
        },
        "timestamp": "2025-01-27T10:30:00"
    },
    "message": "Lead filtering completed successfully"
}
```

## Pipeline Results

The filtering results are included in the final pipeline output:

### Main Pipeline Output
```python
results['lead_filtering'] = {
    'filtering_stats': {
        'total': 100,        # Total web_leads processed
        'filtered': 75,      # Leads with valid contact info
        'extracted': 150,    # Individual leads extracted
        'inserted': 150,     # Leads inserted to leadgen_leads
        'email_based': 120,  # Email-based leads
        'phone_based': 30    # Phone-based leads
    },
    'processing_stats': {
        'total_web_leads': 100,
        'total_extracted_leads': 150,
        'unique_companies': 45,
        'unique_industries': 12,
        'email_based_leads': 120,
        'phone_based_leads': 30
    }
}
```

### API Pipeline Response
The API response includes filtering results in the `scraper_results_summary`:

```json
{
    "scraper_results_summary": {
        "lead_filtering": {
            "status": "success",
            "leads_processed": 100,
            "leads_filtered": 75,
            "leads_extracted": 150,
            "leads_inserted": 150,
            "email_based_leads": 120,
            "phone_based_leads": 30
        }
    },
    "pipeline_metadata": {
        "lead_filtering_successful": true
    }
}
```

## Testing

Run the integration test:

```bash
python test_filter_integration.py
```

This will test:
1. Direct `filter_web_lead` functionality
2. API integration
3. Database connectivity
4. Processing statistics

## Configuration

The filter uses the following environment variables:

- `MONGODB_URI`: MongoDB connection string (default: `mongodb://localhost:27017/`)
- `MONGODB_DATABASE_NAME`: Database name (default: `lead_generation_db`)
- `MONGODB_COLLECTION`: Source collection name (default: `web_leads`)

The target collection is hardcoded as `leadgen_leads`.

## Error Handling

The integration includes comprehensive error handling:

1. **Connection errors**: Logged and reported in results
2. **Processing errors**: Individual lead errors are logged, processing continues
3. **Batch errors**: Failed batches are logged, remaining batches continue
4. **API errors**: Proper HTTP status codes and error messages

## Performance Considerations

- **Batch processing**: Default batch size of 50 for memory efficiency
- **Indexes**: Automatic creation of indexes for common queries
- **Connection management**: Proper connection cleanup
- **Duplicate handling**: Efficient duplicate detection and resolution

## Monitoring

The integration provides detailed logging and statistics:

- Processing progress logs
- Batch completion notifications
- Error reporting
- Performance statistics
- Data quality metrics

This integration ensures that the lead generation pipeline produces high-quality, deduplicated leads ready for sales and marketing use.
