#!/bin/bash
hugo --minify
#rsync -avh -e ssh public/ ryan@10.10.0.118:/opt/cyberalsolutions.com/
rsync -avh -e ssh public/ /home/ryan/repos/CyberalWebsite


