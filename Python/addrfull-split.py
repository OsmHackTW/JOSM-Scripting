# Python script for JOSM (jython engine)
# <script src="https://gist.github.com/bikeoid/cba84543b6c5b6ad72d44d7bb6dcb072.js"></script>
# log report function
# -*- coding: utf-8 -*-

from org.openstreetmap.josm.gui import MainApplication
from org.openstreetmap.josm.command import ChangePropertyCommand, SequenceCommand
import re, datetime
from javax.swing import JOptionPane
from org.openstreetmap.josm.gui import MainApplication
from org.openstreetmap.josm.data import UndoRedoHandler
from org.openstreetmap.josm.plugins.scripting.ui.console import ScriptingConsole
from org.openstreetmap.josm.tools import Logging

import org.openstreetmap.josm.command as Command

def log(msg):
    log_writer = ScriptingConsole.getInstance().getScriptLog().getLogWriter()
    log_writer.println(msg)

now=datetime.datetime.utcnow()

log("=== JOSM Script Started: " + str(now) + "===")

layer = MainApplication.getLayerManager().getEditLayer()
ds = layer.data

# =========================
# SETTINGS
# =========================

PREVIEW_MODE = True

addr_pattern = re.compile(
    # u'^(?:(?P<postcode>\d{3,6}))?' 
    # include 4 figures postcode which doesn't exist
    u'^(?:(?P<postcode>\d{3}|\d{5,6}))?'
    u'(?P<city>[^\w{2}]+[縣市])'
    u'(?P<district>[^\w{1,3}]+[鄉鎮市區])'
    u'(?:(?P<hamlet>[^\w{1,4}]+[村里]))?'
    u'(?:(?P<neighbourhood>\d{1,2}鄰))?'
    u'(?P<streetplace>.*?)'
    u'(?:(?P<housenumber>\d+(?:[-之]\d+)?)號)'
    u'(?:(?P<floor>B?\d+樓))?'
    u'(?:號之(?P<unit>\d+)|號)?'
)

# =========================

commands = []

stats = {
    "objects_checked":0,
    "addresses_parsed":0
}

for obj in ds.getSelected():

    stats["objects_checked"] += 1

    addr_full = obj.get("addr:full")

    if not addr_full:
        continue

    addr_full = unicode(addr_full)

    m = addr_pattern.search(addr_full)

    if not m:
        continue

    stats["addresses_parsed"] += 1

    postcode = m.group("postcode")
    city = m.group("city")
    district = m.group("district")
    hamlet = m.group("hamlet")
    neighbourhood = m.group("neighbourhood")
    streetplace = m.group("streetplace")
    housenumber = m.group("housenumber")
    floor = m.group("floor")
    unit = m.group("unit")

    new_tags = {}

    if postcode:
        new_tags["addr:postcode"] = postcode

    new_tags["addr:city"] = city
    new_tags["addr:district"] = district
    new_tags["addr:housenumber"] = housenumber

    if hamlet:
        new_tags["addr:hamlet"] = hamlet

    if neighbourhood:
        new_tags["addr:neighbourhood"] = neighbourhood

    if floor:
        new_tags[u"addr:floor"] = floor.replace(u"樓",u"")

    if unit:
    	   new_tags[u"addr:unit"] = unit.replace(u"之",u"")

    # detect street or place
    if re.search(u"[路街大道巷弄段]", streetplace):
        new_tags["addr:street"] = streetplace
    else:
        new_tags["addr:place"] = streetplace

    if PREVIEW_MODE:

        log(u"\n--- PREVIEW ---")
        log(addr_full)

        for k,v in new_tags.items():
            log(u" " + k + u"=" + v)

    else:

        for k,v in new_tags.items():
            commands.append(ChangePropertyCommand([obj], k, v))


if not PREVIEW_MODE and commands:

    seq = SequenceCommand(
        u"Split addr:full with postcode and floor",
        commands
    )

    # MainApplication.getUndoRedo().add(seq)
    UndoRedoHandler.getInstance().add(seq)

log(u"\n------ Report ------")
log(u"Objects checked:" + str(stats["objects_checked"]))
log(u"Addresses parsed:" + str(stats["addresses_parsed"]))
    
log(u"Preview mode:" + str(PREVIEW_MODE))

now=datetime.datetime.utcnow()
log("=== JOSM Script Finished: " + str(now) + "===")
