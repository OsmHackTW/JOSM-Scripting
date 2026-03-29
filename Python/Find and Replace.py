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

# =========================
# USER SETTINGS
# =========================

PREVIEW_MODE = True     # True = show result only, False = apply changes

# rename keys, you can ignore the part to just the select parts
KEY_RENAME = {
    u"source:addr": u"source",
    u"addr:place_name": u"addr:place"
}

# regex value transformations, fixing Bafang for example
VALUE_REGEX = {
    u"name": (u"八方雲集 Bafang Dumpling", u"八方雲集"),     # fix the bilingual name to zh
    u"brand": (u"八方雲集 Bafang Dumpling", u"八方雲集"),    # fie the bilingual brand to zh
    "name:en": ("Bafang Dumpling", "Eight Way"),          # rename from Bafang to Eight Way
    "brand:en": ("Bafang Dumpling", "Eight Way")          # rename brand from Bafang to Eight Way
}

# =========================

commands = []
stats = {
    "objects_checked": 0,
    "tags_modified": 0,
    "keys_renamed": 0,
    "values_changed": 0
}

for obj in ds.getSelected():

    stats["objects_checked"] += 1

    tags = obj.getKeys()

    for k, v in tags.items():

        k = unicode(k)
        v = unicode(v)

        new_key = k
        new_value = v

        # key rename
        if k in KEY_RENAME:
            new_key = KEY_RENAME[k]
            stats["keys_renamed"] += 1

        # regex value transform
        if k in VALUE_REGEX:

            pattern, repl = VALUE_REGEX[k]

            if re.search(pattern, v):

                new_value = re.sub(pattern, repl, v)
                stats["values_changed"] += 1

        if new_key != k or new_value != v:

            stats["tags_modified"] += 1

            if PREVIEW_MODE:

                log(u"[PREVIEW]" + str(obj.getId()))
                log(k + u"=" + v + u"→" + new_key + u"=" + new_value)

            else:

                if new_key != k:
                    commands.append(ChangePropertyCommand([obj], k, None))

                commands.append(ChangePropertyCommand([obj], new_key, new_value))


# apply changes
if not PREVIEW_MODE and commands:

    seq = SequenceCommand(
        u"Advanced tag refactor",
        commands
    )

    # MainApplication.getUndoRedo().add(seq)
    UndoRedoHandler.getInstance().add(seq)
    
# =========================
# Statistics
# =========================

log(u"----- Tag Refactor Report -----")
log(u"Objects scanned: " + str(stats["objects_checked"]))
log(u"Tags modified: " + str(stats["tags_modified"]))
log(u"Keys renamed: " + str(stats["keys_renamed"]))
log(u"Values changed: " + str(stats["values_changed"]))
log(u"Preview mode: " +  str(PREVIEW_MODE))

now=datetime.datetime.utcnow()
log("=== JOSM Script Finished: " + str(now) + "===")
