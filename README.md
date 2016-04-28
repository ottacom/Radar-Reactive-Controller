# Radar-Reactive-Controller For Observium (and general purpose)
...In ohter words.. A swiss knife to keep the infrastructure under control

What's that?
Radar Reactive controller is a phytonic application to keep safe your business.
Basically you can control whatever you want using scripts and/or sql query check on databases
I made RRC in order to have some checks on my customers, without false positive/negative
The RRC's aim is to have always the situation under control.



#Quick guide (For impatient, please take a look inside the file)

What you need:
.Mysql instance (local or remote, of course you can use the observium instance)
.The controller.json file - The configuration file of the system
.The database.json file - The db instance file

#The controller.json file

Description of controller.json syntax example


                "controllername_id": controllername (PrimaryKey uinque)
                "probeset":[{
                          "probename_id": probename (PrimaryKey uinque)
                          "sql": sql query
                          "sqlengine" : the sql engine in use defined in database.json
                          "probefile": the script to star (if you use this one you cant use sql)
                          }
                  "condition": sql condition
                  "expected_value": value out from sql condition
                  "ifsatisfied_action": script (syntax is ex: /tmp/switc.sh,par1,par2,etc)
                  "ifnotsatisfied_action": script (syntax is ex: /tmp/switc.sh,par1,par2,etc)
                  "repeat_ifsatisfied_action": once=repeat one time,ever=repeat everytime
                  "repeat_ifnotsatisfied_action":once=repeat one time,ever=repeat everytime
                  "rearm_after": 0= no rearm, > 1 = times satisfied
                  "rearm_action": script (syntax is ex: /tmp/switc.sh,par1,par2,etc)

Important:
The first DB configured in database.json will be used for check conditions


#Check file syntax (Mandatory)

/rrc/rrc.py -m simulation  -d /rrc/database.json -c /rrc/controller.json


#Start your RRC
/rrc/rrc.py -m production -d /rrc/database.json -c /rrc/controller.json

#Add your RRC to crontab
(for me every 2 minutes is pretty good)

*/2 * * * *  /rrc/rrc.py -m production -d /rrc/database.json -c /rrc/controller.json
