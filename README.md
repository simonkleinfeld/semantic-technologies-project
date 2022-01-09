# Question understanding interface
This repository contains code for the project of the course SE Research Seminar: Semantic Technology at the University of Innsbruck during the winter term 2021.

A user interface is offered in which one can choose from a list of questions. Subsequently, a sub-graph (in the environment of the question) of a knowledg graph can be displayed, or a question graph can be generated for this question. This question graph can be exported.

## Technical aspects:
* Programming language: Python
* UI Framework/Graph Framework: Dash-Plotly, Bootstrap components for plotly
* NLP Framework: spacy

## How to use
1. Install the requirements using the requirements.txt file
2. Start the app.py file in the layout folder (tested with python 3.9)
3. Open the displayed url in your webbrowser (probably http://127.0.0.1:8050/ tested with chrome and firefox)
4. Select one of the questions using the select item in the middle of the screen
   1. Use the "Open knowledge graph" button to display the subset of the knowledge graph around this question
   2. Use the "Open question graph" button for generating a question graph
      1. Using the items above the question graph it is possible to edit the question graph
      2. Export the question graph to the local file system using the export button
   3. Visualize the export using the "View export" button
      1. Choose one of the .nxhd exports with the select item in the upper part of the appearing modal layout
5. If you have any issues, have a look on the help menu using the "?" button

## Team members
Marco Salchner, Manuel Buchauer, Simon Kleinfeld

## Responsibilities
* Marco Salchner: Generating and export of the question graph
* Simon Kleinfeld: Frontend layout
* Manuel Buchauer: Paper