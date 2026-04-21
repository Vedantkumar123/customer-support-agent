# 🔧 Troubleshooting Guide

Common issues and their solutions.

## Backend Issues

### Issue: `ModuleNotFoundError: No module named 'flask'`

**Solution**:
```bash
# Reinstall requirements
pip install -r backend/requirements.txt

# Or install manually
pip install Flask Flask-CORS requests rank-bm25
```

**Verify**:
```bash
python -c "import flask; print(flask.__version__)"
```

### Issue: `Address already in use: ('0.0.0.0', 5000)`

**Solution**:
```bash
# Find process using port 5000
netstat -ano | findstr :5000  # Windows
lsof -i :5000                 # Mac/Linux

# Kill process
taskkill /PID <PID> /F        # Windows
kill -9 <PID>                 # Mac/Linux

# Or use different port in app.py
app.run(port=5001)
```

### Issue: `FileNotFoundError: 'policies.json' not found`

**Solution**:
```bash
# Check file exists
ls -la backend/policies.json

# If missing, it should be in repo, check from backend directory
cd backend
python app.py
```

### Issue: Backend returns `500 Internal Server Error`

**Solution**:
```bash
# Check backend terminal for error message
# Common causes:

# 1. Policies.json corrupted
cat backend/policies.json | python -m json.tool  # Validate JSON

# 2. Import errors
python -c "from bm25_retriever import BM25Retriever"

# 3. Missing dependencies
pip list | grep rank-bm25

# 4. File permissions
chmod 644 backend/policies.json  # Make readable
```

### Issue: Slow response times

**Solution**:
```bash
# 1. Check system resources
# Windows
tasklist | findstr python

# Mac/Linux
ps aux | grep python

# 2. Profile code
python -m cProfile -s cumulative app.py

# 3. Check BM25 document loading time
# Add timing to bm25_retriever.py:
import time
start = time.time()
self.bm25 = BM25Okapi(self.corpus)
print(f"BM25 init: {time.time() - start:.3f}s")
```

## Frontend Issues

### Issue: `npm ERR! code EACCES: permission denied`

**Solution**:
```bash
# Fix npm permissions
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
export PATH=~/.npm-global/bin:$PATH

# Or use sudo (not recommended)
sudo npm install
```

### Issue: `Cannot find module 'react'`

**Solution**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install

# Or use yarn
yarn install
```

### Issue: Frontend won't connect to backend

**Checklist**:
```bash
# 1. Check backend is running
curl http://localhost:5000/api/health

# 2. Check CORS enabled
# In app.py: CORS(app)

# 3. Check correct URL in App.js
// Should be: http://localhost:5000

# 4. Check browser console (F12)
# Look for CORS errors or connection refused

# 5. Check firewall
# Port 5000 should be accessible from localhost
```

### Issue: `net::ERR_CONNECTION_REFUSED` in browser

**Solution**:
```bash
# 1. Ensure backend running
python backend/app.py

# 2. Check port
netstat -an | grep 5000  # Should show LISTENING

# 3. Check firewall allows localhost:5000
# Windows Defender → Firewall → Allow app through firewall

# 4. Try alternative port
# Edit app.py: app.run(port=5001)
# Edit App.js: http://localhost:5001
```

### Issue: UI looks broken (CSS not loading)

**Solution**:
```bash
# 1. Hard refresh (clear cache)
Ctrl+Shift+R  # Windows/Linux
Cmd+Shift+R   # Mac

# 2. Check CSS files exist
ls -la frontend/src/components/*.css

# 3. Check imports in JS files
// Should import CSS:
import './ComponentName.css'

# 4. Check webpack is bundling
npm run build  # Build and check dist/

# 5. Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
npm start
```

### Issue: React errors in console

**Solution**:
```bash
# Common React errors and fixes:

# 1. "Cannot read property 'map' of undefined"
# In Component.js:
const modes = modes || {};  // Provide default

# 2. "Missing dependency in useEffect"
// Add to dependency array:
useEffect(() => {
  // ...
}, [dependency]);  // ← Add here

# 3. "Unexpected token"
# Check for syntax errors:
npm run build  # Will show detailed errors
```

## API Issues

### Issue: Empty response from `/api/generate-response`

**Solution**:
```bash
# 1. Check request format
curl -X POST http://localhost:5000/api/generate-response \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "mode": "friendly"}'

# 2. Ensure query is not empty
# "query": "" ❌
# "query": "my question" ✅

# 3. Check mode is valid
# "mode": "strict" or "friendly" or "fallback"

# 4. Check error response
curl -s ... | jq '.error'  # View error message
```

### Issue: Wrong documents retrieved

**Solution**:
```bash
# 1. Test BM25 retrieval directly
curl -X POST http://localhost:5000/api/retrieve-documents \
  -H "Content-Type: application/json" \
  -d '{"query": "refund", "top_k": 5}'

# 2. Check BM25 scores
# Score < 2.0 → Document not relevant
# Score > 10.0 → Document very relevant

# 3. Problem: Policies too vague
# Solution: Make policies more detailed

# 4. Problem: Query too ambiguous
# Example: "help" → matches everything
# Better: "Can I cancel my order?"

# 5. Add more policies
# Edit backend/policies.json and add specific policies
```

### Issue: Sarvam API failing

**Solution**:
```bash
# 1. Check API key is set
echo $SARVAM_API_KEY

# 2. Verify key is valid
# Try making direct curl call to Sarvam API
curl -X POST https://api.sarvam.ai/generate \
  -H "Authorization: Bearer $SARVAM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello", "model_name": "Sarvam-2B-Instruct-v0.1"}'

# 3. Check network/firewall
# API might be blocked by firewall
# Check: ping api.sarvam.ai

# 4. Use mock mode for testing
# In sarvam_client.py:
use_mock=True  # Set to True while debugging

# 5. Check error in response
curl -s ... | jq '.error'
```

## Database/Logging Issues

### Issue: Logs not being created

**Solution**:
```bash
# 1. Check logs directory exists
ls -la backend/logs/

# 2. Create if missing
mkdir -p backend/logs/

# 3. Check file permissions
chmod 755 backend/logs/
chmod 644 backend/logs/*.log  # If files exist

# 4. Check Python logging config
# In logger.py, ensure path is correct:
os.makedirs(log_dir, exist_ok=True)
```

### Issue: Cannot read logs

**Solution**:
```bash
# 1. View text logs
cat backend/logs/support_interactions.log

# 2. View JSON logs (pretty print)
cat backend/logs/interactions.jsonl | python -m json.tool

# 3. Filter logs
grep "friendly" backend/logs/support_interactions.log

# 4. Real-time log watch
tail -f backend/logs/support_interactions.log
```

## Performance Issues

### Issue: Slow response time

**Diagnosis**:
```bash
# 1. Measure latency
time curl http://localhost:5000/api/health

# 2. Profile
python -m cProfile backend/app.py

# 3. Check system resources
# Windows
Get-Process python | Select-Object ProcessName, CPU, Memory

# Mac/Linux
ps aux | grep python
```

**Solutions**:
```bash
# 1. Cache BM25 results
# Add to bm25_retriever.py:
from functools import lru_cache

@lru_cache(maxsize=128)
def retrieve(self, query, top_k=3):
    # ...

# 2. Pre-load policies
# Move initialization outside request handler
retriever = BM25Retriever()  # Before @app.route

# 3. Use async/await
# Upgrade to async Python framework (FastAPI)

# 4. Add caching layer (Redis)
# For production deployments
```

### Issue: High memory usage

**Solution**:
```bash
# 1. Check memory
# Windows Task Manager → Details
# Mac: Activity Monitor
# Linux: free -h

# 2. Profile memory
python -m memory_profiler backend/app.py

# 3. Reduce policy file size
# Remove unnecessary policies from policies.json

# 4. Limit concurrent requests
# Add to Flask:
max_content_length = 16 * 1024 * 1024  # 16MB limit
```

## Configuration Issues

### Issue: Settings not taking effect

**Solution**:
```bash
# 1. Restart server
# Stop: Ctrl+C
# Start: python app.py

# 2. Check environment variables
echo $SARVAM_API_KEY  # Linux/Mac
echo %SARVAM_API_KEY%  # Windows

# 3. Clear cache
# Python cache
rm -rf backend/__pycache__

# npm cache
npm cache clean --force

# Browser cache
Ctrl+Shift+Delete  # Open Clear Browsing Data
```

### Issue: Wrong port being used

**Solution**:
```bash
# 1. Edit app.py
# Change: app.run(port=5000)
# To: app.run(port=5001)

# 2. Edit App.js
// Change: http://localhost:5000
// To: http://localhost:5001

# 3. Check no other app using port
netstat -ano | findstr :5000  # Windows
lsof -i :5000                 # Mac/Linux
```

## Testing Issues

### Issue: Test script won't run

**Solution**:
```bash
# 1. Check Python 3
python --version  # Should be 3.8+

# 2. Add execute permission
chmod +x test_system.py

# 3. Run with Python explicitly
python test_system.py

# 4. Check imports
python -c "from bm25_retriever import BM25Retriever"
```

### Issue: Test failures

**Solution**:
```bash
# 1. Run with verbose output
python -v test_system.py

# 2. Check individual components
python -c "from bm25_retriever import BM25Retriever; print('✅ BM25 OK')"

# 3. Check policies.json is valid
python -c "import json; json.load(open('backend/policies.json'))"

# 4. Check backend is running
curl http://localhost:5000/api/health
```

## Git Issues

### Issue: Cannot push/pull

**Solution**:
```bash
# 1. Check git status
git status

# 2. Commit changes
git add .
git commit -m "message"

# 3. Check remote
git remote -v

# 4. Pull before push
git pull origin main
git push origin main
```

## Windows-Specific Issues

### Issue: `python` command not found

**Solution**:
```bash
# 1. Use python3
python3 app.py

# 2. Add Python to PATH
# Control Panel → System → Advanced → Environment Variables
# Add: C:\Users\YourName\AppData\Local\Programs\Python\Python39

# 3. Use full path
C:\Python39\python.exe app.py
```

### Issue: Path separators wrong

**Solution**:
```python
# Instead of:
path = "backend/policies.json"  # Works on Windows but inconsistent

# Use pathlib:
from pathlib import Path
path = Path("backend") / "policies.json"

# Or use os.path.join:
import os
path = os.path.join("backend", "policies.json")
```

## Mac-Specific Issues

### Issue: Port permission denied

**Solution**:
```bash
# Use port > 1024 (doesn't need sudo)
# Change app.py: app.run(port=5000)

# Or use sudo (not recommended)
sudo python app.py
```

### Issue: Homebrew Python vs System Python

**Solution**:
```bash
# Use specific version
python3 app.py

# Or set default
alias python=python3
```

## Linux-Specific Issues

### Issue: Virtual environment activation

**Solution**:
```bash
# Create venv
python3 -m venv venv

# Activate
source venv/bin/activate

# Check activated
which python  # Should show venv path
```

## General Debugging Tips

### 1. Add Debug Prints

```python
# In bm25_retriever.py
print(f"DEBUG: Query={query}, Score={scores[0]:.2f}")

# In app.py
print(f"DEBUG: Mode={mode}, Docs={len(retrieved_docs)}")
```

### 2. Enable Debug Mode

```python
# In app.py
app.run(debug=True)  # Auto-reload on changes
```

### 3. Check Logs

```bash
# Backend logs
tail -f backend/logs/support_interactions.log

# Browser console
F12 → Console tab

# Network tab
F12 → Network → Check requests/responses
```

### 4. Use Debugger

```python
# In app.py
import pdb

@app.route('/api/debug')
def debug():
    pdb.set_trace()  # Debugger will stop here
    return "debug"
```

### 5. Validation

```bash
# Validate JSON
cat backend/policies.json | python -m json.tool

# Check Python syntax
python -m py_compile backend/app.py

# Lint Python
pip install pylint
pylint backend/app.py
```

## Still Having Issues?

1. **Check logs** in `backend/logs/`
2. **Check browser console** (F12)
3. **Check terminal output** where servers are running
4. **Google the error message**
5. **Check README.md** and documentation
6. **Test API endpoints** with curl
7. **Enable debug mode** for more info
8. **Review code** for recent changes

---

**More questions? Check README.md or ARCHITECTURE.md**
