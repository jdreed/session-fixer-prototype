#!/bin/sh

set -e

CUSTOM_DOTFILES=".path .cshrc.mine .bashrc.mine .environment .bash_environment .startup.X .startup.tty"
PROTOTYPE=/usr/prototype_user

BACKUP_DIR="${HOME}/dotfiles-$(date +"%Y-%m-%d-%H%M.%S")"
if ! mkdir "$BACKUP_DIR"; then
    echo "Unable to back up dotfiles."
    echo "Could not create backup directory." >&2
    exit 1
fi

echo "Backing up dotfiles to: $BACKUP_DIR"
echo

for f in $CUSTOM_DOTFILES; do
    if [ -f "${HOME}/$f" ]; then
	mv -f "${HOME}/$f" "$BACKUP_DIR"
	echo "Backed up $f"
    fi
done

for f in $(ls $PROTOTYPE/.??*); do
    theirs="${HOME}/$(basename "$f")"
    echo -n "Checking $(basename "$f")..."
    if [ -f "$theirs" ]; then
	if diff -q "$theirs" "$f" > /dev/null 2>&1; then
	    echo "OK"
	    continue
	else
	    cp -f "$theirs" "$BACKUP_DIR"
	    cp -f "$f" "${HOME}"
	    echo "UPDATED (original backed up)"
	fi
    else
	echo "MISSING (system default restored)"
	cp -f "$f" "${HOME}"
    fi
done
