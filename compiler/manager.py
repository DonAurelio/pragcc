import tempfile
import subprocess

class GccManager(object):

    def compile_raw_code(self,text):
        
        with tempfile.TemporaryDirectory() as dir_path:
            file_path = os.path.join(dir_path,'temp.c')

            with open(file_path,'w') as file:
                file.write(text)
                file.seek(0)

                command = 'gcc %s' % file_path
                process = subprocess.run(
                    args=command,
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    shell=True, 
                    universal_newlines=True
                )

                return process.stdout, process.stderr