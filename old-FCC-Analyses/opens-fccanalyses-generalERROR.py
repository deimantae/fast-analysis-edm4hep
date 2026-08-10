import yaml
import re
from pathlib import Path
from argparse import ArgumentParser

# Define the operations on the dataframe
class Analysis:
    
    def __init__(self, cmdline_args):
        # Parse additional arguments
        # All command line arguments are provided in the `cmdline_arg`
        # dictionary and arguments after "--" are stored under "remaining" key.
        parser = ArgumentParser(
            description="Additional analysis arguments",
            usage="Provided after '--'")
        parser.add_argument("--parameters-file", required=True, type=str,
                            help="YAML file containing the variables.")
        self.ana_args, _ = parser.parse_known_args(cmdline_args["remaining"])

        # Run over the full statistics and save it to one output file named
        # <outputDir>/<process_name>.root
        self.process_list = {
                'p8_ee_ZZ_ecm240': {'fraction': 0.5}, #  statistics percent
                'p8_ee_WW_ecm240': {'fraction': 0.25},
                'p8_ee_ZH_ecm240': {'fraction': 0.2,}
        }
        self.output_format = 'rntuple'
        self.input_dir = "/eos/experiment/fcc/hh/tutorials/"\
            "edm4hep_tutorial_data/"
        self.output_dir = "outputs/opens-fccanalyses"
        self.test_file = "https://fccsw.web.cern.ch/fccsw/analysis/" \
                         "test-samples/edm4hep099/p8_ee_WW_ecm240_edm4hep.root"
        
        # Load variables from the YAML configuration file
        config_file = Path(__file__).parent / self.ana_args.parameters_file
        
        # Store YAML contents as a dictionary
        with open(config_file, "r") as file:
            self.variables = yaml.safe_load(file)
            
        # Parse the YAML
        self.output_variables = []
        self.definitions = []
        
        for collection_name, variable_list in self.variables.items():
            if variable_list is None:
                continue
        
            for variable in variable_list:
                if isinstance(variable, str):
                    variable_name = variable
                    expression = None
                elif isinstance(variable, dict):
                    for variable_name, expression in variable.items():
                        break
                else:
                    raise TypeError(
                        f"Unsupported variable definition: {variable!r}"
                    )
        
                output_name = f"{collection_name}_{variable_name}"
        
                self.definitions.append(
                    {
                        "collection": collection_name,
                        "variable": variable_name,
                        "expression": expression,
                        "output": output_name,
                    }
                )
        
                self.output_variables.append(output_name)
                    
    # Return the transformed RDataFrame
    def analyzers(self, dframe):
    
        for definition in self.definitions:
    
            collection_name = definition["collection"]
            variable_name = definition["variable"]
            expression = definition["expression"]
            output_name = definition["output"]
    
            if expression is None:
                expression = f"{collection_name}.{variable_name}"
            else:
                expression = expression.replace("np.", "")
    
                identifiers = set(
                    re.findall(r"\b[A-Za-z_]\w*\b", expression)
                )
    
                for identifier in identifiers:
                    if re.search(rf"\b{identifier}\s*\(", expression):
                        continue
    
                    expression = re.sub(
                        rf"\b{identifier}\b",
                        f"{collection_name}.{identifier}",
                        expression,
                    )
    
            dframe = dframe.Define(output_name, expression)
    
        return dframe
    
    # Return the list of branches to save 
    def output(self):
        return self.output_variables