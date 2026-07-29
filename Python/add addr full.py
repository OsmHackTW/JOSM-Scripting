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

layer = MainApplication.getLayerManager().getEditLayer()
ds = layer.data

commands = []

digits = {
    0:u"零",1:u"一",2:u"二",3:u"三",4:u"四",
    5:u"五",6:u"六",7:u"七",8:u"八",9:u"九"
}

def to_chinese(n):
    n = int(n)
    if n <= 10:
        if n == 10:
            return u"十"
        return digits[n]
    elif n < 20:
        return u"十" + digits[n % 10]
    elif n < 100:
        tens = digits[n // 10] + u"十"
        ones = n % 10
        if ones == 0:
            return tens
        return tens + digits[ones]
    else:
        return str(n)

targets = []

for obj in ds.allPrimitives():

    addr_full = obj.get("addr:full") or ""
    postcode = obj.get("addr:postcode") or ""
    city = obj.get("addr:city") or ""
    district = obj.get("addr:district") or ""
    hamlet = obj.get("addr:hamlet") or ""
    neighbourhood = obj.get("addr:neighbourhood") or ""
    street = obj.get("addr:street") or ""
    place = obj.get("addr:place") or ""
    housenumber = obj.get("addr:housenumber") or ""
    floor = obj.get("addr:floor") or ""
    unit = obj.get("addr:unit") or ""

    if not housenumber:
        continue

    road = street if street else place

    if housenumber:
        housenumber = re.sub(u"號$", u"", housenumber)

    if addr_full:
    	   continue
    
    addr_full = u"{}{}{}{}{}{}{}號".format(
        postcode,
        city,
        district,
        hamlet,
        neighbourhood,
        road,
        housenumber
    )

    if floor:
        # remove trailing 樓
        floor_clean = re.sub(u"樓$", u"", floor)

        try:
            floor_cn = to_chinese(int(floor_clean))
            addr_full += floor_cn + u"樓"
        except:
            addr_full += floor_clean + u"樓"

    if unit:
        addr_full += u"之{}".format(unit)

    targets.append(obj)
    
    commands.append(
        ChangePropertyCommand([obj], "addr:full", addr_full)
    )

if commands:
    UndoRedoHandler.getInstance().add(
        SequenceCommand("Generate addr:full with Chinese floors", commands)
    )

log("Generated addr:full for {} objects".format(len(commands)))

for obj in targets:
    log(
        u"{},{},{}".format(
            obj.getId(),
            obj.getType().toString(),
            obj.get("addr:full")
        )
    )

now=datetime.datetime.utcnow()
log("=== JOSM Script Finished: " + str(now) + "===")
