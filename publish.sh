#!/bin/bash
echo "No build step: site is pure static HTML"
#rsync -avh -e ssh public/ ryan@10.10.0.118:/opt/cyberalsolutions.com/
rsync -avh -e ssh public/ /home/ryan/repos/CyberalWebsite


