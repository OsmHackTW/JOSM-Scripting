from org.openstreetmap.josm.gui import MainApplication
from org.openstreetmap.josm.command import ChangePropertyCommand, SequenceCommand
from org.openstreetmap.josm.plugins.scripting.ui.console import ScriptingConsole
from org.openstreetmap.josm.data import UndoRedoHandler

import re, datetime

# -*- coding: utf-8 -*-

layer = MainApplication.getLayerManager().getEditLayer()
ds = layer.data

def log(msg):
    log_writer = ScriptingConsole.getInstance().getScriptLog().getLogWriter()
    log_writer.println(msg)

start_time=datetime.datetime.utcnow()
log("=== JOSM Script Started: " + str(start_time) + "===")

layer = MainApplication.getLayerManager().getEditLayer()
ds = layer.data

# Unicode-safe regex
pattern = re.compile(u"號$")

targets = []

# find objects with addr:housenumber ending with 號
for obj in ds.allPrimitives():

    value = obj.get("addr:housenumber")

    if obj.get("addr:TW:dataset"):
    	   continue

    if value and pattern.search(value):
        targets.append(obj)

commands = []

for obj in targets:

    old_value = obj.get("addr:housenumber")

    new_value = pattern.sub(u"", old_value)

    commands.append(
        ChangePropertyCommand([obj], "addr:housenumber", new_value)
    )

# Apply edits with undo support
if commands:

    seq = SequenceCommand(
        u"Remove trailing 號 from addr:housenumber",
        commands
    )

    UndoRedoHandler.getInstance().add(seq)

# log("Modified objects: " + str(len(commands)))

log(u"Matched objects: {}".format(len(targets)))
log(u"id,type,where,housenumber")

for obj in targets:
    log(
        u"{},{},{},{}".format(
            obj.getId(),
            obj.getType().toString(),
            obj.get("addr:street") or obj.get("addr:place"),
            obj.get("addr:housenumber")
        )
    )

finish_time=datetime.datetime.utcnow()
log("=== JOSM Script Finished: " + str(finish_time) + "===")

