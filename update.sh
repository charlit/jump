#!/bin/sh
# Mac mini: pull the latest jump from GitHub; restart the container only if server.py changed.
# Installed as a cron job (every 5 min), touches nothing but ~/jump and the "jump" container.
PATH=/usr/local/bin:/opt/homebrew/bin:$PATH
cd ~/jump || exit 1
for f in index.html server.py update.sh; do
  curl -fsSL "https://raw.githubusercontent.com/charlit/jump/main/$f" -o "$f.new" || exit 1
done
cmp -s server.py.new server.py || restart=1
for f in index.html server.py update.sh; do mv "$f.new" "$f"; done
[ -n "$restart" ] && docker restart jump >/dev/null
exit 0
