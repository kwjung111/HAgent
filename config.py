#SLAVE/MASTER
MODE="MASTER"
#Agent port
PORT="9000"
#Other Agent's address (IP:Port)
TARGET_NODE="10.0.20.48:9000"

#Systemctl units name
SERVICES=[]
#Systemctl timers name
TIMERS=[]
#Check Interval 
INTERVAL=5
#Maximum Failover / Failback try count. Do not set this to 0
RETRY_COUNT=3

#Telegram Token for Alarm
TG_TOKEN="8187547382:AAGchaydetQ22JSNWDqWaXUvlHRGfr6OorM"
#Telegram ChatID for Alarm
TG_CHATID="6443033704"
