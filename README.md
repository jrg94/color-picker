# color-picker

The PSO2 color picker is a command line tool for generating the
PSO2 color palette given some RGB value. Currently, this is a toy
project that works as follows:

1. Install the color-picker tool: `pip install pso2-color-picker`
2. Execute the color-picker tool: `color-picker`
3. Follow the prompts
    1. "Please provide file name (include .png)": [insert name of output file (e.g. nagatoro-hair.png)]
    2. "Please enter a color as comma-separated RGB" [insert color (e.g. 123, 234, 12)]
    
If done correctly, a window should pop up with an image like the following:

![Sample Green](https://raw.githubusercontent.com/jrg94/color-picker/master/samples/tomo.png)

Likewise, a file will be saved at the location you ran the script with the
file name you provided in Step 3i. 

Let us know if you like it! Given enough community support, we would be happy to 
extend this tool to be more user-friendly.
