import subprocess
import json
import jinja2
import os
import zipfile
import uuid

def write_jinja_file(logger, d, i_filename, o_filename, path):
    try:
        cwd = os.getcwd()
        os.chdir(path)
        logger.info(f"jinja templating {i_filename}")
        j2loader = jinja2.FileSystemLoader(path)
        j2env = jinja2.Environment(loader=j2loader)
        j2template = j2env.get_template(i_filename)
        output = j2template.render(d)
        with open(o_filename, "w") as fh:
            fh.write(output)
            fh.close()
        os.chdir(cwd)
        return
    except Exception as e:
        logger.exception(e)
        os.chdir(cwd)
        raise

def zip_function_upload(logger, zip_file_name, path):
    try:
        cwd = os.getcwd()
        os.chdir(path)
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
        os.chdir(cwd)
        return zip_file_name
    except Exception as e:
        logger.exception(e)
        os.chdir(cwd)
        raise

class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)

def streaming_output(cmd, dirc, logger):
    try:
        p = subprocess.Popen(cmd,
                            cwd=dirc,
                            stdout=subprocess.PIPE)
        for line in iter(p.stdout.readline, b''):
            logger.info('>>> {}'.format(line.rstrip()))
        return
    except Exception as e:
        logger.info(e)
        raise

def create_cdk_json(d, cdk_dir, logger):
    try:
        cdk_file = '{}/cdk.json'.format(cdk_dir)
        with open(cdk_file, 'w') as outfile:
            json.dump({
                'app':'python3 main.py',
                'context':d
                }, outfile, indent=2, separators=(',', ': '), cls=SetEncoder)
        logger.info("Creating cdk context file:")
        return
    except Exception as e:
        logger.info(e)
        raise
