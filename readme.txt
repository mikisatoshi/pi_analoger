/home/repo_loger/
- scheduler.sh
- loger.sh
- backup.sh
-
- [certification]
- [storage]
- [pi_loger]
--- access.py
--- loger.py
--- backup.py

____________________________________________________

crontab -e

*/2 * * * * cd repo_loger && ./loger.sh
30 1,13 * * * cd repo_loger && ./scheduler.sh
00 2 * * * cd repo_loger && ./backup.sh

crontab now runing

--- TIPS ---

git clone https://github.com/mikisatoshi/repo_loger.git
git clone https://github.com/mikisatoshi/pi_loger.git

cd pi_loger
git pull origin master
