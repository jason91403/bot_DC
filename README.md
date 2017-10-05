An AI for a Roguelike
================================================

Name: 		Hsiang-Yu Chiang
Student ID: 	201206886

October 2017

************************************************************

+ The program is an AI bot to play the Dungeon Crawl Stone Soup game. It is also provided on my github:
 https://github.com/jason91403/bot_DC

+ Required python model and the game:

 - 1. pyte
   Install information: 
   https://pyte.readthedocs.io/en/latest/

 - 2. Dungeon Crawl Stone Soup
   Install information: 
   https://crawl.develz.org/download.htm

+ Main file to run:

  - main.py
    Usage:
     python main.py
    Params:
     No param is required.

+ Activate the AI bot:
 
 When the screen is the playing screen (a map on the left side, the state information on the right side), press "o" key
 to activate a bot to consider the next action. Some information of bot thinking will be shown on the terminal screen 
 below. Then, press "p" key to activate a bot to follow the instructions from previous bot thinking.

+ Known bug:

 It may cause some error when some keys are pressed while the screen is not the playing screen (like menu screen), best way
 to do is to create a character and keep the select box on which character is going to play in the original DCSS game. Then,
 , close the original DCSS game and run main.py. Follow this way, it just need to press "Enter" to play while the screen is
 the menu screen.
 screen.
