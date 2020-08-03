#!/bin/bash
hugo --minify
rsync -avh -e ssh public/ root@157.245.84.159:/var/www/html/cyberalsolutions.com
