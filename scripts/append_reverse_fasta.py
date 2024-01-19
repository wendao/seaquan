#!/usr/bin/env python
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio import SeqIO
import os, sys

fn = sys.argv[1]

handle = open( fn, "rU" )
full_handle = open( "wRev_"+fn, "w" )
for record in SeqIO.parse(handle, "fasta"):
    raw_desc = record.description
    #clean
    raw_desc = raw_desc.replace("'", "")
    raw_desc = raw_desc.replace("\"", "")
    #save
    record.description = raw_desc
    SeqIO.write( record, full_handle, "fasta" )
    bw_rec = record
    bw_rec.id = "rev_" + record.id
    bw_rec.description = " ".join(record.description.split()[1:])
    bw_rec.seq = bw_rec.seq[::-1]
    SeqIO.write( bw_rec, full_handle, "fasta" )

handle.close()

