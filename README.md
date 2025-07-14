
# ScanBot

**ScanBot** is a flexible Python tool designed to find web endpoints that do **not** enforce rate limiting, helping security researchers identify potential vulnerabilities related to high request rates.

---

## Features

- Customizable requests per second (RPS)  
- Filter HTTP status codes to include or exclude  
- Support for custom HTTP headers  
- Silent mode and optional output file saving  
- Color-coded console output for easy reading  
- Informative banner and usage warnings for responsible testing  

---

## Installation

1. Clone this repository or download `currate.py`

2. Install required Python packages:

```bash
pip install -r requirements.txt
````

---

## Usage

```bash
python3 ScanBot.py -u https://example.com -w /path/to/wordlist.txt -r 10 -fs 200,403 -fc 404 -o output.txt
```

### Arguments

* `-u`, `--url`: Target base URL (required)
* `-w`, `--wordlist`: Path to wordlist file (required)
* `-r`, `--rps`: Requests per second (default 10)
* `-fs`, `--filter-status`: Comma-separated HTTP status codes to include
* `-fc`, `--filter-status-blacklist`: Comma-separated status codes to exclude
* `-o`, `--output`: Output file to save valid endpoints
* `-s`, `--silent`: Silent mode, no console output except errors
* `--headers`: Custom headers as JSON string, e.g. `'{"User-Agent": "currate"}'`
* `-m`, `--max`: Max requests to send (default 1000)

---

## Wordlists

You can find useful wordlists for endpoint discovery at the SecLists repository:
[https://github.com/danielmiessler/SecLists/tree/master/Discovery/Web-Content](https://github.com/danielmiessler/SecLists/tree/master/Discovery/Web-Content)

Example wordlist to use: `common.txt`

---

## Warning

Please use **currate** responsibly. Do not abuse or overload servers without explicit permission. High request rates can cause service disruption and legal consequences.

---

## Support

If you find this tool useful, consider supporting me on GitHub:
[https://github.com/MicheleMessina-debug](https://github.com/MicheleMessina-debug)

---

## License

This project is licensed under the MIT License. See LICENSE file for details.


