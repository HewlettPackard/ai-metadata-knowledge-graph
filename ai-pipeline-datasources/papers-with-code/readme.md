### Papers-with-code
This folder consists of scripts that collects data from papers-with-code API and crawls the taxonomy information using web scraping


* collect_all_papers.py - collects papers and the ids of task, dataset, methods, evaluations associated with papers

* collect_data.py - collects the detailed information of datasets, methods, evaluations and results. This is the main file from where main functions of collect_all_papers.py and tasks.py is called.

* tasks.py - collects the detailed information of tasks such as task children, task parent and task area id. Hence written as separate script.

* crawl_taxomony.py - uses BeautifulSoup to crawl the taxonomy from https://paperswithcode.com/sota

* archive folder consists of all the old scripts

* All the collected data is stored at - /home/venkatre/kg_recommender/data  and a accessible copy for the team is backed up at: /lustre/data/dataspaces/k-cmf

* to_csv folder consists of scripts that will convert json files obtained through the API calls to csv files in compliance with the papers-wtih-code Graph Data Model. The scripts to convert the data suitable to Metadata KG will be found at hpe/ai-pipeline-knowledge-graph/kg-data-prep