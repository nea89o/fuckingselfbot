#!/usr/bin/env bash
root=$(dirname $0)
cd ${root}
${root}/venv/bin/python ${root}/main.py "$@" &>$HOME/logs/discordbot



