# Evaluation Framework for Network Tariffs (EFf-NeTs)
The **E**valuation **F**ramework **f**or **Ne**twork **T**ariff**s** (EFf-NeTs) is a 
framework that rates different alternatives of network tariffs according to the 
following criteria:
* Efficient grid (= cost-reflection),
* Fairness and customer acceptance,
* Expansion of DER,
* Efficient electricity usage.

It therefore requires certain input parameters, that have to be generated previous to 
the execution of the framework. 

The indicators and logic behind can be found in the publication: 
A. Heider, J. Huber, Y. Farhat, Y. Hertig and G. Hug, _How to choose
a suitable network tariff? - Evaluating network tariffs under increasing
integration of distributed energy resources_, Energy Policy, Vol. 188, 2024,
DOI: 10.1016/j.enpol.2024.114050. Please also cite the paper when using this framework.
The branch _published_version_energy_policy_ is a stored version of the code and data 
that was used in the published paper.


## Usage Details

### Downloading the code

You can download the code by performing:

    git clone https://github.com/AnyaHe/EFf-NeTs.git

in your command line. All required packages should usually be already installed in your 
base environment if you use python regularly.

### Applying the framework
If you want to apply the framework to your own case study, please adapt the input data 
and then execute the file _run_analysis.py_. Files that need to be updated are:
* inputdata_new.xlsx
* cost_contribution_ur.csv
* pv_cost_reduction.csv
* expert_weighting.py (optional)

The file _cost_contribution_ur.csv_ can be automatically updated using the 
_data_preparation.py_ script. If additional or different weights should be used, please 
also adapt the weightings in the _expert_weighting.py_ file.

### Adapting the framework
If you want to refine the existing indicators or add new indicators, please adapt the 
_indicators.py_ file. Feel free to propose changes and get into contact with us. The 
framework is meant as a basis for discussion and further development and will benefit 
from your feedback.
