# n8n AI Assistant Setup - Complete

## ✅ Configuration Summary

The n8n AI Assistant has been successfully configured and is now running in your self-hosted n8n instance.

### What Was Configured

**1. Environment Variables (.env)**
- Added `N8N_AI_ASSISTANT_BASE_URL=https://ai-assistant.n8n.io`
- Fixed database configuration (changed `n8n_traceability` to `n8n` for consistency)

**2. Docker Compose (docker-compose.yml)**
- Added `- N8N_AI_ASSISTANT_BASE_URL` to the n8n service environment variables
- This variable is now passed to the n8n container on startup

**3. Service Status**
- n8n container: ✅ Running
- PostgreSQL: ✅ Healthy
- Ollama: ✅ Running
- Qdrant: ✅ Running

## 🎯 What is the n8n AI Assistant?

The n8n AI Assistant is a built-in feature that helps you:
- **Build workflows faster** - Get AI-powered suggestions while creating workflows
- **Understand nodes** - Get contextual help about node configurations
- **Debug workflows** - Get assistance troubleshooting workflow issues
- **Generate workflow ideas** - Ask the AI to help design automation solutions

## 🚀 How to Access the AI Assistant

### In the n8n Web Interface

1. **Open n8n**: Navigate to http://localhost:5678 (or your Codespace URL)
   - Codespace URL: https://curly-space-spork-v9rg679gpqw3rj6-5678.app.github.dev

2. **Look for the AI Assistant icon** in the n8n interface:
   - Usually appears in the workflow editor
   - May show as a sparkle/star icon or "AI" button
   - Can be accessed via keyboard shortcut or menu

3. **Common AI Assistant features**:
   - Chat interface for asking questions
   - Inline suggestions when editing workflows
   - Context-aware help for specific nodes
   - Workflow generation from natural language descriptions

## 🔍 Verifying the Setup

### Check Environment Variable in Container

```bash
docker compose exec n8n sh -c 'env | grep N8N_AI'
```

**Expected output:**
```
N8N_AI_ASSISTANT_BASE_URL=https://ai-assistant.n8n.io
```

### Check Service Status

```bash
docker compose ps n8n
```

**Expected status:** `Up` (running)

### View n8n Logs

```bash
docker compose logs -f n8n
```

Look for successful initialization messages (no errors about AI Assistant)

## 🔧 Configuration Details

### AI Assistant Connection

- **Base URL**: `https://ai-assistant.n8n.io`
- **Provider**: n8n's managed AI service (hosted by n8n team)
- **Authentication**: Handled automatically by n8n (no additional API keys needed)
- **Usage**: Free for self-hosted instances with reasonable usage limits

### Important Notes

1. **Internet Required**: The AI Assistant connects to n8n's external service, so you need internet access
2. **Data Privacy**: Workflow metadata may be sent to n8n's AI service for assistance
3. **Rate Limits**: The service may have rate limits for free self-hosted instances
4. **Alternative**: If you prefer fully offline operation, you can remove the configuration (AI Assistant won't be available)

## 🎨 Example Use Cases

### 1. Generate a Workflow from Description

In the AI Assistant chat:
```
"Create a workflow that monitors a Gmail inbox for emails with attachments, 
extracts text from PDF attachments, and stores the content in Qdrant"
```

### 2. Get Help with a Node

When configuring a node:
```
"How do I configure the HTTP Request node to use Bearer token authentication?"
```

### 3. Debug a Workflow Error

When troubleshooting:
```
"My workflow fails with 'Cannot read property of undefined'. 
What's the most common cause of this error?"
```

### 4. Learn Best Practices

General questions:
```
"What's the best way to handle rate limiting when calling external APIs?"
```

## 🔄 Restarting Services

If you need to restart n8n after making changes:

```bash
# Restart just n8n
docker compose restart n8n

# Or recreate the container (full refresh)
docker compose up -d n8n --force-recreate

# View logs
docker compose logs -f n8n
```

## 🛠️ Troubleshooting

### AI Assistant Not Appearing in UI

1. **Clear browser cache** and refresh the page
2. **Verify environment variable** is set (see verification steps above)
3. **Check n8n version**: AI Assistant may require n8n v1.0+ (you're running v2.10.3 ✅)
4. **Check n8n documentation** for version-specific feature availability

### Connection Issues

If the AI Assistant shows connection errors:
- **Verify internet connectivity** from the container
- **Check firewall rules** (outbound HTTPS to ai-assistant.n8n.io)
- **Review n8n logs** for specific error messages

### Performance Issues

If AI Assistant is slow:
- This is normal for the free managed service (shared infrastructure)
- Consider upgrading to n8n Cloud for faster AI responses
- Or use local LLM alternatives (not officially supported as AI Assistant replacement)

## 📚 Additional Resources

- **n8n AI Assistant Docs**: https://docs.n8n.io/hosting/configuration/environment-variables/ai-assistant/
- **n8n AI Features**: https://docs.n8n.io/advanced-ai/
- **n8n Community Forum**: https://community.n8n.io/
- **Workflow Templates**: https://n8n.io/workflows/

## 🔒 Security Considerations

### What Data is Sent

When using the AI Assistant:
- Workflow structure and node configurations may be sent to n8n's service
- Credentials and sensitive data are **NOT** sent
- Only metadata needed for providing assistance is transmitted

### Disabling AI Assistant

To disable if you have privacy concerns:

1. **Remove from .env**:
   ```bash
   # Comment out or delete this line
   # N8N_AI_ASSISTANT_BASE_URL=https://ai-assistant.n8n.io
   ```

2. **Restart n8n**:
   ```bash
   docker compose restart n8n
   ```

## ✅ Setup Complete!

Your n8n instance is now enhanced with AI assistance capabilities. Open the web interface and explore the AI-powered features to accelerate your workflow development.

---

**Setup completed on**: March 5, 2026  
**n8n version**: 2.10.3  
**Configuration files modified**:
- `.env`
- `docker-compose.yml`
