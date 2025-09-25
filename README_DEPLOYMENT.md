# Deployment Instructions for Backend on Railway

This guide will help you deploy the Flask backend on Railway.app to get a live URL.

## Prerequisites
- Create a Railway account at https://railway.app/
- Install Git and have your backend code in a GitHub repository or local folder

## Steps to Deploy

1. Go to https://railway.app/ and log in.

2. Click on "New Project" and select "Deploy from GitHub repo" or "Start from Scratch".

3. If deploying from GitHub:
   - Connect your GitHub account.
   - Select the repository containing the backend folder.

4. If starting from scratch:
   - Upload your backend folder files.

5. Railway will detect the `Procfile` and `requirements.txt` automatically.

6. Railway will install dependencies and run the command in `Procfile` (`python server.py`).

7. Once deployed, Railway will provide a public URL for your backend API.

8. You can test the API endpoints using the URL, for example:
   - GET `https://your-project-url/api/trips`
   - POST `https://your-project-url/api/trips`

## Notes
- Make sure your `server.py` listens on the port provided by Railway via the `PORT` environment variable. Modify your `app.run()` in `server.py` as follows:

```python
import os

if __name__ == '__main__':
    create_table()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
```

- Commit and push this change before deploying.

## Alternative Platforms
You can also deploy on Render.com or Heroku with similar steps.

---

If you want, I can help you with these code changes or further deployment assistance.
