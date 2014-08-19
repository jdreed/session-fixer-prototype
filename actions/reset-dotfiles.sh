#!/bin/sh

CUSTOM_DOTFILES=".path .cshrc.mine .bashrc.mine .environment .bash_environment .startup.X .startup.tty"
PROTOTYPE=/usr/prototype_user

BACKUP_DIR="${HOME}/dotfiles-$(date +"%s")"
mkdir "$BACKUP_DIR"

for f in CUSTOM_DOTFILES; do
    if [ -f "${HOME}/$f" ]; then
	mv -vf "${HOME}/$f" "${BACKUP_DIR}/$f"
    fi
done

for f in $(ls $PROTOTYPE/.??*) abc; do
    cp -vf "$f" "${HOME}"
done
