from lib.logger import Logger
import jinja2
import os
import zipfile


def template(logger, d, chdir, i_filename, o_filename):
    logger.info(f"Creating template for {i_filename}")
    logger.info(f"Zipping function {i_filename} into {o_filename}")
    jinja(logger, d, i_filename, chdir)    
    zip_function_upload(logger, o_filename,  chdir)
    return

def jinja(logger, d, i_filename, path):
    try:
        olddir = os.getcwd()
        newdir = f"{path}/test/"
        os.chdir(newdir)
        logger.info(os.getcwd())
        logger.info(os.listdir())
        j2loader = jinja2.FileSystemLoader(newdir)
        j2env = jinja2.Environment(loader=j2loader)
        j2template = j2env.get_template(i_filename)
        output = j2template.render(d)
        with open("bash.sh", "w") as fh:
            fh.write(output)
        os.chdir(olddir)
        return
    except Exception as e:
        logger.exception(e)
        raise

def zip_function_upload(logger, zip_file_name, path):
    try:
        #os.chdir(path)
        if os.path.exists(zip_file_name):
            try:
                os.remove(zip_file_name)
            except OSError:
                pass
        zip_file = zipfile.ZipFile(zip_file_name, mode='a')
        for folder, subs, files in os.walk('.'):
            for filename in files:
                file_path = os.path.join(folder, filename)
                if not zip_file_name in file_path:
                    zip_file.write(file_path)
        zip_file.close()
        os.chdir(olddir)
        return
    except Exception as e:
        logger.exception(e)
        raise

logger = Logger(loglevel='info')
chdir = os.getcwd()


template(logger, {'name':'HELLOWORLD'}, chdir, 'bash.sh.j2', 'buildspec.yml.zip')
