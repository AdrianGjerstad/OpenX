#!/usr/bin/bash

function openx() {
  # Python3 Installed Check
  command -v python3 >/dev/null 2>&1 || { echo >&2 "Python3 is required to run OpenX. Aborting."; return 126; }

  # OpenX Path Check
  if [[ $OPENXPATH == "" ]]; then
    echo >&2 "Environment variable \$OPENXPATH is not set. Aborting."
    return 125
  fi

  # OpenX Path Trailing Slash Check
  if [[ ! $OPENXPATH == */ ]]; then
    echo >&2 "Environment variable \$OPENXPATH does not end with '/' character. Aborting."
    return 124
  fi

  # OpenX Path Existance Check
  if [[ ! -d $OPENXPATH ]]; then
    echo >&2 "Environment variable \$OPENXPATH does not exist. Aborting."
    return 123
  fi
  
  python3 ${OPENXPATH}openx.py $@

  return $?
}
