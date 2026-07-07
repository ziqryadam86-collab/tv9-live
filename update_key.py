import requests
import re
import base64

url = "https://buttoncalc.blogspot.com/2026/06/photo.html?m=1"

# Fungsi tukar HEX ke Base64 format ClearKey (Kalis ralat)
def hex_to_base64(hex_str):
    clean_hex = re.sub(r'[^A-Fa-f0-9]', '', hex_str)
    bytes_data = bytes.fromhex(clean_hex)
    b64 = base64.b64encode(bytes_data).decode('utf-8')
    return b64.replace('=', '').replace('+', '-').replace('/', '_')

try:
    # 1. Ambil data dari blogspot
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    html = response.text

    # 2. Tapis kotak TV9
    channels = re.findall(r'<li class="channel-item">.*?</li>', html, re.DOTALL)
    tv9_html = None
    for channel in channels:
        if 'alt="TV9"' in channel or 'class="channel-name">TV9</span>' in channel:
            tv9_html = channel
            break

    if tv9_html:
        kid_match = re.search(r'kid&quot;\s*:\s*&quot;([a-f0-9]{32})&quot;', tv9_html, re.IGNORECASE)
        key_match = re.search(r'key&quot;\s*:\s*&quot;([a-f0-9]{32})&quot;', tv9_html, re.IGNORECASE)

        if kid_match and key_match:
            KID = kid_match.group(1)
            KEY = key_match.group(1)
            
            # === HAA NI SAYA DAH MASUKKAN BALIK UNTUK ABANG ===
            # Simpan fail keys.txt dahulu supaya GitHub tak error
            with open("keys.txt", "w", encoding="utf-8") as f:
                f.write(f"{KID}:{KEY}")
            print("Berjaya menyimpan fail keys.txt")
            
            # Tukar ke Base64 untuk MPD
            base64_kid = hex_to_base64(KID)
            base64_key = hex_to_base64(KEY)
            
            # 3. Tarik manifest asli TV9
            target_mpd = "https://ngtv-live-cbj.gcdn.co/Content/DASH/Live/channel(TV9)/master.mpd"
            mpd_res = requests.get(target_mpd, headers={"User-Agent": "Mozilla/5.0 (Linux; Android 10; K)"})
            mpd_text = mpd_res.text
            
            # 4. Jahit siap-siap ClearKey DRM dalam kod MPD
            drm_header = f"""
    <ContentProtection schemeIdUri="urn:uuid:e251367d-bb43-4d70-970f-5544af77c198" value="ClearKey">
      <clearkey:Laurl Lic_type="EME-CLEARKEY">data:application/json,{"{"}"keys":[{"{"}"kty":"oct","kid":"{base64_kid}","k":"{base64_key}"{"}"}],"type":"temporary"{"}"}</clearkey:Laurl>
    </ContentProtection>"""
            
            final_mpd = mpd_text.replace("<AdaptationSet", f"<AdaptationSet>\n{drm_header}")
            
            # 5. Simpan fail tv9.mpd
            with open("tv9.mpd", "w", encoding="utf-8") as f:
                f.write(final_mpd)
                
            print("Berjaya menjahit MPD TV9 terbaru!")
        else:
            print("Kunci gagal dijumpai.")
    else:
        print("Blok TV9 tidak dijumpai.")

except Exception as e:
    print(f"Ralat: {e}")
        
