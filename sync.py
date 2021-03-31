import os
import json
import time
import logging
import requests as r
from pprint import pprint
from slack_bolt import App
from dotenv import load_dotenv

load_dotenv()
app = App()

journal_channel = 'C01T2K8K328'
sep = '<br/>'


try: 
    with open('state.txt') as json_file:
        state = json.load(json_file)
        last = state['oldest']

except: 
    print("No state, starting fresh")
    state = {'oldest': 0}
    last = 0

entries = []
messages = app.client.conversations_history(channel=journal_channel, oldest=state['oldest'])['messages']
for message in messages: 
    entry = "**" + (time.strftime("%I:%m %p", time.localtime(float(message['ts']))) + "**" + sep)
    entry += message['text']
    entries.append(entry)
    state['oldest'] = max(float(message['ts']), state['oldest'])

if last: 
    entries.pop() # there'll be an extra at the end

journal_string = (2*sep).join(entries[::-1])
journal_string = f"{len(entries)} DM{'s' if len(entries) > 1 else ''} today:" + sep*2 + journal_string

if entries:
    print("Journal String:\n")
    print(journal_string)
    r.post('https://maker.ifttt.com/trigger/slack_day_one_sync/with/key/13Z80uk8mT-kN-RWMAOPl', data={"value1": journal_string, "value2": time.strftime("%m/%d", time.localtime())})
    print("Journal entry made!")
else: 
    print("No entries to report")


with open('state.txt', 'w') as outfile:
    json.dump(state, outfile)
