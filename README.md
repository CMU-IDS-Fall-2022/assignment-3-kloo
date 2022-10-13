# CMU Interactive Data Science Assigment 3

* **Team members**: ipk@andrew.cmu.edu 
* **Online URL**: https://cmu-ids-fall-2022-assignment-3-kloo-streamlit-app-vphgy2.streamlitapp.com/

## Project Overview

This repository contains a streamlit app and the supporting files, including a data generating script.  This project gives users a unique way to explore Penguins NHL game data, allowing simultaneous exploration across time, space, and context.  For a full description of the project, see writeup.md.

## File Descriptions

- data
        - full_data.csv = stacked dataframe containing events from NHL games
        - win_prob.csv = dataframe containing a row for every minute for all penguins games between 2016 and 2022.  Each minute has the penguins' win probability.
- www
        - nite.wav = an audio sample from famed penguins radio announcer Mike Lang
        - pens_log.png = the penguins (best version of their) logo
        - screenshot.png = a screenshot of the app used in the write up (writeup.md)
- LICENSE = license information
- prepare_data.py = script for generating all data used in this app.  Source is the NHL's undocumented API.
- README.md = generates this document.
- requirements.txt = all packages needed to run the app
- streamlit_app.py = streamlit app
- writeup.md = a description of the project

## Deliverables

- [x] An interactive data science or machine learning application using Streamlit.
- [x] The URL at the top of this readme needs to point to your Streamlit application online. The application should also list the names of the team members. 
- [x] A write-up that describes the goals of your application, justifies design decisions, and gives an overview of your development process. Use the `writeup.md` file in this repository. You may add more sections to the document than the template has right now.
