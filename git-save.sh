#!/bin/bash
# Alle Änderungen sichern und committen

# aktuelles Datum/Zeit für Commit-Message
MSG="Autosave $(date '+%Y-%m-%d %H:%M:%S')"

# Änderungen ins Staging
git add -A

# Commit erstellen
git commit -m "$MSG"

# Optional: gleich pushen, falls Remote vorhanden
if git remote get-url origin &>/dev/null; then
  git push
fi
