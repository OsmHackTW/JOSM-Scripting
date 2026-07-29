# Python script for JOSM (jython engine)
# <script src="https://gist.github.com/bikeoid/cba84543b6c5b6ad72d44d7bb6dcb072.js"></script>
# log report function

import re, datetime
from javax.swing import JOptionPane
from org.openstreetmap.josm.gui import MainApplication
from org.openstreetmap.josm.data import UndoRedoHandler

from org.openstreetmap.josm.command import ChangePropertyCommand, SequenceCommand
from org.openstreetmap.josm.plugins.scripting.ui.console import ScriptingConsole
from org.openstreetmap.josm.tools import Logging

import org.openstreetmap.josm.command as Command

def log(msg):
    log_writer = ScriptingConsole.getInstance().getScriptLog().getLogWriter()
    log_writer.println(msg)

now=datetime.datetime.utcnow()

log("=== JOSM Script Started: " + str(now) + "===")

# -*- coding: utf-8 -*-

layer = MainApplication.getLayerManager().getEditLayer()
ds = layer.data

commands = []

for obj in ds.getSelected():

    tags = obj.getKeys()

    for k, v in tags.items():

        # ensure unicode
        k = unicode(k)
        v = unicode(v)
        
        # skip address tags
        if k.startswith("addr:"):
            continue

        # skip protected tags
        if k in ["source", "wikidata", "wikipedia"]:
            continue

        # skip already disused tags
        if k.startswith("disused:"):
            continue

        # skip already building tags
        if k.startswith("building"):
            continue

        new_key = "disused:" + k

        # remove original tag
        commands.append(
            ChangePropertyCommand([obj], k, None)
        )

        # add disused tag
        commands.append(
            ChangePropertyCommand([obj], new_key, v)
        )

# apply undoable command
if commands:
    seq = SequenceCommand(
        u"Convert tags to disused:* (except addr:, source, wikidata)",
        commands
    )
#    MainApplication.getUndoRedo().add(seq)
    UndoRedoHandler.getInstance().add(seq)
 #   UndoRedoHandler.getInstance().add(
log("Commands modified for {} tags".format(len(commands)))

now=datetime.datetime.utcnow()
log("=== JOSM Script Finished: " + str(now) + "===")
