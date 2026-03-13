import asyncio
import httpx
import hashlib
from googlesearch import search

class MailScanner:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }

    async def check_github(self, email):
        """Finds public profiles, avatars, and names from GitHub."""
        url = f"https://api.github.com/search/users?q={email}+in:email"
        async with httpx.AsyncClient(headers=self.headers) as client:
            try:
                resp = await client.get(url)
                data = resp.json()
                if data.get("total_count", 0) > 0:
                    user = data["items"][0]
                    return {"site": "GitHub", "status": "Found", "details": f"User: {user['login']}", "url": user["html_url"], "avatar": user["avatar_url"]}
                return {"site": "GitHub", "status": "Not Found"}
            except:
                return {"site": "GitHub", "status": "Error"}

    async def check_microsoft(self, email):
        """Checks if a Microsoft/Outlook/Live account exists."""
        url = "https://login.microsoftonline.com/common/GetCredentialType"
        async with httpx.AsyncClient(headers=self.headers) as client:
            try:
                resp = await client.post(url, json={"username": email})
                exists = resp.json().get("IfExistsResult") == 0
                return {"site": "Microsoft", "status": "Registered" if exists else "Available"}
            except:
                return {"site": "Microsoft", "status": "Error"}

    async def check_spotify(self, email):
        """
        Checks if a Spotify account exists.
        FIX: the old spclient.wg.spotify.com endpoint is no longer publicly
        accessible. Use the current web signup validation endpoint instead.
        A 'status' of 20 still means the email is already taken.
        """
        url = "https://www.spotify.com/api/signup/validateEmail"
        params = {"email": email, "displayName": ""}
        async with httpx.AsyncClient(headers=self.headers) as client:
            try:
                resp = await client.get(url, params=params, follow_redirects=True)
                is_taken = resp.json().get("status") == 20
                return {"site": "Spotify", "status": "Registered" if is_taken else "Available"}
            except Exception as e:
                return {"site": "Spotify", "status": "Error", "details": str(e)}

    async def check_gravatar(self, email):
        """The most reliable way to get a profile picture (Avatar)."""
        email_hash = hashlib.md5(email.lower().encode()).hexdigest()
        url = f"https://www.gravatar.com/{email_hash}.json"
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url)
                if resp.status_code == 200:
                    entry = resp.json()["entry"][0]
                    return {"site": "Gravatar", "status": "Found", "details": entry.get("displayName"), "avatar": entry.get("thumbnailUrl")}
                return {"site": "Gravatar", "status": "Not Found"}
            except:
                return {"site": "Gravatar", "status": "Error"}

    async def check_linkedin(self, email):
        """
        Searches for LinkedIn profiles via Google.
        FIX: newer googlesearch-python removed 'num' and 'stop' kwargs.
        Use only 'num_results' (the current param name) and wrap in
        run_in_executor so the blocking call doesn't freeze the event loop.
        """
        query = f'site:linkedin.com/in "{email}"'
        try:
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                lambda: list(search(query, num_results=1))
            )
            if results:
                return {"site": "LinkedIn", "status": "Found", "details": "Profile found via search", "url": results[0]}
            return {"site": "LinkedIn", "status": "Not Found"}
        except Exception as e:
            return {"site": "LinkedIn", "status": "Error", "details": str(e)}

    async def check_haveibeenpwned(self, email):
        """
        Checks for data breaches.
        FIX: HIBP v3 requires a paid API key in the 'hibp-api-key' header.
        Without it the API returns 401, which was silently swallowed as "Error".
        Added the auth header (reads from env var HIBP_API_KEY) and surfaces a
        clear message when the key is missing so the user knows what to do.
        """
        import os
        api_key = os.environ.get("HIBP_API_KEY", "")
        if not api_key:
            return {"site": "HaveIBeenPwned", "status": "Skipped", "details": "Set HIBP_API_KEY env var (free key at haveibeenpwned.com)"}

        url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
        headers = {"User-Agent": "MailTrace-OSINT", "hibp-api-key": api_key}
        async with httpx.AsyncClient(headers=headers) as client:
            try:
                resp = await client.get(url)
                if resp.status_code == 200:
                    breaches = resp.json()
                    breach_names = [b['Name'] for b in breaches]
                    return {"site": "HaveIBeenPwned", "status": "Breached", "details": f"Found in {len(breaches)} breaches: {', '.join(breach_names[:3])}", "breaches": breaches}
                elif resp.status_code == 404:
                    return {"site": "HaveIBeenPwned", "status": "Safe"}
                elif resp.status_code == 401:
                    return {"site": "HaveIBeenPwned", "status": "Error", "details": "Invalid API key"}
                else:
                    return {"site": "HaveIBeenPwned", "status": "Error", "details": f"HTTP {resp.status_code}"}
            except Exception as e:
                return {"site": "HaveIBeenPwned", "status": "Error", "details": str(e)}

    async def check_amazon(self, email):
        return {"site": "Amazon", "status": "Check Not Implemented"}

    async def check_dropbox(self, email):
        return {"site": "Dropbox", "status": "Check Not Implemented"}

    async def scan_all(self, email):
        tasks = [
            self.check_github(email),
            self.check_microsoft(email),
            self.check_spotify(email),
            self.check_gravatar(email),
            self.check_linkedin(email),
            self.check_haveibeenpwned(email),
            self.check_amazon(email),
            self.check_dropbox(email)
        ]
        return await asyncio.gather(*tasks)