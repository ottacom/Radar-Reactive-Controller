# Radar-Reactive-Controller For Observium (and general purpose)

What's that?
Radar Reactive controller is a phytonic application to keep safe your business
Basically you can control wathever you want using scripts and/or sql query on database
but I made RRC in order to make some check on my customers, without having false positive/negative
The RRC's aim is to have ever the situation under control.



#Quick guide (For impatient, pleas Jump in example guide below)

What you need:
-Mysql instance (local or remote, of course you can use the observium istance)
-The controller.json file - The configuration file of the system
-The database.json file - The db instance file

#The controller.json file

Description of controller.json syntax example


"controllerset":

                [{
                "controllername_id": controllername (PrimaryKey uinque)
                "probeset":[{
                          "probename_id": probename (PrimaryKey uinque)
                          "sql": sql query
                          "sqlengine" : the sql engine in use
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
                }


Description of database.json syntax example (Only mysql is supported at the moment)

Please remind the first database configured will be used for check condition  
      "databases":
                        [{
                          "database_id":"conditiondb",
                          "dbengine":"mysql",
                          "host":"192.168.122.144",
                          "database": "observium",
                          "username":"root",
                          "password":"password"
                        },{
                          "database_id":"mysql1",
                          "dbengine":"mysql",
                          "host":"192.168.122.144",
                          "database": "observium",
                          "username":"root",
                          "password":"password"
                        },]


}


#Example guide and use


consider to use Observium

Edit database.json:


{
        "controllerset":

                        [{
                        "controllername_id":"Saturation provider1",
                        "probeset":[{
                                  "probename_id":"mplsin",
                                  "sql": "select ((ifInOctets_rate * 8)/1000000) from `ports-state` where port_id='46220';",
                                  "sqlengine" : "mysql1",
                                  "probefile": ""
                                  },{
                                  "probename_id":"mplsout",
                                  "sql": "select ((ifOutOctets_rate * 8)/1000000) from `ports-state` where port_id='46220';",
                                  "sqlengine" : "mysql1",
                                  "probefile": ""
                                  }],
                          "condition":"select (mplsin >= 9) or (mplsout >= 9)",
                          "expected_value":"False",
                          "ifsatisfied_action": "",
                          "ifnotsatisfied_action": "/opt/Radar-Reactive-Controller/scripts/smssend.sh,00,999999999,Saturazione MPLS_ROMA_MALTA",
			  "repeat_ifsatisfied_action":"once",
                          "repeat_ifnotsatisfied_action":"once",
                          "rearm_after": 0,
                          "rearm_action": ""
                        },{
                        "controllername_id":"Saturation provider2",
                        "probeset":[{
                                  "probename_id":"coltin",
                                  "sql": "select ((ifInOctets_rate * 8)/1000000) from `ports-state` where port_id='46235';",
                                  "sqlengine" : "mysql1",
                                  "probefile": ""
                                  },{
                                  "probename_id":"coltout",
                                  "sql": "select ((ifOutOctets_rate * 8)/1000000) from `ports-state` where port_id='46235';",
                                  "sqlengine" : "mysql1",
                                  "probefile": ""
                                  }],
                          "condition":"select (coltin >= 18) or (coltout >= 18)",
                          "expected_value":"False",
                          "ifsatisfied_action": "",
                          "ifnotsatisfied_action": "/opt/Radar-Reactive-Controller/scripts/smssend.sh,00,999999999,Saturazione_COLT_ROMA",
			  "repeat_ifsatisfied_action":"once",
                          "repeat_ifnotsatisfied_action":"once",
                          "rearm_after": 0,
                          "rearm_action": ""
                        },{
			"controllername_id":"Saturation provider3",
                        "probeset":[{
                                  "probename_id":"fastwebin",
                                  "sql": "select ((ifInOctets_rate * 8)/1000000) from `ports-state` where port_id='46212';",
                                  "sqlengine" : "mysql1",
                                  "probefile": ""
                                  },{
                                  "probename_id":"fastwebout",
                                  "sql": "select ((ifOutOctets_rate * 8)/1000000) from `ports-state` where port_id='46212';",
                                  "sqlengine" : "mysql1",
                                  "probefile": ""
                                  }],
                          "condition":"select (fastwebin >= 18) or (fastwebout >= 18)",
                          "expected_value":"False",
                          "ifsatisfied_action": "",
                          "ifnotsatisfied_action": "/opt/Radar-Reactive-Controller/scripts/smssend.sh,00,999999999,Saturazione_FASTWEB_ROMA",
			  "repeat_ifsatisfied_action":"once",
                          "repeat_ifnotsatisfied_action":"once",
                          "rearm_after": 0,
                          "rearm_action": ""
                        },{
		        "controllername_id":"Saturation MPLS network",
                        "probeset":[{
                                  "probename_id":"Goin",
                                  "sql": "select ((ifInOctets_rate * 8)/1000000) from `ports-state` where port_id='2141';",
                                  "sqlengine" : "mysql1",
                                  "probefile": ""
                                  },{
                                  "probename_id":"Goout",
                                  "sql": "select ((ifOutOctets_rate * 8)/1000000) from `ports-state` where port_id='2141';",
                                  "sqlengine" : "mysql1",
                                  "probefile": ""
                                  }],
                          "condition":"select (Goin >= 12) or (Goout >= 12)",
                          "expected_value":"False",
                          "ifsatisfied_action": "",
                          "ifnotsatisfied_action": "/opt/Radar-Reactive-Controller/scripts/smssend.sh,00,999999999,Saturazione_GO-MALTA",
			  "repeat_ifsatisfied_action":"once",
                          "repeat_ifnotsatisfied_action":"once",
                          "rearm_after": 0,
                          "rearm_action": ""
                        },{
                        "controllername_id":"Video streaming",
                        "probeset":[{
                                  "probename_id":"Gostreaming",
                                  "sql": "select ((ifinOctets_rate * 8)/1000000) from `ports-state` where port_id='4660';",
                                  "sqlengine" : "mysql1",
                                  "probefile": ""
                                  }],
                          "condition":"select (Gostreaming <= 2)",
                          "expected_value":"False",
                          "ifsatisfied_action": "",
                          "ifnotsatisfied_action": "/opt/Radar-Reactive-Controller/scripts/reazione_down_streaming.sh",
			  "repeat_ifsatisfied_action":"once",
                          "repeat_ifnotsatisfied_action":"once",
                          "rearm_after": 1,
                          "rearm_action": "/opt/Radar-Reactive-Controller/scripts/smssend.sh,00,999999999,O_Streaming_ritornato_operativo_O"
                        },{
                        "controllername_id":"Check VPN",
                        "probeset":[{
                                  "probename_id":"chkping",
                                  "sql": "",
                                  "sqlengine" : "",
                                  "probefile": "/opt/Radar-Reactive-Controller/scripts/pingchk.sh,10.116.192.1"
                                  }],
                          "condition":"select IF(((WEEKDAY(CURDATE())) < 6) AND (chkping = 0),'True','False');",
                          "expected_value":"True",
                          "ifsatisfied_action": "",
                          "ifnotsatisfied_action": "/opt/Radar-Reactive-Controller/scripts/reazione_down_tgz.sh",
                          "repeat_ifsatisfied_action":"once",
                          "repeat_ifnotsatisfied_action":"once",
                          "rearm_after": 1,
                          "rearm_action": "/opt/Radar-Reactive-Controller/scripts/smssend.sh,00,999999999,VPN TGZ tornata up"
                        }
			]

}



Edit database.json

database.json
{
      "databases":
                        [{
                          "database_id":"mysql1",
                          "dbengine":"mysql",
                          "host":"127.0.0.1",
                          "database": "observium",
                          "username":"root",
                          "password":"superpassword"
                        }]


}



#Check file syntax (Mandatory)

/opt/Radar-Reactive-Controller/rrc.py -m simulation  -d /opt/Radar-Reactive-Controller/database.json -c /opt/Radar-Reactive-Controller/controller.json


#Start your RRC
/opt/Radar-Reactive-Controller/rrc.py -m production -d /opt/Radar-Reactive-Controller/database.json -c /opt/Radar-Reactive-Controller/controller.json

#Add your RRC to crontab (for me every 2 minutes is good)
*/2 * * * *  /opt/Radar-Reactive-Controller/rrc.py -m production -d /opt/Radar-Reactive-Controller/database.json -c /opt/Radar-Reactive-Controller/controller.json
