from flask import Flask, request, jsonify
import yt_dlp
import requests

app = Flask(__name__)

def fetch_facebook_api(fb_url):
    try:
        # ক্লাউড ব্লক বাইপাস করার জন্য ওপেন গেটওয়ে কল
        api_endpoint = f"https://api-social.shuvro.workers.dev/facebook?url={fb_url}"
        res = requests.get(api_endpoint, timeout=12).json()
        if res.get("status") and res.get("video_url"):
            return res.get("video_url")
    except Exception:
        pass
        
    try:
        # বিকল্প ব্যাকআপ গেটওয়ে
        backup_endpoint = f"https://tools.betabotz.eu.org/tools/fbdl?url={fb_url}"
        res = requests.get(backup_endpoint, timeout=12).json()
        if res.get("result"):
            return res.get("result").get("video_url") or res.get("result").get("hd") or res.get("result").get("sd")
    except Exception:
        pass
    return None

@app.route('/download', methods=['GET'])
def download():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"status": False, "error": "No URL provided"}), 400
        
    # ১. ফেসবুক হলে গেটওয়ে ব্যবহার
    if 'facebook.com' in video_url or 'fb.watch' in video_url:
        fb_direct = fetch_facebook_api(video_url)
        if fb_direct:
            return jsonify({"status": True, "video_url": fb_direct})
            
    # ২. ইনস্টাগ্রাম ও অন্যান্য সাইটের জন্য yt-dlp
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
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
