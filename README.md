# Question understanding interface
This repository contains code for the project of the course SE Research Seminar: Semantic Technology at the University of Innsbruck during the winter term 2021.

An UI with an input field for a question is provided. Below this input field following features are provided:

* List all named entities
* Display a dependency graph 
* Show sub-graph of an RDF graph around topic entity of question
* Build a question graph and allow user modifications of it
* Do graph matching with the question graph over the RDF graph either as done in gAnswer or similiar approaches or our own
* Display top-k matching subgraphs 
* Optional: Make top-k matching subgraphs interactable
* Optional: Form natural language answer from top-k matching subgraphs
* Optional: Support multiple forms of RDF graphs

Technical aspects:
* Programming language: Python
* UI Framework/Graph Framework: Dash-Plotly
* NLP Framework: spacy or stanza
