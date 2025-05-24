from flask import Flask, request, send_file
import instaloader
import os
import uuid

app = Flask(__name__)
loader = instaloader.Instaloader(dirname_pattern='downloads', save_metadata=False)

@app.route('/')
def home():
    return "Reel Downloader API is running."

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    if not url or "/reel/" not in url:
        return {"error": "Invalid URL"}, 400

    shortcode = url.split("/reel/")[1].split("/")[0]
    try:
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        temp_id = str(uuid.uuid4())
        temp_path = os.path.join("downloads", temp_id)
        os.makedirs(temp_path, exist_ok=True)
        loader.dirname_pattern = temp_path
        loader.download_post(post, target='reel')

        for file in os.listdir(temp_path):
            if file.endswith(".mp4"):
                return send_file(os.path.join(temp_path, file), as_attachment=True)

        return {"error": "No video found"}, 404
    except Exception as e:
        return {"error": str(e)}, 500

# ✅ IMPORTANT: This allows Render to host your app properly!
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
