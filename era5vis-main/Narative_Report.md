# Jakob Werkgarner

**Assigned task**  
My task was to create the ERA5 cross-section plotting, including deviations (anomalies) from the climatological mean and plotting of the case file on pressure levels. I also added the call to my function in `cli.py` and made sure that `build_html.py` works correctly. In addition, I created the model climatology and the model topography from the ERA5 surface data. (The code is basically just resampling and computing the terrain height / g, so it is not included here.)

**Changes and outcome**  
During the implementation I added plotting routines for anomalies, climatological background fields, and terrain masking to improve readability. Wind arrows were implemented; although they are not used now, they can be used later on if the project is developed further. The rest basically went as planned, except that the output of the plotting function is not a Matplotlib figure anymore but now a path pointing to the created PNG for the HTML creation.

**Biggest challenge in implementation**  
The biggest challenge was finding a workflow that works with the files of the others. Different programming styles, mostly learned in a hands-on way, made the code inconsistent and harder to combine.

**Biggest challenge when merging**  
Since I followed Simon’s structure (especially for output handling), merging was not a major problem. However, after feedback, integrating `plot_crosssection` into `graphics.py` and separating helper functions caused some issues with shared variables and scripts called from the terminal, which required some debugging.


-----------------------------

# Kilian Trummer

**Assigned task and changes**  
My initial task was to implement the API and the new CLI commands and to verify their correct setup through testing. In the end my additianal task was the proper integration of the model_climate dataset and for writing suitable test cases to ensure its correct functionality.

**Changes and outcome**
My biggest challenge was the implementation of the download function for the model_climate data. It took some time to understand how the UIBK fileshare platform could be used as an automated download source. With the help of ChatGPT, I was finally able to implement a solution, which should work reliably. Although I was already close to a correct implementation, the AI support significantly reduced the debugging time, as the main issue was not located in the code itself but in the structure of the download link.

**Biggest challenge in implementation**
Another major challenge occurred for me during the code merging. In some cases, the code ran without issues on other computers but failed on mine. I pin pointed this mainly to differences in operating systems and local folder structures, even though we all worked within the same Git repository. Additionally, while the .gitignore file was very helpful in avoiding the upload of large .nc files, it occasionally led to inconsistencies in the initial setup, particularly regarding the era5_model_height.nc and model_clim.nc files.
The main takeaway from this project is the importance of writing proper test cases early in the  process of building a shared project and running them regularly, rather than only at the end. This helps ensure that all team members work with a consistent initial setup and reduces the risk of incorrect implementations when adding new features.
