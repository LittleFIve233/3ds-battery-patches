#!/usr/bin/env python

import os
import struct
import subprocess
from contextlib import suppress

patchname = ""
firmver = ""
titleid = ""
text_end = 0x0
text_padding_end = 0x0
patch = bytearray()

def current_patch_directory():
    return "build/" + patchname + "/" + firmver + "/" + titleid

def begin_patch(_titleid, _text_end, _text_padding_end):
    global patch, titleid, text_end, text_padding_end
    patch = str.encode("PATCH");
    titleid = _titleid
    text_end = _text_end;
    text_padding_end = _text_padding_end

def end_patch():
    global patch, firmver, patchname, titleid
    patch += str.encode("EOF");
    with suppress(FileExistsError): os.mkdir("build")
    with suppress(FileExistsError): os.mkdir("build/" + patchname)
    with suppress(FileExistsError): os.mkdir("build/" + patchname + "/" + firmver)
    with suppress(FileExistsError): os.mkdir("build/" + patchname + "/" + firmver + "/" + titleid)
    open(current_patch_directory() + "/code.ips", "wb").write(patch)

def make_branch_link(src, dst):
    opcode = 0xEB000000 | ((((dst - src) >> 2) - 2) & 0xFFFFFF)
    return struct.pack("<I", opcode)

def add_function_call(addr, inputfile, outputfile, substitutions = {}):
    global patch, text_end, text_padding_end
    if subprocess.call(["armips", inputfile]) != 0:
        exit(1)

    content = bytearray(open(outputfile, "rb").read())
    if text_end + len(content) > text_padding_end:
        print(titleid + ": Not enough free space for function body")
        return

    patch += struct.pack(">I", addr)[1:]
    patch += struct.pack(">H", 0x0004)
    patch += make_branch_link(addr, text_end)

    i = 0
    while i < len(content):
        word = struct.unpack("<I", content[i:i+4])[0]
        if word in substitutions:
            content[i:i+4] = struct.pack("<I", substitutions[word])
        i += 4;

    patch += struct.pack(">I", text_end)[1:]
    patch += struct.pack(">H", len(content))
    patch += content

    text_end += len(content)

def make_instruction(instruction):
    source = ".arm.little\n.create \"instruction.bin\",0\n.arm\n_start:\n" + instruction + "\n.close\n"
    open("instruction.s", "w").write(source)
    if subprocess.call(["armips", "instruction.s"]) != 0:
        exit(1)
    out = open("instruction.bin", "rb").read()
    os.remove("instruction.s")
    os.remove("instruction.bin")
    return out

def replace_instruction(addr, instruction):
    global patch
    patch += struct.pack(">I", addr)[1:]
    patch += struct.pack(">H", 0x0004)
    patch += make_instruction(instruction)

def exheader_add_service(exheader, service):
    for i in range(0x250, 0x350, 8):
        if exheader[i:i+8] == bytearray(8):
            exheader[i:i+8] = bytearray(service, "ascii")
            break
    for i in range(0x650, 0x750, 8):
        if exheader[i:i+8] == bytearray(8):
            exheader[i:i+8] = bytearray(service, "ascii")
            break
    return exheader

#
# statusbatpercent
#

def patch_statusbatpercent_JP():
    """ Battery percent in statusbar """
    begin_patch("0004003000008202", 0x20514C, 0x20614C)
    # Update date while updating minutes
    replace_instruction(0x000EF1B0, "add r5, r5, 1")
    # Replace date string with battery percent
    add_function_call(0x000EF2EC, "src/statusbattery.s", "statusbattery.bin", {
        0xdead0000 : 0x33C14C,
        0xdead0001 : 0x3412D9
    });
    end_patch()

def patch_statusbatpercent_US():
    """ Battery percent in statusbar """
    begin_patch("0004003000008F02", 0x20514C, 0x20614C)
    # Update date while updating minutes
    replace_instruction(0x000EF1B0, "add r5, r5, 1")
    # Replace date string with battery percent
    add_function_call(0x000EF2EC, "src/statusbattery.s", "statusbattery.bin", {
        0xdead0000 : 0x33C14C,
        0xdead0001 : 0x3412D9
    });
    end_patch()

    
def patch_statusbatpercent_EU():
    """ Battery percent in statusbar """
    begin_patch("0004003000009802", 0x20514C, 0x20614C)
    # Update date while updating minutes
    replace_instruction(0x000EF1B0, "add r5, r5, 1")
    # Replace date string with battery percent
    add_function_call(0x000EF2EC, "src/statusbattery.s", "statusbattery.bin", {
        0xdead0000 : 0x33C14C,
        0xdead0001 : 0x3412D9
    });
    end_patch()

#
# statusbaticon
#

def patch_statusbaticon_JP():
    """ Battery icon in statusbar shows each bar as 25% of charge """
    begin_patch("0004003000008202", 0x20514C, 0x20614C)
    # Replace call to GetBatteryLevel
    add_function_call(0x000EF3CC, "src/statusbatteryicon.s", "statusbatteryicon.bin", {
        0xdead0000 : 0x33C14C,
        0xdead0001 : 0x3412D9
    });
    end_patch()

def patch_statusbaticon_US():
    """ Battery icon in statusbar shows each bar as 25% of charge """
    begin_patch("0004003000008F02", 0x20514C, 0x20614C)
    # Replace call to GetBatteryLevel
    add_function_call(0x000EF3CC, "src/statusbatteryicon.s", "statusbatteryicon.bin", {
        0xdead0000 : 0x33C14C,
        0xdead0001 : 0x3412D9
    });
    end_patch()

def patch_statusbaticon_EU():
    """ Battery icon in statusbar shows each bar as 25% of charge """
    begin_patch("0004003000009802", 0x20514C, 0x20614C)
    # Replace call to GetBatteryLevel
    add_function_call(0x000EF3CC, "src/statusbatteryicon.s", "statusbatteryicon.bin", {
        0xdead0000 : 0x33C14C,
        0xdead0001 : 0x3412D9
    });
    end_patch()

#
# sm_home
#

def patch_sm_home_J():
    exheader = bytearray(open("extheader_J.bin", "rb").read())
    exheader_patched = exheader_add_service(exheader, "mcu::HWC")
    open(current_patch_directory() + "/exheader.bin", "wb").write(exheader_patched)

def patch_sm_home_U():
    exheader = bytearray(open("extheader_U.bin", "rb").read())
    exheader_patched = exheader_add_service(exheader, "mcu::HWC")
    open(current_patch_directory() + "/exheader.bin", "wb").write(exheader_patched)

def patch_sm_home_E():
    exheader = bytearray(open("extheader_E.bin", "rb").read())
    exheader_patched = exheader_add_service(exheader, "mcu::HWC")
    open(current_patch_directory() + "/exheader.bin", "wb").write(exheader_patched)

# Create statusbatpercent patches
patchname = "statusbatpercent"
firmver = "JP"
patch_statusbatpercent_JP()
patch_sm_home_J()
firmver = "US"
patch_statusbatpercent_US()
patch_sm_home_U()
firmver = "EU"
patch_statusbatpercent_EU()
patch_sm_home_E()

# Create statusbaticon patches
patchname = "statusbaticon"
firmver = "JP"
patch_statusbatpercent_JP()
patch_sm_home_J()
firmver = "US"
patch_statusbatpercent_US()
patch_sm_home_U()
firmver = "EU"
patch_statusbatpercent_EU()
patch_sm_home_E()
