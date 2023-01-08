<div align="center"> 
<h1><b> Telegram Bot for Generating Mediainfo and Screenshots from file or links.</b></h1>
</div>

- can generate Mediainfo from telegram files, gdrive files and direct download links.
- can generate random frames Screenshots from Telegram video files, gdrive and download links.
- upload screenshots to <a href="https://slow.pics/">slow.pics</a> website.

( Base repository : https://github.com/sanjit-sinha/TelegramBot-Boilerplate )

----

<div align="center"> 
<h2><b> Bot Commands </b></h2>
</div>

- `/m or /mediainfo  ` - Type link after command or reply to telegram file to generate Mediainfo.
- `/ss or /screenshot` - Type link after command or reply to telegram video file to generate screenshots.
- `/paste` - paste your text in katb.in
- few more commands like `/start` `/help` `/py` `/exec` `/update` etc

Add number of frames you want to generate after `|` flag. Example: `/ss [video file link] | 10` (Default 5 and Max 15)

Note: Generating screenshots from some drive link and direct download link is not stable yet.

----
<div align="center"> 
<h1><b>Screenshots</b></h1>
</div>

| ![](https://te.legra.ph/file/9a29440d0a8544408f28f.jpg) | ![](https://te.legra.ph/file/3d81bf56ab50635fdcb45.jpg)|
|--------------------------------------------------------|--------------------------------------------------------|
| ![](https://te.legra.ph/file/54454be994d4311bcf20e.jpg)| ![](https://te.legra.ph/file/cdc73890b2693686b3d2b.jpg) |

------

 
<div align="center"> 
<h2><b>Bot Deployment and Usage</b></h2>
<p><b>( VPS or Local hosting )</b></p>
</div>

Upgrading, Updating and setting up required packages in Server.

```
sudo apt-get update && sudo apt-get upgrade -y
sudo apt install python3-pip -y
sudo pip3 install -U pip
sudo apt-get install -y mediainfo
sudo apt-get install ffmpeg
```

Dependencies:
- Python 3.9 or greater
- FFmpeg
- mediainfo

Cloning Github Respository and Starting the Bot in Server.
 
```
git clone https://github.com/sanjit-sinha/Tg-MediaInfoBot && cd Tg-MediaInfoBot
pip3 install -U -r requirements.txt
```

Now edit the config vars by typing `nano config.env` and save it by pressing <kbd>ctrl</kbd>+<kbd>o</kbd> and <kbd>ctrl</kbd>+<kbd>x</kbd>.
<br>
<br>

<details>
<summary><strong> Setting up config variables files (config.env), credentials.json and token.json</strong></summary>
<br>
<ul>
 <li>Get your API_ID and API_HASH from <a href="https://my.telegram.org/auth">Telegram.org</a>, BOT_TOKEN from <a href="https://t.me/botfather">Botfather.</a> You can get user ids for bot owner from <a href="https://t.me/MissRose_bot">MissRoseBot</a> by just using /info command and copying ID value from result. </li>
 <li>Click <a href="https://github.com/sanjit-sinha/Tg-MediaInfoBot#getting-google-oauth-api-credentialjson-file-and-tokenjson">here</a> for getting Google OAuth API credential.json file and token.json
 </ul>
</details>

now you can start the bot by simply typing `bash start` or `python3 -m TelegramBot`

The bot will stop working once you logout from the server. You can run the bot 24*7 in the server by using screen or tmux.
```
sudo apt install tmux -y
tmux && bash start
```
  
Now the bot will run 24*7 even if you logout from the server. [Click here to know about tmux and screen advance commands.](https://grizzled-cobalt-5da.notion.site/Terminal-Multiplexers-to-run-your-command-24-7-3b2f3fd15922411dbb9a46986bd0e116)

------
 
<div align="center"> 
<h2><b>Getting Google OAuth API credential.json file and token.json</b></h2>
</div>

**NOTES**
- Old authentication changed, now we can't use bot or replit to generate token.json. You need OS with a local browser. For example `Termux`.
- You can ONLY open the generated link from `token_generator.py` in local browser.
- ( <a href="https://github.com/anasty17/mirror-leech-telegram-bot#3-getting-google-oauth-api-credential-file-and-tokenpickle">source</a> )

1. Visit the [Google Cloud Console](https://console.developers.google.com/apis/credentials)
2. Go to the OAuth Consent tab, fill it, and save.
3. Go to the Credentials tab and click Create Credentials -> OAuth Client ID
4. Choose Desktop and Create.
5. Publish your OAuth consent screen App to prevent **token.json** from expire
6. Use the download button to download your credentials.
7. Rename that file into credentials.json and move that file to the root of repo.
8. Visit [Google API page](https://console.developers.google.com/apis/library)
9. Search for Google Drive Api and enable it in Google Cloud Console 
10. Finally, run the script from inside of repository 

```
pip3 install google-api-python-client google-auth-httplib2 google-auth-oauthlib
python3 token_generator.py
```


-----
