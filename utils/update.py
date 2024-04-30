import os
import shutil
import tarfile
import deflate

def unpack_tgz(tgz_path, to_path):
    os.mkdir(to_path[:-1])
    with open(tgz_path, 'rb') as tgz:
        tar_file = deflate.DeflateIO(tgz, deflate.AUTO, 9)
        unpack_tar = tarfile.TarFile(fileobj=tar_file)
        for unpack_file in unpack_tar:
            if unpack_file.type != tarfile.DIRTYPE and not '@PaxHeader' in unpack_file.name:
                out_filepath = to_path + unpack_file.name[2:]
                makedirs(out_filepath)
                subf = unpack_tar.extractfile(unpack_file)
                with open(out_filepath, "wb") as outf:
                    shutil.copyfileobj(subf, outf)
                    outf.close()

def makedirs(name, mode=0o777):
    ret = False
    s = ""
    comps = name.rstrip("/").split("/")[:-1]
    if comps[0] == "":
        s = "/"
    for c in comps:
        if s and s[-1] != "/":
            s += "/"
        s += c
        try:
            os.mkdir(s)
            ret = True
        except:
            pass
    return ret

def copy_file(from_path, to_path):
    with open(from_path, 'rb') as from_file:
        with open(to_path, 'wb') as to_file:
            CHUNK_SIZE = 256
            data = from_file.read(CHUNK_SIZE)
            while data:
                to_file.write(data)
                data = from_file.read(CHUNK_SIZE)
        to_file.close()
    from_file.close()

def copy_directory(from_path, to_path):
    for entry in os.ilistdir(from_path):
        if entry[1] == 0x4000:
            copy_directory(from_path + '/' + entry[0], to_path + '/' + entry[0])
        else:
            print(from_path, entry[0])
            copy_file(from_path + '/' + entry[0], to_path + '/' + entry[0])
