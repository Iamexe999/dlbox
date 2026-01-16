# dlbox

dlbox is a zero-cost, no-JavaScript, seedbox-like download manager built on
top of aria2 and Python, designed especially for restricted networks
(e.g. school or campus Wi-Fi).

It provides:
- resumable HTTPS downloads
- background download queueing
- checksum verification
- Windows + WSL quality-of-life helpers
- no torrents on restricted networks

This is not a real remote seedbox. Instead, it provides the workflow
of a seedbox using only legal, standard HTTPS traffic.

---

## Features

- Background download queue (aria2 session-based)
- Resume interrupted downloads
- Multi-connection HTTPS downloads
- SHA-256 hashing and verification
- Add links from Windows clipboard
- Open downloads directly in Windows Explorer
- Clean up `.aria2` partial files
- Batch-add URLs from a text file
- No JavaScript
- Zero cost

---

## Requirements

- Windows 10/11
- WSL (Arch Linux or Kali Linux recommended)
- Python 3.9+
- aria2

### Install dependencies

Kali (WSL):
```bash
sudo apt update
sudo apt install -y python3 aria2
Arch (WSL):

bash
Copy code
sudo pacman -Syu --noconfirm python aria2
Installation
Clone the repository:

bash
Copy code
git clone https://github.com/<your-username>/dlbox.git
cd dlbox
Create the directory structure:

bash
Copy code
mkdir -p ~/dlbox/{downloads,meta,logs}
Copy dlbox.py into ~/dlbox/ and make it executable:

bash
Copy code
chmod +x ~/dlbox/dlbox.py
Optional but recommended: make it a system command:

bash
Copy code
sudo ln -sf ~/dlbox/dlbox.py /usr/local/bin/dlbox
Usage
Start the downloader:

bash
Copy code
dlbox start
Add a download:

bash
Copy code
dlbox add https://example.com/file.iso
Check status:

bash
Copy code
dlbox status
Stop the downloader:

bash
Copy code
dlbox stop
Checksum Verification
Get SHA-256:

bash
Copy code
dlbox sha256 filename.iso
Verify against an expected hash:

bash
Copy code
dlbox verify filename.iso --sha256 <expected_hash>
Windows Integration Helpers
These helpers are optional but recommended.

Add from Windows clipboard (dlclip):

bash
Copy code
dlclip
Open downloads folder in Explorer (dlopen):

bash
Copy code
dlopen
Batch-add URLs from a file (dladdfile):

bash
Copy code
dladdfile links.txt
Clean leftover .aria2 files (dlclean):

bash
Copy code
dlclean
File locations
Downloaded files are stored in:

bash
Copy code
~/dlbox/downloads
From Windows Explorer:

arduino
Copy code
\\wsl$\kali\home\<your_user>\dlbox\downloads
(or Arch instead of kali)

What dlbox is not
Not a remote server

Not a paid seedbox

Not a torrent evasion tool

Not intended to bypass institutional policy

dlbox only manages standard HTTPS downloads using open-source tools.

Rationale
Many networks block BitTorrent but allow HTTPS.
dlbox provides a clean, legal, reproducible workflow that:

works on restricted networks

teaches practical tooling (aria2, Python, WSL)

avoids unreliable “free seedbox” approaches