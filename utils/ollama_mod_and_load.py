import logging
from ollama import list, show, create
from langchain_community.llms import Ollama

def ollama_mod_and_load(model, num_ctx = None):
    """
    Retrieves or creates a crewai model based on the specified base model name.
    :param model_name: The base name of the model to check or modify, potentially with a version.
    :return: An instance of the LLM model from Ollama.
    """
    model_name=model
    #TODO: Save models with crewia and mun_ctx suffix so no ned to create modelfile all the time
    #existing_models = [model['name'] for model in list()['models']]
    
    # Split the model name into base and version if it contains ':'
    if ':' in model_name:
        base_model_name, version = model_name.split(':')
    else:
        base_model_name, version = model_name, None

    # Construct the crewai model name depending on whether a version was specified
    crewai_model_name = f"{base_model_name}_crewai"
    if version:
        crewai_model_name += f":{version}"

    # Check if the crewai version of the model already exists
    # if crewai_model_name in existing_models:
    #     logging.info(f"Model '{crewai_model_name}' found, loading directly.")
    #     return Ollama(model=crewai_model_name)

    # Get details of the base model
    model_details = show(model_name)
    modelfile = model_details['modelfile']

    # Check if the PARAMETER stop "\nObservation" and num_ctx exists with the right context size
    if r'\\nObservation' in modelfile and f"PARAMETER num_ctx {num_ctx} in modelfile": 
        logging.info(f"Parameter stop '\\nObservation' exists in '{model_name}', loading model.")
        return Ollama(model=model_name)
    
    updated_modelfile = modelfile.rstrip() + "\n" + 'PARAMETER stop ' + r"\nObservation"
    if num_ctx:
        # Remove any existing 'PARAMETER num_ctx' line from modelfile
        updated_modelfile = '\n'.join(line for line in modelfile.split('\n') if not line.strip().startswith('PARAMETER num_ctx'))
        updated_modelfile = updated_modelfile + f"\nPARAMETER num_ctx {num_ctx}"
    
    logging.info(f"Creating new model '{crewai_model_name}' with updated stop parameter.")
    for response in create(model=crewai_model_name, modelfile=updated_modelfile, stream=True):
        print(response['status']) 
    return Ollama(model=crewai_model_name)

if __name__ == "__main__":
    #Test
    test_model_name = "phi:latest"
    model = ollama_mod_and_load(test_model_name)
    print(f"Model loaded or created: {model}")
