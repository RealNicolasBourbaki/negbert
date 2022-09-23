SENT_FILE = ""  # the file with all the sentences from which you want to detect negations
CUES_PRED = ""  # file path where you store all the cues
SCOPE_PRED = ""  # file path where you store all the scopes
MODEL_SAVE = "" # root path where you store all the models
BERT_CONFIG = "models/cue_config.json"
XNET_CONFIG = "models/xnet_config.json"

# datasets directories declairation
SHERLOCK_TRAIN = "dataset/SEM-2012-SharedTask-CD-SCO-training.txt"
SHERLOCK_DEV = "dataset/SEM-2012-SharedTask-CD-SCO-dev.txt"
SHERLOCK_TEST_CARDBOARD = "dataset/SEM-2012-SharedTask-CD-SCO-test-cardboard-GOLD.txt"
SHERLOCK_TEST_CIRCLE = "dataset/SEM-2012-SharedTask-CD-SCO-test-circle-GOLD.txt"