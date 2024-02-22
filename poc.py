import yaml

class BuildNotesMerger:
    def __init__(self):
        self.target_tag = ""
        self.primary_build_dict = None
        remote_repo = PLAYOUT_GIT_DEFAULTS_MAP[local_default_file][0]
        remote_path = PLAYOUT_GIT_DEFAULTS_MAP[local_default_file][1]
        release_name = PLAYOUT_GIT_DEFAULTS_MAP[local_default_file][2]
        release_changes_map = self.input_json
        local_download_location = os.path.join(PLAYOUT_DEFAULTS_FOLDER, local_default_file)
        if release_name in release_changes_map.keys() and not self.is_config_downloaded[local_default_file]:
            git_tag = release_data["dockerImages"][release_name].split(":")[1]
            cmnd = f'curl  \
                    -u "{self.git_user_name}:{self.git_password}" \
                    -H "Accept: application/vnd.github.v4.raw" \
                    -o {local_download_location} \
                    -L https://api.github.com/repos/amagimedia/{remote_repo}/contents/{remote_path}?ref={git_tag}'

            retVal, retStr = self.__execute(cmnd)
        

def merge_yaml(yaml1_path, yaml2_path, output_path):
    # Load YAML data from the first file
    with open(yaml1_path, 'r') as f1:
        yaml1_data = yaml.safe_load(f1)

    # Load YAML data from the second file
    with open(yaml2_path, 'r') as f2:
        yaml2_data = yaml.safe_load(f2)

    



# Paths to the YAML files
yaml1_path = "1.yaml"
yaml2_path = "2.yaml"
output_path = "merged_yaml.yml"

# Merge the YAML files
merge_yaml(yaml1_path, yaml2_path, output_path)
