FROM joseluisq/static-web-server:2-alpine 

COPY . /home/sws/public

# static-web-server defaults to `Cache-Control: max-age=86400` on everything it
# serves, including HTML. Every deploy was therefore invisible for up to 24 hours
# to anyone who had visited before -- including us, which is how "I don't see any
# changes on the site" happened after a deploy that had in fact gone fine.
#
# Disabled: with no Cache-Control, browsers fall back to heuristic freshness from
# Last-Modified, so a file that just changed is revalidated immediately (a cheap
# 304) while genuinely static files still cache. Images and CSS/JS are unaffected
# -- NPM's asset cache sets its own policy for those at the proxy.
ENV SERVER_CACHE_CONTROL_HEADERS=false

EXPOSE 80
