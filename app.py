from flask import Flask, request, jsonify
import yt_dlp
import requests
import re

app = Flask(__name__)

def get_facebook_direct_url(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    # শর্ট লিংক ও রিডাইরেক্ট ফলো করা
    res = requests.get(url, headers=headers, allow_redirects=True, timeout=12)
    html = res.text
    
    # ভিডিও সোর্স URL খোঁজা (HD অথবা SD)
    hd_match = re.search(r'hd_src:"([^"]+)"', html) or re.search(r'hd_src_no_ratelimit:"([^"]+)"', html)
    sd_match = re.search(r'sd_src:"([^"]+)"', html) or re.search(r'sd_src_no_ratelimit:"([^"]+)"', html)
    
    video_url = None
    if hd_match:
        video_url = hd_match.group(1)
    elif sd_match:
        video_url = sd_match.group(1)
    else:
        # বিকল্প ব্রাউজার মেটা ট্যাগ প্যাটার্ন
        meta_match = re.search(r'<meta property="og:video" content="([^"]+)"', html) or re.search(r'"playable_url":"([^"]+)"', html)
        if meta_match:
            video_url = meta_match.group(1).replace(r'\/', '/')
            
    return video_url

@app.route('/download', methods=['GET'])
def download():
    raw_url = request.args.get('url')
    if not raw_url:
        return jsonify({"status": False, "error": "No URL provided"}), 400
        
    try:
        # ১. ফেসবুক ভিডিও হলে ডিরেক্ট স্ক্র্যাপার দিয়ে চেষ্টা করা
        if 'facebook.com' in raw_url or 'fb.watch' in raw_url:
            direct_link = get_facebook_direct_url(raw_url)
            if direct_link:
                return jsonify({"status": True, "video_url": direct_link})

        # ২. ইনস্টাগ্রাম বা অন্যান্য প্ল্যাটফর্মের জন্য yt-dlp
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
            }
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(raw_url, download=False)
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
