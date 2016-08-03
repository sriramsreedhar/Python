#!/usr/bin/python

'''
The purpose of this script is to provide an easy-to-use interface for tracking various ops tasks and submitting them as work records to JIRA.

Documentation: https://confluence.sco.cisco.com/pages/viewpage.action?pageId=37093788 Mike R

'''
VERSION = "1.4"
LOGLEVEL = "WARNING"

import cmd
import datetime
import os
import pickle
import logging
import requests
import getpass
import signal
from re import search

logging.basicConfig(level=LOGLEVEL)   # Adjust this level for more verbose output

class Timey(cmd.Cmd):
    intro = 'Hi! I\'m Timey McTimeface. Type help or ? to list commands.\nVersion: '+VERSION
    prompt = '(timey) '

    currentTask = None        # The name of the current task being tracked
    currentDuration = None    # Duration of a currently tracked task as a string, only updated by do_current
    lastStart = None          # A datetime object representing the last time the task was started
    data = {}                 # A dictionary of tracked tasks and their durations
    aliases = {}              # A dictionary of task name aliases that map to Jira story IDs
    username = None           # User's provided Jira username
    password = None           # User's provided Jira password

    DATAFILE = 'timey_data.p'                # Data file to store task durations
    ALIASFILE = 'timey_alias.p'              # Data file to store task name aliases
    JIRA_URL = 'https://metacloud.jira.com'  # URL for posting to Jira

    def alias_start(self, arg):
        'Start tracking time for a given task. Examples:\n\tbegin CISOPS-001\n\tbegin email'
        if not arg:
            print "A task name must be provided. Examples:\n\tbegin CISOPS-001\n\tbegin email"
        else:
            now = datetime.datetime.today()
            humanTime = now.strftime('%H:%M:%S')
            # If a task is already being actively tracked
            if self.currentTask:
                # If the user tried to start the same task twice, just tell them
                if self.currentTask == arg:
                    diff = str(now - self.lastStart).split('.')[0]
                    print "\""+arg+"\" already started! Current duration: "+diff.zfill(8)
                    return 1
                # Stop the previously tracked task
                self.alias_stop(self.currentTask)
            # Start tracking the new task
            self.currentTask = arg
            self.lastStart = now
            print "STARTED "+str(arg)+" at "+humanTime
        return 0

    def alias_stop(self, arg):
        'Stop tracking time for a given task. Examples:\n\tbegin CISOPS-001\n\tbegin email'
        if not arg and not self.currentTask:
            print "A task name must be provided. Examples:\n\tbegin CISOPS-001\n\tbegin email"
        else:
            # If the user didn't specify a task name and the currently tracked task
            #  is called "exit", we must be getting ready to quit so there's no need to do anything
            if not arg and self.currentTask == "exit":
                return
            # Otherwise, stop the currently running task (or whatever the user specified)
            else:
                arg = self.currentTask
            now = datetime.datetime.today()
            humanTime = now.strftime('%H:%M:%S')
            diff = str(now - self.lastStart).split('.')[0]
            self.update_data(arg, self.lastStart, diff.zfill(8))
            print "STOPPED "+str(arg)+" at "+humanTime+" (duration: "+diff.zfill(8)+")"
            self.currentTask = None
            self.lastStart = None

    def alias_exit(self, arg):
        'Stop the currently tracked task and exit'
        # If no task is running, set the current task to "exit", 
        #  which is a signal for the stop command that nothing needs to be done
        if not self.currentTask:
            self.currentTask = "exit"
        # Try to stop the currently tracked task before quitting
        self.alias_stop("")
        # Clear the cached credentials just to be extra safe
        self.username = None
        self.password = None
        exit()

    def save_data(self, file=DATAFILE):
        # Write the current data/alias dictionaries to files via pickle
        f = open(file,'w')
        if file == self.DATAFILE:
            pickle.dump(self.data,f)
        else:
            pickle.dump(self.aliases,f)
        f.close()

    def load_data(self, file=None):
        # Default should assume we're loading the data file
        if file is None:
            file = self.DATAFILE
        # Read the current data/alias dictionaries from files via pickle
        try:
            logging.debug('Loading from file: '+str(file))
            if file == self.DATAFILE:
                if os.path.exists(file):
                    f = open(file, 'rbU')
                    try:
                        self.data = pickle.load(f)
                    # Create an empty data set if the file is empty
                    except EOFError:
                        self.data = {}
                    logging.debug(self.data)
                    f.close()
                else:
                    open(file, 'wb').close()
                    self.data = {}
                    logging.debug("Creating empty file "+file+". Creating empty data set")
            else:
                if os.path.exists(file):
                    f = open(file, 'rbU')
                    try:
                        self.aliases = pickle.load(f)
                    # Create an empty data set if the file is empty
                    except EOFError:
                        self.aliases = {}
                    logging.debug(self.aliases)
                    f.close()
                else:
                    open(file, 'wb').close()
                    self.aliases = {}
        except IOError:
            logging.debug("IOError for "+file+". Closing program")
            self.do_exit()

    def update_data(self, task, start, duration):
        logging.debug("Updating data for task: "+task+", start: "+str(start)+", duration: "+str(duration))
        # Refresh data
        self.load_data()

        logging.debug("Starting data: "+str(self.data))
        # If the task was already tracked previously,
        #  update the duration with a total duration for all iterations
        if self.data.has_key(task):
            logging.debug("Task "+task+" already exists in data")
            oldTimes = self.data[task]['duration'].split(':')
            logging.debug("Old times: "+str(oldTimes))
            oldDuration = datetime.timedelta(hours=int(oldTimes[0]),minutes=int(oldTimes[1]),seconds=int(oldTimes[2]))
            newTimes = duration.split(':')
            logging.debug("New times: "+str(newTimes))
            newDuration = datetime.timedelta(hours=int(newTimes[0]),minutes=int(newTimes[1]),seconds=int(newTimes[2]))
            logging.debug("New duration: "+str(newDuration))
            totalDuration = str(oldDuration+newDuration)
            self.data[task]['duration'] = totalDuration
        # Otherwise, just create the new data entry for the task
        else:
            self.data[task] = {'start': start, 'duration': duration}
        logging.debug("Ending data: "+str(self.data))
        # Write the updated data to a file
        self.save_data()

    def do_current(self, arg):
        'Print the currently tracked task and its duration'
        if not self.currentTask:
            print "No task is currently being tracked!"
        else:
            now = datetime.datetime.today()
            humanTime = now.strftime('%H:%M:%S')
            diff = str(now - self.lastStart).split('.')[0]
            self.currentDuration = diff.zfill(8)
            print "Current task: "+self.currentTask+", Current duration: "+diff.zfill(8)

    def do_report(self, arg):
        'Print a report of tracked tasks and their durations'
        self.load_data()
        logging.debug(self.data)
        totalHours = 0
        totalMins = 0
        totalSecs = 0
        for task in self.data:
            # If we're reporting the currently running task, give a total duration
            if self.currentTask == task:
                oldTimes = self.data[task]['duration'].split(':')
                logging.debug("Old times: "+str(oldTimes))
                oldDuration = datetime.timedelta(hours=int(oldTimes[0]),minutes=int(oldTimes[1]),seconds=int(oldTimes[2]))
                now = datetime.datetime.today()
                diff = str(now - self.lastStart).split('.')[0]
                newTimes = diff.split(':')
                logging.debug("New times: "+str(newTimes))
                newDuration = datetime.timedelta(hours=int(newTimes[0]),minutes=int(newTimes[1]),seconds=int(newTimes[2]))
                logging.debug("New duration: "+str(newDuration))
                totalDuration = str(oldDuration+newDuration)
                print "Task: "+task+", Duration: "+str(totalDuration).zfill(8)
                # Add the time to a cumulative total across all tasks
                words = totalDuration.split(':')
                totalHours += int(words[0])
                totalMins += int(words[1])
                totalSecs += int(words[2])
            else:
                print "Task: "+task+", Duration: "+self.data[task]['duration'].zfill(8)
                # Add the time to a cumulative total across all tasks
                words = self.data[task]['duration'].split(':')
                totalHours += int(words[0])
                totalMins += int(words[1])
                totalSecs += int(words[2])
        # Also print the currently tracked task individually
        if self.currentTask:
            self.do_current("")
            words = self.currentDuration.split(':')
            totalHours += int(words[0])
            totalMins += int(words[1])
            totalSecs += int(words[2])

        # Normalize the cumulative duration and print
        totalMins+=totalSecs/60
        totalSecs=totalSecs%60
        totalHours+=totalMins/60
        totalMins=totalMins%60
        print "-------------\nTotal Duration: "+str(totalHours).zfill(2)+":"+str(totalMins).zfill(2)+":"+str(totalSecs).zfill(2)

    def do_jira(self, arg):
        'Post tracked task durations to Jira'
        self.load_data()
        self.load_data(file=self.ALIASFILE)
        logging.debug(self.data)
        if self.username is None or self.password is None:
            self.username=raw_input("Username: ")
            self.password=getpass.getpass("Password: ")
        cleanup = []
        badCreds = False
        print ("Uploading..."),
        for task in self.data:
            print ("."),
            # If the task has an alias, use the Jira ID and comment from the alias config
            if self.aliases.has_key(task):
                jira = self.aliases[task]['jira']
                comment = self.aliases[task]['comment']
            else:
            # Otherwise, assume the task name is the Jira ID and we have no comment
                jira = task
                comment = ""

            # True if the jira ID matches the correct pattern
            if search("[A-Z]+\-[0-9]+",jira.upper()):
                # Stupid Jira API won't accept timeSpent even though it's in the documentation,
                #  so we need to report the time as timeSpentSeconds (total duration in seconds)
                times = self.data[task]['duration'].split(':')
                secSpent = int(times[2]) #seconds
                secSpent += int(times[1])*60 #minutes
                secSpent += int(times[0])*3600 #hours
                # Jira only accepts values of 60 seconds or greater, so round up
                if secSpent < 60:
                    secSpent = 60
                # JSON data to include with POST
                rdata = '{"comment": "'+comment+'", "timeSpentSeconds": '+str(secSpent)+'}'
                # POST to API
                r = requests.post(self.JIRA_URL+'/rest/api/2/issue/'+jira.upper()+'/worklog', auth=(self.username, self.password), data=rdata, headers={"Content-Type": "application/json"})
                # If Jira accepted the request (201), add the task to a cleanup queue so we don't report it again later
                if r.status_code == 201:
                    cleanup.append(task)
                # If Jira returns a 401 unauthorized, we need to re-prompt the user for credentials
                elif r.status_code == 401:
                    badCreds = True
                else:
                    logging.warning("Failed to post data for "+task)
            else:
                print 'Unable to post "'+task+'" because it is an ambiguous task ID. Please create an alias or post duration manually.'
        
        print ("done!")
        # Remove anything reported to Jira from the data/report
        for task in cleanup:
            del self.data[task]
        self.save_data()

        if badCreds:
            self.username = None
            self.password = None
            badCreds = False

        print "Jira post results: success="+str(len(cleanup))+", fail="+str(len(self.data))

    def do_list(self, arg):
        'Lists all tasks currently assigned to you'
        logging.debug(Timey.data)
        if self.username is None or self.password is None:
            self.username=raw_input("Username: ")
            self.password=getpass.getpass("Password: ")

        badCreds = False
        # GET request to Jira API
        r = requests.get(Timey.JIRA_URL+'/rest/api/2/search?jql=assignee='+self.username+' AND resolution IS EMPTY&fields=id,summary&maxResults=100', auth=(self.username, self.password))
        # If Jira accepted the request (200), list stories
        if r.status_code == 200:
            storiesJson = r.json()
            for issue in storiesJson.items()[0][1]:
                print issue["key"]+"    :       "+issue["fields"]["summary"]
        # If Jira returns a 401 unauthorized, we need to re-prompt the user for credentials
        elif r.status_code == 401:
            badCreds = True
            logging.warning('401 Unauthorized. Please check your credentials.')
        else:
            logging.warning(r.status_code)
        if badCreds:
            self.username = None
            self.password = None
            badCreds = False

    def do_add(self, arg):
        'Manually add/update a task and duration. Examples:\n\tadd CISOPS-001 00:10:00\n\tadd email 1:00:00'
        if not arg:
            print "Add command must specify a task/alias name. Examples:\n\tadd CISOPS-001 00:10:00\n\tadd email 1:00:00"
            return

        words = arg.split()
        task = words[0]
        # If the task is a Jira story, always store it in upper case to avoid duplicate entries
        if search("[A-Za-z]+\-[0-9]+",task):
            logging.debug('Converting Jira ID '+task+' to upper case')
            task = task.upper()
        try:
            hours = int(words[1].split(':')[0])
            mins = int(words[1].split(':')[1])
            secs = int(words[1].split(':')[2])
            duration = str(hours).zfill(2)+":"+str(mins).zfill(2)+":"+str(secs).zfill(2)
        except:
            print "Invalid time specified for task. Time must be in the format hh:mm:ss."
            return
        logging.debug("Adding task "+task+", duration "+duration)
        self.update_data(task, datetime.datetime.today(), duration)

    def do_delete(self, arg):
        'Manually delete a task from the tracking list.\n\tExamples: delete CISOPS-001\n\tdelete email'
        if not arg:
            print "A task name must be provided. Examples:\n\tdelete CISOPS-001\n\tdelete email"
            return
        if search("[A-Za-z]+\-[0-9]+",arg):
            logging.debug('Converting Jira ID '+arg+' to upper case')
            arg = arg.upper()
        self.load_data()
        if not self.data.has_key(arg):
            print "A task called \""+arg+"\" could not be found! Use 'report' to get a list of known tasks."
        else:
            confirm = ""
            while confirm.lower() != "y" and confirm.lower() != "n":
                confirm = raw_input("Are you sure you want to delete \""+arg+"\"? (y/n) ")
            if confirm.lower() == "y":
                del self.data[arg]
                self.save_data()

    def do_aliasview(self, arg):
        'View a list of aliases that map a custom task name to a Jira story.'
        self.load_data(file=self.ALIASFILE)
        for alias in self.aliases:
            print "Alias: "+alias+", Story: "+self.aliases[alias]['jira']+", Comment: "+self.aliases[alias]['comment']

    def do_aliasadd(self, arg):
        'Create an alias that maps a custom task name to a Jira story with an optional comment. Example:\n\taliasadd email CISOPS-1125 Daily emails'
        words = arg.split()
        if len(words) < 2:
            print "Invalid command syntax. Example:\n\taliasadd email CISOPS-1125 Daily emails"
        elif not search("[A-Z]+\-[0-9]+",words[1].upper()):
            print "Invalid format for Jira story."
        else:
            self.load_data(file=self.ALIASFILE)
            comment = ""
            # Funky logic to make sure a space isn't added after the last word in the comment
            if len(words) > 2:
                for i in xrange(1, len(words)):
                    if i == len(words)-1:
                        comment += words[i]
                    elif i >= 2:
                        comment += words[i]+" "
            self.aliases[words[0]] = {'jira': words[1].upper(), 'comment': comment}
            self.save_data(file=self.ALIASFILE)

    def do_aliasdel(self, arg):
        'Delete an alias that maps a custom task name to a Jira story. Example:\n\taliasdel email'
        self.load_data(file=self.ALIASFILE)
        if self.aliases.has_key(arg):
            confirm = ""
            while confirm.lower() != "y" and confirm.lower() != "n":
                confirm = raw_input("Are you sure you want to delete \""+arg+"\"? (y/n) ")
            if confirm.lower() == "y":
                del self.aliases[arg]
                self.save_data(file=self.ALIASFILE)

    def do_set(self, arg):
        'Set various config options:\n\tset jiraurl https://metacloud.jira.com\n\tset datafile /home/mirober2/timey_data.p\n\tset aliasfile /home/mirober2/timey_alias.p\n\tset log debug'
        global LOGLEVEL
        if not arg:
            print "\nAvailable options: jiraurl datafile aliasfile log\n"
            print "Current option values:"
            print "Jira URL: "+self.JIRA_URL
            print "Data file: "+self.DATAFILE
            print "Alias file: "+self.ALIASFILE
            print "Log level: "+LOGLEVEL
            return
        words = arg.split()
        if words[0] == "jiraurl":
            print "Old URL: "+self.JIRA_URL
            if len(words) > 1:
                self.JIRA_URL = words[1]
            print "New URL: "+self.JIRA_URL
        elif words[0] == "datafile":
            print "Old file: "+self.DATAFILE
            if len(words) > 1:
                self.DATAFILE = words[1]
            print "New file: "+self.DATAFILE
        elif words[0] == "aliasfile":
            print "Old file: "+self.ALIASFILE
            if len(words) > 1:
                self.ALIASFILE = words[1]
            print "New file: "+self.ALIASFILE
        elif words[0] == "log":
            levels = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']
            if len(words) > 1:
                if words[1].upper() not in levels:
                    print "Available levels: "+str(levels)
                else:
                    print "Old log level: "+LOGLEVEL
                    LOGLEVEL = words[1].upper()
                    logging.getLogger().setLevel(LOGLEVEL)
                    print "New log level: "+LOGLEVEL

    def do_version(self, arg):
        'Print the version of this script'
        print "Version: "+VERSION

    def do_begin(self, arg):
        'Start tracking time for a given task. Examples:\n\tbegin CISOPS-001\n\tbegin email'
        self.alias_start(arg)

    def do_start(self, arg):
        'Start tracking time for a given task. Examples:\n\tbegin CISOPS-001\n\tbegin email'
        self.alias_start(arg)

    def do_end(self, arg):
        'Stop tracking time for a given task. Examples:\n\tbegin CISOPS-001\n\tbegin email'
        self.alias_stop(arg)

    def do_stop(self, arg):
        'Stop tracking time for a given task. Examples:\n\tbegin CISOPS-001\n\tbegin email'
        self.alias_stop(arg)

    def do_quit(self, arg):
        'Stop the currently tracked task and exit'
        self.alias_exit(arg)

    def do_exit(self, arg):
        'Stop the currently tracked task and exit'
        self.alias_exit(arg)

if __name__ == '__main__':
    # Catch CTRL-C to make sure we save data before exiting
    def signal_handler(signal, frame):
        Timey.alias_exit(Timey(), "")
    signal.signal(signal.SIGINT, signal_handler)

    # Starts the parser
    Timey().cmdloop()
