#!/usr/bin/env python
#
#  Copyright (C) Dario Clavijo (daedalus2027@gmail.com)
#
# Ref - http://ps3wiki.lan.st/index.php/XRegistry_File_Format
#
# This software is distributed under the terms of the GNU General Public
# License ("GPL") version 3, as published by the Free Software Foundation.
#

import os,time,sys,binascii

orig_header = "BCADADBC0000009000000002BCADADBC" 
data_marker = "4D26"
data_offset = "FFF0"

debug_mode=False

def tohex(text):
    return binascii.b2a_hex(text)

def hextoint(data):
    return int(f"0x{data}", 0)

def next_file_entry(f,list):

    offset = f.tell()
    entry_id_hex = tohex(f.read(2))
    entry_id = hextoint(entry_id_hex) 
    entry_len_hex = tohex(f.read(2))
    entry_len = hextoint(entry_len_hex)
    entry_value_hex = tohex(f.read(1)) 
    entry_value = hextoint(entry_value_hex)       
    entry_setting = f.read(entry_len)
    entry_sep = tohex(f.read(1))

    if (entry_sep == "00") and (entry_id_hex != "aabb") and (entry_len_hex != "ccdd"):
	tuple = [offset,entry_id,entry_setting,entry_value]
        list.append(tuple)
	if debug_mode: print "offset: " + str("%x" %  offset)  +  " ID: " + entry_id_hex   + " len:" + entry_len_hex + " data:" + entry_setting 
	return True 
    else:
	return False    

def next_data_entry(f,list):

    offset = f.tell()
    data_entry_flags_hex = tohex(f.read(2))
    data_entry_flags =  hextoint(data_entry_flags_hex)
    data_entry_filename_hex = tohex(f.read(2))
    data_entry_filename = hextoint(data_entry_filename_hex)
    data_entry_checksum_hex = tohex(f.read(2))
    data_entry_checksum = hextoint(data_entry_checksum_hex)
    data_entry_len_hex = tohex(f.read(2))
    data_entry_len = hextoint(data_entry_len_hex)    
    data_entry_type_hex = tohex(f.read(1))
    data_entry_type = hextoint(data_entry_type_hex)
    data_entry_data_value = f.read(data_entry_len)
    data_entry_sep_hex = tohex(f.read(1))

    if (data_entry_flags_hex != "aabb") and (data_entry_filename_hex != "ccdd") and (data_entry_checksum_hex != "ee00" ) :
	tuple = [offset,data_entry_flags,data_entry_filename,data_entry_checksum,data_entry_len,data_entry_type,data_entry_data_value]
        list.append(tuple)
	if debug_mode: print "offset:" + str("%x" %  offset) +  " ID: " + data_entry_filename_hex + " flags: " + data_entry_flags_hex + " checksum: " + data_entry_checksum_hex + " type: " + data_entry_type_hex + " data: " + data_entry_data_value
	return True
    else:
	return False

def is_data_mark(f):
    mark = f.read(2)
    mark_hex = tohex(mark) 
    if debug_mode: print "Mark: " + mark_hex
    return (mark_hex == "4d26")
    
def save_tuple_csv(fout,list):
    f = open(fout,"w")
    for tuple in list:
	string = tuple_to_csv(list)
        f.write(string + "\n")
    f.close()

def tuple_to_csv(tuple):
    if tuple != None:
	string = str(tuple)
	string = string.replace("[","")
	string = string.replace("]","")
    return string

def join_fields(filename_entrys,data_entrys):
    list = []
    for data_entry in data_entrys:
	i=0
	found=False
	while not found and i < len(filename_entrys):
	    filename_entry=filename_entrys[i]
	    i=i + 1
	    if (data_entry[2] == filename_entry[0] - 16):
		found=True
		tuple = [filename_entry,data_entry]
		list.append(tuple)
    return list

def proccess(fin,fout):
    print "File: " + fin
    f = open(fin,"rw+")
    data = f.read(16)
    hex_header = tohex(data)
    if hex_header == orig_header.lower(): 
	print "Header: Ok"
	filename_entrys = []
	filename_entry = next_file_entry(f,filename_entrys)
	while filename_entry:
	    filename_entry = next_file_entry(f,filename_entrys)
	print "Filename Entrys: " + str(len(filename_entrys))
	f.seek(hextoint("fff0"))
	if is_data_mark(f):
	    print "Data mark: Ok"
	    data_entrys = []
	    data_entry = next_data_entry(f,data_entrys)
	    while data_entry:
		data_entry = next_data_entry(f,data_entrys)
	    f.close()	
	    print "Data Entrys: " + str(len(data_entrys))
	    csv_list = join_fields(filename_entrys,data_entrys)
	    print "Joind Entrys: " + str(len(csv_list))
	    print "Writing: " + fout
	    save_tuple_csv(fout,csv_list)
	else:
	    print "Failed to read mark!"
	    f.close()

if __name__ == "__main__":
    #debug_mode=True
    if (len(sys.argv) > 2):
	fin = sys.argv[1]
	fout = sys.argv[2]
	if fin != "" and fout != "":
	    proccess(fin,fout)
	else:
	    print "..."
