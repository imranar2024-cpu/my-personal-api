from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

@app.route('/download', methods=['GET'])
def download():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"status": False, "error": "No URL provided"}), 400
        
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    }

    if os.path.exists('cookies.txt'):
        ydl_opts['cookiefile'] = 'cookies.txt'
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

            # প্রথমে সরাসরি url খুঁজবে
            direct_link = info.get('url')

            # না থাকলে formats থেকে নেবে
            if not direct_link and 'formats' in info:
                for f in info['formats']:
                    if f.get('url'):
                        direct_link = f['url']
                        break

            # playlist হলে entries থেকে নেবে
            if not direct_link and 'entries' in info:
                direct_link = info['entries'][0].get('url')

            if direct_link:
                return jsonify({"status": True, "video_url": direct_link})
            else:
                return jsonify({"status": False, "error": "Direct link not found"}), 404
                
    except Exception as e:
        return jsonify({"status": False, "error": f"Extraction failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
