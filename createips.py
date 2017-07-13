#!/usr/bin/env python

import os
import struct
import subprocess
from contextlib import suppress

free_addr = 0x205000

patchname = ""
firmver = ""
titleid = ""
text_end = 0x0
text_padding_end = 0x0
patch = bytearray()

def begin_patch(_titleid, _text_end, _text_padding_end):
    global patch, titleid, text_end, text_padding_end
    patch = str.encode("PATCH");
    titleid = _titleid
    text_end = _text_end;
    text_padding_end = _text_padding_end

def end_patch():
    global patch, firmver, patchname, titleid
    patch += str.encode("EOF");
    with suppress(FileExistsError): os.mkdir("patches")
    with suppress(FileExistsError): os.mkdir("patches/" + patchname)
    with suppress(FileExistsError): os.mkdir("patches/" + patchname + "/" + firmver)
    with suppress(FileExistsError): os.mkdir("patches/" + patchname + "/" + firmver + "/" + titleid)
    open("patches/" + patchname + "/" + firmver + "/" + titleid + "/code.ips", "wb").write(patch)

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

def patch_statusbatpercent_eu_11_4():
    """ Battery percent in statusbar """
    begin_patch("0004003000009802", 0x2050C4, 0x2058C4)
    # Update date while updating minutes
    replace_instruction(0x000EF1D0, "mov r5, 1")
    # Replace date string with battery percent
    add_function_call(0x000EF30C, "src/statusbattery.s", "statusbattery.bin", {
        0xdead0000 : 0x33C14C
    });
    end_patch()

def patch_statusbatpercent_eu_11_5():
    """ Battery percent in statusbar """
    begin_patch("0004003000009802", 0x20512C, 0x20592C)
    # Update date while updating minutes
    replace_instruction(0x000EF190, "mov r5, 1")
    # Replace date string with battery percent
    add_function_call(0x000EF2CC, "src/statusbattery.s", "statusbattery.bin", {
        0xdead0000 : 0x33C14C
    });
    end_patch()

def patch_statusbaticon_eu_11_4():
    """ Battery icon in statusbar shows each bar as 25% of charge """
    begin_patch("0004003000009802", 0x2050C4, 0x2058C4)
    # Replace call to GetBatteryLevel
    add_function_call(0x000FF3EC, "src/statusbatteryicon.s", "statusbatteryicon.bin", {
        0xdead0000 : 0x33C14C
    });
    end_patch()

def patch_statusbaticon_eu_11_5():
    """ Battery icon in statusbar shows each bar as 25% of charge """
    begin_patch("0004003000009802", 0x20512C, 0x20592C)
    # Replace call to GetBatteryLevel
    add_function_call(0x000FF3AC, "src/statusbatteryicon.s", "statusbatteryicon.bin", {
        0xdead0000 : 0x33C14C
    });
    end_patch()

patchname = "statusbatpercent"
firmver = "11.4"
patch_statusbatpercent_eu_11_4()
firmver = "11.5"
patch_statusbatpercent_eu_11_5()

patchname = "statusbaticon"
firmver = "11.4"
patch_statusbaticon_eu_11_4()
firmver = "11.5"
patch_statusbaticon_eu_11_5()
