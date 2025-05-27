import requests
import time
import json
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Semaphore

try:
    from pyfiglet import Figlet
except ImportError:
    print("Missing module 'pyfiglet'. Install it with: pip install pyfiglet")
    exit(1)

# ANSI Colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
RESET = "\033[0m"

DEFAULT_MAX_REQUESTS = 1000
DEFAULT_RPS = 10

def print_banner():
    f = Figlet(font='slant')
    print(CYAN + f.renderText('currate') + RESET)

def print_welcome():
    print(CYAN + "="*60 + RESET)
    print(f"{CYAN}Welcome to currate!{RESET}")
    print(f"{CYAN}Use responsibly. Don't overload target servers with too many requests.{RESET}")
    print(f"{CYAN}Support the project on GitHub: {YELLOW}https://github.com/8TB-Available{RESET}")
    print(CYAN + "="*60 + RESET + "\n")

def load_endpoints(wordlist_path):
    with open(wordlist_path, "r") as file:
        return [line.strip() for line in file if line.strip()]

def test_endpoint(base_url, endpoint, headers, delay, limiter):
    url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
    with limiter:
        time.sleep(delay)
        try:
            response = requests.get(url, headers=headers, timeout=5)
            return (endpoint, response.status_code)
        except requests.RequestException:
            return (endpoint, None)

def print_status(endpoint, status, silent):
    if silent:
        return
    if status == 200:
        print(f"{GREEN}[200 OK] {endpoint}{RESET}")
    elif status == 429:
        print(f"{RED}[429 RATE LIMIT] {endpoint}{RESET}")
    elif status:
        print(f"{YELLOW}[{status}] {endpoint}{RESET}")
    else:
        print(f"{RED}[ERROR] {endpoint} -> No response{RESET}")

def main():
    parser = argparse.ArgumentParser(description="currate - find endpoints without rate limiting")
    parser.add_argument("-u", "--url", required=True, help="Target base URL (e.g. https://example.com)")
    parser.add_argument("-w", "--wordlist", required=True, help="Wordlist file path")
    parser.add_argument("-r", "--rps", type=int, default=DEFAULT_RPS, help="Requests per second (default 10)")
    parser.add_argument("-fs", "--filter-status", type=str, help="Comma separated list of status codes to INCLUDE (e.g. 200,403)")
    parser.add_argument("-fc", "--filter-status-blacklist", type=str, help="Comma separated list of status codes to EXCLUDE")
    parser.add_argument("-o", "--output", help="Output file to save valid endpoints")
    parser.add_argument("-s", "--silent", action="store_true", help="Silent mode (no console output except errors)")
    parser.add_argument("-m", "--max", type=int, default=DEFAULT_MAX_REQUESTS, help="Maximum requests to send (default 1000)")
    parser.add_argument("--headers", type=str, help="Custom headers in JSON format, e.g. '{\"User-Agent\": \"currate\"}'")

    args = parser.parse_args()

    print_banner()
    print_welcome()

    base_url = args.url
    wordlist_path = args.wordlist
    rps = args.rps
    max_requests = args.max
    silent = args.silent
    output_path = args.output

    headers = {}
    if args.headers:
        try:
            headers = json.loads(args.headers)
        except json.JSONDecodeError:
            print(f"{RED}[!] Invalid JSON for headers{RESET}")
            return

    status_filter_include = None
    status_filter_exclude = None

    if args.filter_status:
        try:
            status_filter_include = set(int(x) for x in args.filter_status.split(","))
        except ValueError:
            print(f"{RED}[!] Invalid --filter-status values{RESET}")
            return

    if args.filter_status_blacklist:
        try:
            status_filter_exclude = set(int(x) for x in args.filter_status_blacklist.split(","))
        except ValueError:
            print(f"{RED}[!] Invalid --filter-status-blacklist values{RESET}")
            return

    delay = 1.0 / rps if rps > 0 else 0
    limiter = Semaphore(rps if rps > 0 else 1)

    endpoints = load_endpoints(wordlist_path)
    valid_endpoints = []
    count = 0
    rate_limit_detected = False

    if not silent:
        print(f"[+] Target: {base_url}")
        print(f"[+] Rate: {rps} requests/sec | Max requests: {max_requests}")
        if headers:
            print(f"[+] Custom headers: {headers}")
        if status_filter_include:
            print(f"[+] Including status codes: {sorted(status_filter_include)}")
        if status_filter_exclude:
            print(f"[+] Excluding status codes: {sorted(status_filter_exclude)}")
        if output_path:
            print(f"[+] Output file: {output_path}")
        print("")

    with ThreadPoolExecutor(max_workers=max(rps * 2, 10)) as executor:
        futures = []
        for endpoint in endpoints:
            if count >= max_requests:
                break
            futures.append(executor.submit(test_endpoint, base_url, endpoint, headers, delay, limiter))
            count += 1

        for future in as_completed(futures):
            endpoint, status = future.result()
            if status == 429:
                rate_limit_detected = True

            # Filtering logic:
            if status is None:
                # skip errors
                continue

            if status_filter_include is not None and status not in status_filter_include:
                continue

            if status_filter_exclude is not None and status in status_filter_exclude:
                continue

            print_status(endpoint, status, silent)

            if status == 200:
                valid_endpoints.append(endpoint)

    if output_path:
        try:
            with open(output_path, "w") as f:
                for ep in valid_endpoints:
                    f.write(ep + "\n")
            if not silent:
                print(f"{GREEN}[+] Saved {len(valid_endpoints)} valid endpoints to: {output_path}{RESET}")
        except Exception as e:
            print(f"{RED}[!] Error saving output file: {e}{RESET}")

    if not silent:
        if rate_limit_detected:
            print(f"{RED}[!] Rate limiting detected! The site HAS rate limits.{RESET}")
        else:
            print(f"{GREEN}[!] No rate limiting detected! The site is vulnerable to high request rates.{RESET}")

        print("[+] Scan complete.")

if __name__ == "__main__":
    main()
