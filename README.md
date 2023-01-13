# negbert + TPP intergration

Negation detection with BERT

### Please firstly install packages for running NegBERT:

- install ```pytorch```: the compatibility of pytorch is as tricky as always. 
Please [check your CUDA version first](https://stackoverflow.com/questions/9727688/how-to-get-the-cuda-version), 
and use the command that correspondes to your CUDA version on [this page](https://pytorch.org/get-started/previous-versions/) 
provided by PyTorch official. ```pytorch 1.12.1``` has been tested, so versions that are lower than that should be working fine.

- Install other packaeges using ```requirements.txt``` provided in this folder: ```pip install -r requirements.txt```

- Go to ```config.py```, and fill in the value of ```MODEL_SAVE``` with the path where the models were saved. 
Please notice this path should not contain the name of the models. 
The models usually have two parts: a ```.bin``` file and ```config.json```. 
For example, if these two files have the following absolute path: ```path/to/examples/model1/mode.bin``` 
and ```path/to/examples/model1/config.json```, then the value of ```MODEL_SAVE``` should be ```path/to/examples/```

- Now you can run TPP as normal

- Tested on Windows 10 pro and Ubuntu 20.04 LTS
