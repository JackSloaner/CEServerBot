# ECE 2T7 Discord server bot
## Description
This repository hosts the server-specific Discord bot designed for my UofT graduating class' Discord server. Developing this bot provided me with a practical outlet to apply my coding skills. Unlike solving abstract coding problems, or private side projects where I don't have to worry about specifics, I was forced to be more thorough in the implementation details to deploy a service that wasn't easily abused or broken. In the process of making it, I've learned many invaluable lessons. 
- First and foremost, I now feel fully comfortable navigating library documentation, as was learned through the use of `discord.py`, `beautifulSoup4`, and more. 
- I've expanded my knowledge on web scraping and webhooks by automating news channels that repeatedly pull information from different news sources on the internet.
- I've been able to practice and refine my usage of git and gitHub, both in the context of a virtual coding environment, and in general. This includes practicing *Atomic Commits*, properly formatting commit messages, `git push`-ing and `git pull`-ing, and navigating back to previous commits to fix mistakes via `git reset {path}`.
- I've learned that I need to organize my code better for my next project. My idea to merely split up event functions and helper functions into two seperate files was insufficient to properly organize my code. This realization came to me when I needed to go back and fix my helper functions. If I could restart this project, one major change I would make would be to organize seperate features into classes (e.g. One class for all role menu creation, one class for all webhooks, where I would implement the "strategy/policy" design pattern to switch between different specific web scraping methods).

## Features
These are the bot's main features:
- Reaction role assignment: With the help of the admin function `$roleMenu`, the bot will send out a message in the `#roles` channel that acts as a "Role Menu". The message outlines multiple server roles and their corresponding emoji. When users add an emoji reaction to the message, the bot assigns them the associated server role. Similarly, when the user removes their reaction, the role is revoked. This provides a seemless role self-management experience to the users.
- News Channels: `#uoft-news`, and `#techmeme-news` are the two server news channels. The former provides the latest news directly from the University of Toronto's website, while the latter provides the latest news in tech, courtesy of techmeme.com. The bot updates both channels every 5 minutes, scraping the respective news pages and transferring the raw HTML data to a nicely formatted embed to send to the webhook.
- Admin commands: `$blackList`, `$whiteList`, `$clearChannel`, and `$roleMenu` are all the bot's admin commands. `$blackList` blacklists users from `/suggest`, while `$whiteList` whitelists users from it. `$clearChannel` clears a given channel's messages. `$roleMenu` creates a reaction role menu as previously stated.
- Slash commands: `/introduce` and `/moderate`, and `/suggest` are the bot's slash commands. The first lets new members introduce themselves by creating a custom embed that is sent to a intoductions-only channel. The second sends the user an ephemeral message to a moderation application link. The third sends mods server suggestion to a private channel; there is a cooldown on this command. Rather than making commands with the `on_message()` event, slash commands are integrated commands within discord.py, with enhanced usability features. These commands are intended for all users.

## How to use
This is a server-specific bot, so it only works on the ECE 2T7 server. If you would like to preview the bot, send me a message via linkedin at https://www.linkedin.com/in/jack-sloan-127a95229 to receive an invite link to the discord server.
