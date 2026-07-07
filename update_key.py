import requests
import re
import base64

url = "https://buttoncalc.blogspot.com/2026/06/photo.html?m=1"

# Fungsi tukar HEX ke Base64 format ClearKey
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
            
            # Simpan fail keys.txt
            with open("keys.txt", "w", encoding="utf-8") as f:
                f.write(f"{KID}:{KEY}")
            print("Berjaya menyimpan fail keys.txt")
            
            # Tukar ke Base64 untuk ClearKey
            base64_kid = hex_to_base64(KID)
            base64_key = hex_to_base64(KEY)
            
            # 3. KITA KLON & CIPTA STRUKTUR MPD TV9 TERUS DALAM KOD (Kalis Sekat!)
            template_mpd = f"""<?xml version="1.0" encoding="utf-8"?>
<MPD xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="urn:mpeg:dash:schema:mpd:2011" xmlns:clearkey="http://dashif.org/guidelines/clearKey" xsi:schemaLocation="urn:mpeg:dash:schema:mpd:2011 DASH-MPD.xsd" profiles="urn:mpeg:dash:profile:isoff-live:2011" type="dynamic" minimumUpdatePeriod="PT5S" availabilityStartTime="2021-11-23T03:36:20Z" publishTime="2023-10-18T00:00:00Z" timeShiftBufferDepth="PT30S" maxSegmentDuration="PT9S">
  <Period id="p0" start="PT0S">
    <AdaptationSet id="0" contentType="video" segmentAlignment="true" bitstreamSwitching="true" maxWidth="1920" maxHeight="1080" maxFrameRate="25" par="16:9">
      <ContentProtection schemeIdUri="urn:uuid:e251367d-bb43-4d70-970f-5544af77c198" value="ClearKey">
        <clearkey:Laurl Lic_type="EME-CLEARKEY">data:application/json,{{"keys":[{{"kty":"oct","kid":"{base64_kid}","k":"{base64_key}"}}],"type":"temporary"}}</clearkey:Laurl>
      </ContentProtection>
      <SegmentTemplate timescale="1000" duration="8000" startNumber="1" initialization="https://ngtv-live-cbj.gcdn.co/Content/DASH/Live/channel(TV9)/init-video=$RepresentationID$.dash" media="https://ngtv-live-cbj.gcdn.co/Content/DASH/Live/channel(TV9)/media-video=$RepresentationID$-$Number$.dash"/>
      <Representation id="1" mimeType="video/mp4" codecs="avc1.64001f" width="1280" height="720" frameRate="25" sar="1:1" bandwidth="2200000"/>
      <Representation id="2" mimeType="video/mp4" codecs="avc1.640028" width="1920" height="1080" frameRate="25" sar="1:1" bandwidth="4500000"/>
    </AdaptationSet>
    <AdaptationSet id="1" contentType="audio" segmentAlignment="true" lang="ms">
      <ContentProtection schemeIdUri="urn:uuid:e251367d-bb43-4d70-970f-5544af77c198" value="ClearKey">
        <clearkey:Laurl Lic_type="EME-CLEARKEY">data:application/json,{{"keys":[{{"kty":"oct","kid":"{base64_kid}","k":"{base64_key}"}}],"type":"temporary"}}</clearkey:Laurl>
      </ContentProtection>
      <SegmentTemplate timescale="1000" duration="8000" startNumber="1" initialization="https://ngtv-live-cbj.gcdn.co/Content/DASH/Live/channel(TV9)/init-audio=$RepresentationID$.dash" media="https://ngtv-live-cbj.gcdn.co/Content/DASH/Live/channel(TV9)/media-audio=$RepresentationID$-$Number$.dash"/>
      <Representation id="1" mimeType="audio/mp4" codecs="mp4a.40.2" audioSamplingRate="48000" bandwidth="128000"/>
    </AdaptationSet>
  </Period>
</MPD>"""
            
            # 4. Simpan fail tv9.mpd
            with open("tv9.mpd", "w", encoding="utf-8") as f:
                f.write(template_mpd)
                
            print("Berjaya mencipta MPD TV9 tulen tanpa ralat 403!")
        else:
            print("Kunci gagal dijumpai.")
    else:
        print("Blok TV9 tidak dijumpai.")

except Exception as e:
    print(f"Ralat: {e}")
            
