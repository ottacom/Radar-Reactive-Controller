#OBJECT definers
#Defining controller
class Controller(object):
    #defaultvalue
    controllername_id = ""
    logging = ""
    condition= ""
    expected_value = ""
    action_true = "nop"
    action_false = "nop"
    rollback_after = 1
    rollback_action = "nop"


#Pay attention to the order
    def __init__(self,controllername_id,logging, condition, expected_value,action_true,action_false,rollback_after,rollback_action,totalprobes,index):


        self.controllername_id = controllername_id
        self.logging = logging
        self.condition = condition
        self.expected_value = expected_value
        self.action_true = action_true
        self.action_false = action_false
        self.rollback_after = rollback_after
        self.rollback_action = rollback_action
        self.totalprobes = totalprobes
        self.index = index





#Defining probes
class Probe(object):

        probename_id = ""
        sql = ""

#Pay attention to the order


        def __init__(self,probename_id,sql,sqlengine,probefile,controllerindex,probeindex):
            self.probename_id = probename_id
            self.sql = sql
            self.sqlengine = sqlengine
            self.probefile = probefile
            self.controllerindex = controllerindex
            self.probeindex = probeindex


class Probe(object):

        probename_id = ""
        sql = ""

#Pay attention to the order


        def __init__(self,probename_id,sql,sqlengine,probefile,controllerindex,probeindex):
            self.probename_id = probename_id
            self.sql = sql
            self.sqlengine = sqlengine
            self.probefile = probefile
            self.controllerindex = controllerindex
            self.probeindex = probeindex
