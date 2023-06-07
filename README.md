# ECE 2T7 Discord server bot
## Description
This repository hosts the server-specific Discord bot designed for my UofT graduating class' Discord server. Developing this bot provided me with a practical outlet to apply my coding skills. Unlike solving abstract coding problems where I don't have to worry about specifics, I was forced to be more thorough in the implementation details to deploy a service that wasn't easily abused or broken. In the process of making it, I've learned many invaluable lessons. 
- First and foremost, I now feel comfortable navigating library documentation, as was learned through the use of `discord.py`, `beautifulSoup4`, and more. 
- I've expanded my knowledge on web scraping and webhooks by automating news channels that repeatedly pull information from different news sources on the internet.
- I've learned that I need to organize my code better for my next project. My idea to merely split up event functions and helper functions into two seperate files was insufficient to properly organize my code. This realization came to me when I needed to go back and fix my helper functions. If I could restart this project, one major change I would make would be to organize seperate features into classes (e.g. One class for all role menu creation, one class for all webhooks, where I would implement the "strategy/policy" design pattern to switch between different specific web scraping methods.)

## Features
These are the bot's main features:
- Reaction role assignment: With the help of the admin function $roleMenu, the bot will send out a message in the `#roles` channel that acts as a "Role Menu". The message outlines multiple server roles and their corresponding emoji. When users add an emoji reaction to the message, the bot assigns them the associated server role. Similarly, when the user removes their reaction, the role is revoked. This provides a seemless role self-management experience to the users.
