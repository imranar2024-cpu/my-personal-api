from flask import Flask, request, jsonify
import yt_dlp
import requests

app = Flask(__name__)

def resolve_url(url):
    try:
        # ফেসবুকের /share/ লিংকগুলোকে আসল ভিডিও লিংকে রূপান্তর করার জন্য
        response = requests.head(url, allow_redirects=True, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        return response.url
    except Exception:
        return url

@app.route('/download', methods=['GET'])
def download():
    raw_url = request.args.get('url')
    if not raw_url:
        return jsonify({"status": False, "error": "No URL provided"}), 400
        
    # রিয়েল URL বের করা
    video_url = resolve_url(raw_url)
        
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Sec-Fetch-Mode': 'navigate',
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            direct_link = info.get('url')
            
            if not direct_link and 'entries' in info:
                direct_link = info['entries'][0].get('url')
                
            if direct_link:
                return jsonify({"status": True, "video_url": direct_link})
            else:
                return jsonify({"status": False, "error": "Direct link not found"}), 404
                
    except Exception as e:
        return jsonify({"status": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
