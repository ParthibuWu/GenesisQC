from Bio import SeqIO
from Bio.SeqIO.QualityIO import FastqGeneralIterator
from typing import Optional, Dict
from file_utils import detect_compression, detect_file_format, get_text_handle
from sequence_analysis import calculate_gc_content


def process_uploaded_file(content: bytes,
                          filename: str,
                          filter_ids: Optional[str] = None,
                          stats_only: bool = True) -> Dict:

    compression = detect_compression(filename)
    file_format = detect_file_format(filename)
    handle = get_text_handle(content, compression)

    wanted_ids = None
    if filter_ids:
        wanted_ids = set(i.strip() for i in filter_ids.split(","))

    if file_format == "fastq":
        return _process_fastq(handle, wanted_ids, stats_only,
                              filename, compression)
    else:
        return _process_fasta_like(handle, file_format,
                                   wanted_ids, stats_only,
                                   filename, compression)


def _process_fastq(handle, wanted_ids, stats_only,
                   filename, compression):

    total_len = 0
    total_gc = 0
    total_reads = 0
    sequences = []

    for title, seq, qual in FastqGeneralIterator(handle):

        record_id = title.split(None, 1)[0]

        if wanted_ids and record_id not in wanted_ids:
            continue

        gc = calculate_gc_content(seq)
        avg_q = sum(ord(q) - 33 for q in qual) / len(qual) if qual else 0

        total_len += len(seq)
        total_gc += gc
        total_reads += 1

        if not stats_only:
            sequences.append({
                "ID": record_id,
                "Length": len(seq),
                "GC_content": gc,
                "Avg_quality": avg_q
            })

    result = {
        "filename": filename,
        "format": "fastq",
        "compression": compression,
        "total_sequences": total_reads,
        "total_bases": total_len,
        "average_length": round(total_len / total_reads, 2)
            if total_reads else 0,
        "average_gc_content": round(total_gc / total_reads, 2)
            if total_reads else 0,
        "filtered": bool(wanted_ids),
    }

    if not stats_only:
        result["sequences"] = sequences

    return result


def _process_fasta_like(handle, file_format,
                        wanted_ids, stats_only,
                        filename, compression):

    total_len = 0
    total_gc = 0
    count = 0
    sequences = []

    for record in SeqIO.parse(handle, file_format):

        if wanted_ids and record.id not in wanted_ids:
            continue

        seq = str(record.seq)
        gc = calculate_gc_content(seq)

        total_len += len(seq)
        total_gc += gc
        count += 1

        if not stats_only:
            sequences.append({
                "ID": record.id,
                "Length": len(seq),
                "GC_content": gc
            })

    result = {
        "filename": filename,
        "format": file_format,
        "compression": compression,
        "total_sequences": count,
        "total_bases": total_len,
        "average_length": round(total_len / count, 2)
            if count else 0,
        "average_gc_content": round(total_gc / count, 2)
            if count else 0,
        "filtered": bool(wanted_ids),
    }

    if not stats_only:
        result["sequences"] = sequences

    return result
