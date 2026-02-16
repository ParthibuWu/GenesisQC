import io
import gzip
import bz2

def detect_compression(filename: str) -> str:
    name = filename.lower()
    if name.endswith((".gz", ".gzip")):
        return "gzip"
    elif name.endswith((".bz2", ".bzip2")):
        return "bzip2"
    return "none"


def detect_file_format(filename: str) -> str:
    name = filename.lower()

    for ext in [".gz", ".gzip", ".bz2", ".bzip2"]:
        if name.endswith(ext):
            name = name[:-len(ext)]

    if name.endswith((".fa", ".fasta", ".fna")):
        return "fasta"
    elif name.endswith((".fq", ".fastq")):
        return "fastq"
    elif name.endswith((".gb", ".gbk", ".genbank")):
        return "genbank"
    elif name.endswith(".embl"):
        return "embl"

    raise ValueError("Unsupported format")


def get_text_handle(content: bytes, compression: str):
    if compression == "gzip":
        return gzip.open(io.BytesIO(content), mode="rt")
    elif compression == "bzip2":
        return bz2.open(io.BytesIO(content), mode="rt")
    else:
        return io.StringIO(content.decode("utf-8"))
