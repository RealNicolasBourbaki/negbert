from threading import Lock
import pathlib
import traceback
import os
import time
import sys
import shutil

from config import MODEL_SAVE

RUNNING = True
STOPPING = False
SUCCESS = 1
FAILURE = 0
STOP = -1


class TPP:
    """
    This is the Python implementation of the Trivial Pseudo Pipeline for Expensive-to-start Modules (TPP).

    It is some sort of Minimal Multilingual Filesystem-Only-based Message Queue where the "Message" is a file.
    "Multilingual" only means that it is implemented in both Python and Java.
    "Minimal" should mean that we do not require a 3rd party library in order to run
    
    Author of original Java version: Fritz.Hohl@sony.com
    Author of Python version: Soh-Eun.Shim@sony.com
    Date 27.07.2022    
    """
    moduleId = "none"  # the configuration id of this module
    inputDir = ""  # the path to the input direcory
    outputDir = ""  # the path to the output directory
    counter = 0  # the counter of the module (or, to be more exact, the next free counter number); needed for writing output files
    index = 0  # the read counter of the module
    lock = Lock()

    class ReadStatus:
        status = 'success'
        input = ''

    """
	Gets the path to the config file
	returns: A Path object to the config file
	"""

    def get_config_path(self):
        fileName = 'config' + self.moduleId + '.txt'
        filePath = pathlib.Path(self.inputDir, fileName)
        return filePath

    """
	Checks if a config file exists in the input directory
	returns: A boolean indicating whether the config file exists
	"""

    def config_exists(self):
        return os.path.exists(self.get_config_path())

    """
    Reads the counters in the config file into class variables
    returns: 1 if successfully read, 0 if not
    """

    def config_read(self):
        if not self.config_exists():
            print('No config file found')
        else:
            print('Config file found, loading counters')
            with open(self.get_config_path(), "r", encoding='utf8') as file:
                counters = file.readlines()
                self.counter = int(counters[0].rstrip('\n'))
                self.index = int(counters[1].rstrip('\n'))
                file.close()

    """
    Writes the counter and index variables into a config file in the input folder
    Returns: 1 if successfully written, 0 if not
    """

    def config_write(self):
        readCounterStr = str(self.counter)
        writeCounterStr = str(self.index)
        with open(self.get_config_path(), "w", encoding='utf8') as file:
            file.write(readCounterStr + '\n' + writeCounterStr)
            file.close()

    """
    This is just a pseudo core work routine that would contain the actual logic of this module
    Param input: this is the input file content
    Returns: this is the output file content
    """

    def work(self, input: str):

        from transformers_for_negation_and_scope_speculation import CustomData, sentence_reader

        tokenized_sent = sentence_reader(input)

        data = CustomData(tokenized_sent).get_cue_dataloader()
        cues = cue_model.predict(data)[0]
        data = CustomData(tokenized_sent, cues=cues).get_scope_dataloader()
        scopes = scp_model.predict(data)

        these_cues, these_scopes = [], []
        for word, cue, scope in zip(tokenized_sent, cues[0], scopes):
            if cue != "3":
                these_cues.append(word)
            if scope == "1":
                these_scopes.append(word)

        return "sentence: " + tokenized_sent[0] + "\t cues: " + " ".join(these_cues) + "\t scopes: " + " ".join(
            these_scopes)

    """
    TPP library call to write a file (in outputDir) which will contain output
    Returns: SUCCESS if everything went fine, FAILURE else
    """

    def tpp_write(self, output: str, outputDir: str):
        status = SUCCESS
        try:
            filename = ''
            self.lock.acquire()
            filename = self.moduleId + "-" + str(self.counter) + ".txt"
            self.counter += 1
            self.lock.release()
            filepath1 = outputDir + filename

            with open(filepath1, "w", encoding='utf8') as file:
                file.write(output)
                file.close()

            filepath2 = outputDir + "m" + filename
            source = pathlib.Path(filepath1)
            target = pathlib.Path(filepath2)
            os.replace(source, target)
            print("written " + filepath2)

        except Exception as e:
            print("tpp_write: Exception occurred: " + str(e))
            traceback.print_exception(type(e), e, e.__traceback__)
            status = FAILURE

        return (status)

    def tpp_busy_read(self, inputDir: str):
        status = self.ReadStatus()
        status.status = SUCCESS
        doLoop = True

        folder = inputDir
        while (doLoop):
            for fileEntry in os.listdir(folder):
                if not os.path.isdir(fileEntry):
                    fileName = os.path.basename(fileEntry)
                    if fileName == 'STOP':
                        print('Copying STOP file to output directory')
                        shutil.copy(pathlib.Path(inputDir, fileEntry), pathlib.Path(tpp.outputDir, fileEntry))
                        print('Writing config file')
                        self.config_write()
                        doLoop = False
                        status.status = FAILURE
                        break

                    if fileName.startswith('m') and '-' in fileName:
                        foundIndex = fileName.split('-')[1]
                        if foundIndex.endswith('.txt'):
                            foundIndex = os.path.splitext(foundIndex)[0]

                foundIndexInt = -1

                try:
                    foundIndexInt = int(foundIndex)

                except:
                    # intentionally left blank
                    None

                if foundIndexInt >= self.index:
                    print("I will now process " + fileName)
                    text = ""
                    try:
                        with open(pathlib.Path(inputDir, fileName), "r", encoding='utf8') as file:
                            text = file.readlines()
                            file.close()

                    except Exception as e:
                        print("Problem reading " + fileName + ": " + str(e))
                    doLoop = False
                    status.status = SUCCESS
                    status.input = ''.join(text)
                    self.index = foundIndexInt + 1
                    break
            # wait a little bit

            try:
                time.sleep(0.025)
            except KeyboardInterrupt as e:
                print("Who interrupted my sleep?")
                traceback.print_exception(type(e), e, e.__traceback__)

        return (status)


if __name__ == '__main__':
    tpp = TPP()
    status = RUNNING
    output = ""
    readStatus = tpp.ReadStatus()
    writeStatus = SUCCESS
    print("TPP starting...")
    if len(sys.argv) != 4:
        print('usage: java TPP <module-id> <input dir> <output dir>')
        print('The directories need to also include the final directory separator at the end, e.g. / for Linux')
        status = STOPPING
    else:
        tpp.moduleId = sys.argv[1]
        tpp.inputDir = sys.argv[2]
        # if not inputDir.endswith("\\"):
        #    inputDir += "\\"
        tpp.outputDir = sys.argv[3]
        # if not outputDir.endswith("\\"):
        #     outputDir += "\\"
    print(tpp.moduleId + "<>" + tpp.inputDir + "<>" + tpp.outputDir)

    print('Reading config file')
    tpp.config_read()

    #  while we do not get a STOP or have a non-successful read or write, (busy-wait) read an input file, write an output file
    while (status):
        print('main: going into read')
        readStatus = tpp.tpp_busy_read(tpp.inputDir)
        if readStatus.status == SUCCESS:
            print('main: read SUCCESS')
            from transformers_for_negation_and_scope_speculation import CueModel, ScopeModel

            cue_model = CueModel(full_finetuning=True, train=False,
                                 pretrained_model_path=MODEL_SAVE + "Cue_Detection2.pickle/")

            scp_model = ScopeModel(full_finetuning=True, train=False,
                                   pretrained_model_path=MODEL_SAVE + "Scope_Resolution_Augment2.pickle/")

            output = tpp.work(readStatus.input)
            writeStatus = tpp.tpp_write(output, tpp.outputDir)
            if writeStatus != SUCCESS:
                status = STOPPING
            else:
                print('main: write SUCCESS')
        else:
            print('main: read FAILURE')
            status = STOPPING
    print('TPP stopped')
