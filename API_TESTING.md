# 🧪 API Testing Guide

Complete guide for testing the Customer Support AI API using curl, Postman, or other HTTP clients.

## Server Setup

Before testing, ensure:
1. Backend is running: `python backend/app.py`
2. Server listens on: `http://localhost:5000`

## Health Check

### Test if server is running

```bash
curl -X GET http://localhost:5000/api/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "service": "Customer Support Response Generator",
  "version": "1.0.0"
}
```

## Modes Endpoint

### Get available support modes

```bash
curl -X GET http://localhost:5000/api/modes
```

**Expected Response**:
```json
{
  "success": true,
  "modes": {
    "strict": {
      "name": "STRICT_POLICY",
      "value": "strict",
      "description": "Strict Policy Mode...",
      "temperature": 0.2,
      "max_tokens": 150
    },
    "friendly": {
      "name": "FRIENDLY",
      "value": "friendly",
      "description": "Friendly Mode...",
      "temperature": 0.7,
      "max_tokens": 200
    },
    "fallback": {
      "name": "FALLBACK",
      "value": "fallback",
      "description": "Fallback Mode...",
      "temperature": 0.5,
      "max_tokens": 100
    }
  }
}
```

## Generate Response

### Main endpoint for generating responses

```bash
curl -X POST http://localhost:5000/api/generate-response \
  -H "Content-Type: application/json" \
  -d '{
    "query": "My product arrived late and damaged. Can I get a refund?",
    "mode": "friendly"
  }'
```

**Parameters**:
- `query` (string, required): Customer complaint or question
- `mode` (string, optional): "strict", "friendly", or "fallback" (default: "friendly")

**Response**:
```json
{
  "success": true,
  "response": "Thank you for reaching out to us! We completely understand your situation...",
  "mode_used": "friendly",
  "retrieved_documents": [
    {
      "id": 4,
      "title": "Delivery Delay Compensation",
      "score": 8.45
    },
    {
      "id": 5,
      "title": "Damaged Product Policy",
      "score": 7.82
    }
  ],
  "parameters": {
    "temperature": 0.7,
    "max_tokens": 200
  },
  "model": "Sarvam-2B",
  "is_mock": false
}
```

### Test Queries

Try these example queries:

#### Query 1: Delivery Delay
```bash
curl -X POST http://localhost:5000/api/generate-response \
  -H "Content-Type: application/json" \
  -d '{
    "query": "My order is 10 days late!",
    "mode": "friendly"
  }'
```
**Expected**: Retrieves "Delivery Delay Compensation" policy

#### Query 2: Damaged Product
```bash
curl -X POST http://localhost:5000/api/generate-response \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Product arrived damaged. What should I do?",
    "mode": "strict"
  }'
```
**Expected**: Retrieves "Damaged Product Policy"

#### Query 3: Return Question
```bash
curl -X POST http://localhost:5000/api/generate-response \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Can I return this item after 14 days?",
    "mode": "friendly"
  }'
```
**Expected**: Retrieves "Return Policy"

#### Query 4: Refund Request
```bash
curl -X POST http://localhost:5000/api/generate-response \
  -H "Content-Type: application/json" \
  -d '{
    "query": "I want my money back",
    "mode": "friendly"
  }'
```
**Expected**: Retrieves "Refund Policy"

#### Query 5: Complex Issue (Fallback)
```bash
curl -X POST http://localhost:5000/api/generate-response \
  -H "Content-Type: application/json" \
  -d '{
    "query": "The product quality is terrible and I am very unhappy",
    "mode": "friendly"
  }'
```
**Expected**: Low score → Falls back to escalation

## Retrieve Documents

### Get relevant documents without generating response

```bash
curl -X POST http://localhost:5000/api/retrieve-documents \
  -H "Content-Type: application/json" \
  -d '{
    "query": "refund policy",
    "top_k": 3
  }'
```

**Parameters**:
- `query` (string, required): Search query
- `top_k` (integer, optional): Number of documents to return (default: 3, max: 5)

**Response**:
```json
{
  "success": true,
  "query": "refund policy",
  "documents": [
    {
      "id": 1,
      "title": "Refund Policy",
      "content": "Customers can request refunds...",
      "score": 12.45
    },
    {
      "id": 5,
      "title": "Damaged Product Policy",
      "content": "If a product arrives damaged...",
      "score": 6.78
    }
  ]
}
```

### Test Semantic Retrieval

```bash
# Test different queries
curl -X POST http://localhost:5000/api/retrieve-documents \
  -H "Content-Type: application/json" \
  -d '{"query": "delay", "top_k": 3}'

curl -X POST http://localhost:5000/api/retrieve-documents \
  -H "Content-Type: application/json" \
  -d '{"query": "exchange", "top_k": 5}'

curl -X POST http://localhost:5000/api/retrieve-documents \
  -H "Content-Type: application/json" \
  -d '{"query": "cancellation", "top_k": 2}'
```

## Test Prompt

### Preview prompt without calling LLM

```bash
curl -X POST http://localhost:5000/api/test-prompt \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Can I get a refund?",
    "mode": "strict"
  }'
```

**Response**:
```json
{
  "success": true,
  "mode": "strict",
  "prompt": "You are a professional customer support assistant...\n\nCONTEXT:\n...",
  "configuration": {
    "temperature": 0.2,
    "max_tokens": 150,
    "description": "Strict Policy Mode..."
  },
  "retrieved_documents": [
    {
      "title": "Refund Policy",
      "score": 10.23
    }
  ]
}
```

**Use Case**: Debug prompts before sending to LLM

### Compare Prompts Across Modes

```bash
# Strict Mode
curl -X POST http://localhost:5000/api/test-prompt \
  -H "Content-Type: application/json" \
  -d '{"query": "refund", "mode": "strict"}' > strict_prompt.json

# Friendly Mode
curl -X POST http://localhost:5000/api/test-prompt \
  -H "Content-Type: application/json" \
  -d '{"query": "refund", "mode": "friendly"}' > friendly_prompt.json

# Compare
diff strict_prompt.json friendly_prompt.json
```

## Statistics

### View usage statistics

```bash
curl -X GET http://localhost:5000/api/statistics
```

**Response**:
```json
{
  "success": true,
  "statistics": {
    "total_interactions": 42,
    "by_mode": {
      "strict": 10,
      "friendly": 28,
      "fallback": 4
    },
    "avg_response_length": 156.8
  }
}
```

## Error Handling

### Missing Required Field

```bash
curl -X POST http://localhost:5000/api/generate-response \
  -H "Content-Type: application/json" \
  -d '{"mode": "friendly"}'
```

**Response** (400):
```json
{
  "success": false,
  "error": "Missing required field: query"
}
```

### Invalid Mode

```bash
curl -X POST http://localhost:5000/api/generate-response \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "mode": "invalid"}'
```

**Response** (400):
```json
{
  "success": false,
  "error": "Invalid mode. Use: strict, friendly, or fallback"
}
```

### Empty Query

```bash
curl -X POST http://localhost:5000/api/generate-response \
  -H "Content-Type: application/json" \
  -d '{"query": "", "mode": "friendly"}'
```

**Response** (400):
```json
{
  "success": false,
  "error": "Query cannot be empty"
}
```

### Server Error

```json
{
  "success": false,
  "error": "Error generating response: [error details]"
}
```

## Testing Tools

### Using Postman

1. **Create Collection**: "Customer Support API"
2. **Add Requests**:
   - GET `/api/health`
   - GET `/api/modes`
   - POST `/api/generate-response`
   - POST `/api/retrieve-documents`
   - POST `/api/test-prompt`
   - GET `/api/statistics`

3. **Set Variables**:
   ```json
   {
     "base_url": "http://localhost:5000"
   }
   ```

4. **Use in Requests**:
   ```
   {{base_url}}/api/generate-response
   ```

### Using Insomnia

Similar to Postman. Import the following:

```
POST http://localhost:5000/api/generate-response
Content-Type: application/json

{
  "query": "My order is late",
  "mode": "friendly"
}
```

### Using VS Code REST Client Extension

Create `test.http`:

```http
### Health Check
GET http://localhost:5000/api/health

### Get Modes
GET http://localhost:5000/api/modes

### Generate Response
POST http://localhost:5000/api/generate-response
Content-Type: application/json

{
  "query": "My product arrived damaged",
  "mode": "friendly"
}

### Retrieve Documents
POST http://localhost:5000/api/retrieve-documents
Content-Type: application/json

{
  "query": "refund",
  "top_k": 3
}

### Get Statistics
GET http://localhost:5000/api/statistics
```

Then click "Send Request" in VS Code.

## Load Testing

### Test with Apache Bench

```bash
# Single request
ab -n 1 http://localhost:5000/api/health

# 100 requests
ab -n 100 http://localhost:5000/api/health

# 100 requests, 10 concurrent
ab -n 100 -c 10 http://localhost:5000/api/health

# POST request
ab -n 100 -c 10 -p request.json -T application/json \
  http://localhost:5000/api/generate-response
```

### Test with Apache JMeter

1. Create Thread Group (100 users)
2. Add HTTP Sampler with:
   - Method: POST
   - Path: /api/generate-response
   - Body Data: `{"query": "test", "mode": "friendly"}`
3. Add View Results Tree listener
4. Run test

### Performance Baseline

Expected performance:
- Response time: < 100ms
- Throughput: > 100 requests/second
- CPU usage: < 20%
- Memory: < 100MB

## Automated Testing Script

Create `test_api.sh`:

```bash
#!/bin/bash

BASE_URL="http://localhost:5000"

# Test 1: Health
echo "Testing Health..."
curl -s $BASE_URL/api/health | jq .

# Test 2: Modes
echo -e "\nTesting Modes..."
curl -s $BASE_URL/api/modes | jq '.modes | keys'

# Test 3: Generate Response
echo -e "\nTesting Generate Response..."
curl -s -X POST $BASE_URL/api/generate-response \
  -H "Content-Type: application/json" \
  -d '{"query": "My order is late", "mode": "friendly"}' | jq '.response'

# Test 4: Statistics
echo -e "\nTesting Statistics..."
curl -s $BASE_URL/api/statistics | jq '.statistics'

echo -e "\n✅ All tests completed"
```

Run with:
```bash
chmod +x test_api.sh
./test_api.sh
```

## Response Format Standards

All successful responses follow:
```json
{
  "success": true,
  "data": {}
}
```

All error responses follow:
```json
{
  "success": false,
  "error": "Error description"
}
```

## Rate Limiting

Current implementation has no rate limiting.

For production, consider adding:
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

## CORS Configuration

Currently allows all origins:
```python
CORS(app)  # Allow all
```

For production, restrict to specific origins:
```python
CORS(app, origins=["https://yourdomain.com"])
```

## Security Headers

Add to Flask app:
```python
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

---

**Happy Testing! 🚀**
