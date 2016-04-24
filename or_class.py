#OBJECT definers
#Defining controller
class Controller(object):
    #defaultvalue
    controllername_id = ""
    logging = ""
    condition= ""
    expected_value = ""
    ifsatisfied_action_action = "nop"
    on_ifnotsatisfied_action_action = "nop"
    rearm_after = 0
    rearm_action = "nop"



    def __init__(self,controllername_id,logging, condition, expected_value,ifsatisfied_action,ifnotsatisfied_action,repeat_ifsatisfied_action,repeat_ifnotsatisfied_action,rearm_after,rearm_action,totalprobes,index,lastresult):


        self.controllername_id = controllername_id
        self.logging = logging
        self.condition = condition
        self.expected_value = expected_value
        self.ifsatisfied_action = ifsatisfied_action
        self.ifnotsatisfied_action = ifnotsatisfied_action
        self.repeat_ifsatisfied_action = repeat_ifsatisfied_action
        self.repeat_ifnotsatisfied_action = repeat_ifnotsatisfied_action
        self.rearm_after = rearm_after
        self.rearm_action = rearm_action
        self.totalprobes = totalprobes
        self.index = index
        self.lastresult = lastresult



class Probe(object):

        probename_id = ""
        sql = ""



        def __init__(self,probename_id,sql,sqlengine,probefile,controllerindex,probeindex,abs_probeindex,lastresult):
            self.probename_id = probename_id
            self.sql = sql
            self.sqlengine = sqlengine
            self.probefile = probefile
            self.controllerindex = controllerindex
            self.probeindex = probeindex
            self.abs_probeindex = abs_probeindex
            self.lastresult = lastresult




class Dbengine(object):


        def __init__(self,database_id,dbengine,host,database,username,password,dbindex):
            self.database_id = database_id
            self.dbengine = dbengine
            self.host = host
            self.database = database
            self.username = username
            self.password = password
            self.dbindex = dbindex
