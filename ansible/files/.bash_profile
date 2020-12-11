#
# Custom comand prompt
#
# colors & styles
	BOLD=$(tput bold)
	RESET=$(tput sgr0)
	ORANGE=$(tput setaf 166)
	GREEN=$(tput setaf 71)
	YELLOW=$(tput setaf 228)
	BLUE=$(tput setaf 4)
	CYAN=$(tput setaf 6)
# prompt
	PS1="\[${BOLD}\]\n"
	PS1+="\[${ORANGE}${BOLD}\]\u ";
	PS1+="\[${RESET}\]on \[${YELLOW}${BOLD}\]\h ";
	PS1+="\[${RESET}\]using \[${CYAN}${BOLD}\]\s ";
	PS1+="\[${RESET}\]in \[${GREEN}${BOLD}\]\W ";
	PS1+="\[${RESET}\]\n\$ \[${RESET}\]";
export PS1

alias rss="systemctl restart gameserver; systemctl status gameserver"
alias tl="tail -f ~/src/server/log/server.log"

# show banner and tail log @ login
cat .banner
tl
