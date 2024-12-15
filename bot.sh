#!/bin/bash

# Prepend secrets from SECRETS folder to config.py
if [ -d "$SECRETS" ]; then
  mv config.py config.old

  for FILE in $SECRETS/*; do
    echo $(basename $FILE) = $(<$FILE) >> config.py;
  done

  cat config.old >> config.py
fi

/usr/local/bin/python bot.py
