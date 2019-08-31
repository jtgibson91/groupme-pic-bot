# groupme-pic-bot

A GroupMe bot that filters through all the of posted pictures in the group and posts a random one from that day in previous years. The group must obviously be at least a year old for that to work. Once found, the bot posts the picture, the group member who posted the image, and the original date it was posted.

You must register a development account with GroupMe to get a token id. Follow the instructions here to get one: https://dev.groupme.com/tutorials/oauth

You must then create your bot to get your bot id. Follow step 2 to create a bot using Groupme's API: https://dev.groupme.com/tutorials/bots

Once you have the access token, bot id, and group id, enter those into the three variables at the top of app.py and run the bot from a terminal like so:

`< $ python3 ./app.py >`

That will make the bot work once (post one picture). If you want to have the bot run automatically, every day for example, you need to put it on a timer on a machine that is always on. For example, put it on a Digitalocean droplet on a cron timer. 
