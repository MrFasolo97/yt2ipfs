# yt2ipfs
___
## A video and image importer from YouTube to IPFS
___
This API is meant to look for and/or save videos from YouTube to IPFS.

It's main intended use is as a complementary tool to sync videos from YouTube to DTube.

You ***should*** authenticate the users and videos ***outside*** the API, and the API should get request ***only*** from trusted programs and servers, mainly for copyright reasons.

### Requirements
This software needs:

- **youtube-dl** binary to be installed and in PATH variable
- **python 3**
- Full access to an **IPFS node** 
- Optionally a reverse proxy server as **NGINX** or similar

And was tested with:

- Ubuntu 21.04
- python 3.9.5

### Install and run
    git clone https://github.com/MrFasolo97/yt2ipfs && cd yt2ipfs
    pip3 install -r requirements.txt
    cp config_example.json config.json  # Remeber to add a strong API key,
                                        # and set or change what needed
    python3 main.py

What I'm going to suggest is usually something to avoid, but in this case it looks like it's safe to do so, exception
made for macOS. Check this comment and the next one: [IPFS Py Client Issue](https://github.com/ipfs-shipyard/py-ipfs-http-client/issues/296#issuecomment-905484061)

To make the library needed to add files to IPFS to work correctly, you should open the \_\_init\_\_.py file
and modify the VERSION\_MAXIMUM variable to be at least 0.0.1 bigger than what you're running on your
IPFS node (In my case 0.9.1 because I'm running 0.9.0). For me the path is the following:
	
	~/.local/lib/python3.9/site-packages/ipfshttpclient/client/__init__.py
