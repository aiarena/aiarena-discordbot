# SC2 AI Discord Bot
Discord Bot for the SC2 AI Discord Server.

#### Motivation

This bot is to provide a tool for SC2AI Bot programmers to be able to quickly gather bot info and replays of a bot, instead of having to manually traverse the aiarena.net website.
#### Commands

- !bot <bot name> : Shows bot information
- !gg <bot_name> <num_days> optional: --loss --tag <tag_name> --limit <num_replays> : Creates and sends a replay pack of <bot_name>'s last <num_days> games as a DM. If "--loss" is specified, the replays will be only of games where the bot lossed.  If "--limit" is specified, then only <limit> wnumber of replays, if --tag is included, then only replays with tag <tag_name> will be included will be included
- !top10 : Shows the current top 10 bots on the ladder
- !top16: Shows the current top 16 bots on the ladder

- !gs : Shows the getting started guide
