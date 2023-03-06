<div align="center">
<img src="https://graph.org/file/d305c3259ca8d5324ee61.png" align="center" style="width: 30%" />


<h2 align="center">Telegram MediaInfoBot</h2>
</div>

<p align="center">
<img src="https://img.shields.io/github/stars/sanjit-sinha/Tg-MediaInfoBot">
<img src="https://img.shields.io/github/forks/sanjit-sinha/Tg-MediaInfoBot">
<img src="https://img.shields.io/github/repo-size/sanjit-sinha/Tg-MediaInfoBot">
<img src="https://img.shields.io/badge/License-MIT-green.svg">
<img src="https://www.repostatus.org/badges/latest/active.svg">
</p>

----

<b> This Telegram Bot can perform various tasks with media files, such as :- </b>

- Generating Mediainfo from Google Drive links, direct download links, and Telegram files, and displaying the information on a custom-designed website.
- Creating screenshots from Google Drive links, direct download links, and Telegram files, and posting them on slow.pics
- Generating custom-duration video samples from video files.
- Creating spectrograms of Telegram audio files and displaying them as images.
- pasting the text in the katb.in website.


Note: This Bot is made on top of this repository -> https://github.com/sanjit-sinha/TelegramBot-Boilerplate 

____

<h2 align="center"> Screenshots </h2> 

![](https://graph.org/file/3f9346b6c369f4222cadb.jpg) |
|----------------------------------------------------------|

![](https://graph.org//file/499ec614796ce14e4cd3c.png)
|----------------------------------------------------------|

| ![](https://graph.org/file/8bcc663207262b45b0e8a.jpg) | ![](https://graph.org/file/9a0d26cb23963d96d28d6.jpg)|
|--------------------------------------------------------|--------------------------------------------------------|

<p align="center"><b>Exmaple Links<br>( <a href="https://mediainfo.deta.dev/ohROIsS5">Mediainfo</a> • <a href="https://slow.pics/c/PiZz4LuS">Screenshot</a> • <a href="https://graph.org//file/499ec614796ce14e4cd3c.png">Audiograph</a> )</b></p>

------

<h2 align="center"> Bot Commands and Usage</h2>

- `/m or /mediainfo  ` - Type link after command or Reply to telegram file to generate Mediainfo.
- `/ss or /screenshot` - Type link after command or Reply to telegram video file to generate screenshots.
- `/sample`  or `/trim` - Type link after command or Reply to telegram video file to generate sample video.
- `/spek` or `/sox`  - Reply to Telegram file to generate audio spectogram.
- `/paste` - paste your text in katb.in website. 

 <b> Additional Flags for screenshot and mediainfo command :- </b>

**--count=10** *[ Number of screenshots. Default 10, Max 20 ]*, 
**--fps=10**  *[ Difference between two consecutive screenshots in seconds. Default 5, Max 15 ]*.
**--time=01:20:10**  *[ Time from where the screenshots should be taken in HH:MM:SS format ]*,
**--hdr**  *[ For HDR Videos.]*

**--r** *[ For raw Mediainfo in document format. ]*

 (Few more commands `/start` `/help` `/ping` `/update` `/logs`)
 
 _____
 
<h2 align="center"> Bot Deployment </h2>
 
<b> Install and update Dependencies 

```sh
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y python3-pip
sudo pip3 install -U pip
sudo apt-get install -y --no-install-recommends mediainfo ffmpeg
sudo apt-get install libsox-fmt-mp3
sudo apt-get install sox 
```
clone the repository and install the requirements

```sh
git clone https://github.com/sanjit-sinha/Tg-MediaInfoBot
cd Tg-MediaInfoBot
pip3 install -U -r requirements.txt
```

Now edit the config vars by typing `nano config.env` and save it by pressing <kbd>ctrl</kbd>+<kbd>o</kbd> and <kbd>ctrl</kbd>+<kbd>x</kbd>.
<br>

<details>
<summary><strong>Getting Google OAuth API credential.json file and token.json (important)</strong></summary>
<br>
<ul>
<li>

**NOTES**
- You need credentials.json and token.json in root folder for bot to work.
- Old authentication changed, now we can't use bot or replit to generate token.json. You need OS with a local browser. For example `Termux`.
- You can ONLY open the generated link from `token_generator.py` in local browser.

**STEPS**
- Visit the [Google Cloud Console](https://console.developers.google.com/apis/credentials)
- Go to the OAuth Consent tab, fill it, and save.
- Go to the Credentials tab and click Create Credentials -> OAuth Client ID
- Choose Desktop and Create.
- Publish your OAuth consent screen App to prevent **token.json** from expire
- Use the download button to download your credentials.
- Rename that file into credentials.json and move that file to the root of repo.
- Visit [Google API page](https://console.developers.google.com/apis/library)
- Search for Google Drive Api and enable it in Google Cloud Console 
- Finally, run the script from inside of repository 
<br>
 
```sh
pip3 install google-api-python-client google-auth-httplib2 google-auth-oauthlib
python3 token_generator.py
```
 </ul>
</details>

Now you can start the bot by simply typing `bash start` or `python3 -m TelegramBot`

> **The bot will stop working once you logout from the server. You can run the bot 24*7 in the server by using tmux.**
> ```sh
> sudo apt install tmux -y
> tmux
> bash start
> ```

Now the bot will run 24*7 even if you logout from the server. [Click here to know about tmux and screen advance commands.](https://grizzled-cobalt-5da.notion.site/Terminal-Multiplexers-to-run-your-command-24-7-3b2f3fd15922411dbb9a46986bd0e116)
<br >

> **Note** You can also Deploy Bot using Docker
> ```sh
> docker build . -t mediainfobot 
> docker run mediainfobot
>```

_____

  
<h2 align="center">Copyright and License</h1>
<br>
<img src="https://telegra.ph/file/b5850b957f081cfe5f0a6.png" align="right" width="110">

* copyright (C) 2023 by [Sanjit sinha](https://github.com/sanjit-sinha)
* Licensed under the terms of the [The MIT License](https://github.com/sanjit-sinha/Tg-MediaInfoBot/blob/main/LICENSE)


-------

  

