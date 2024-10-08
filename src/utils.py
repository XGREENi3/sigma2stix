import os
import shutil
import uuid
import json
import yaml
import hashlib
import requests
import re
from git import Repo
from typing import List
from src import config
from stix2 import Bundle
from stix2 import Filter


def clone_github_repository(repo_url, destination_path, tag_name):
    try:
        repo = Repo.clone_from(repo_url, destination_path, branch=tag_name)
        print(f"Repository cloned successfully to {destination_path}")
    except Exception as e:
        print(f"Failed to clone repository: {e}")


def check_dir(dir:str):
    if not os.path.exists(dir):
        os.makedirs(dir)


def delete_files_and_folders_except_rules(prefix='rules', keep_count=2):
    directory_path = 'data'
    all_items = os.listdir(directory_path)
    rules_folders = [item for item in all_items if item.startswith(prefix)]
    rules_folders.sort()
    folders_to_keep = rules_folders[:keep_count]
    for item in all_items:
        item_path = os.path.join(directory_path, item)
        if os.path.isdir(item_path) and not item.startswith(prefix):
            try:
                if item not in folders_to_keep:
                    shutil.rmtree(item_path)
                    print(f"Deleted: {item_path}")
            except:
                pass
        elif os.path.isfile(item_path):
            if not item.startswith(prefix):
                os.remove(item_path)


def get_all_yaml_files(folder="data"):
    file_with_path = []
    for root, dirs, files in list(os.walk(folder)):
        if ".git" in root:
            continue
        yaml_files = []
        for file in files:
            if file.endswith('.yml') or file.endswith('.yaml'):
                file_path = os.path.join(root, file)
                yaml_files.append(file_path)
        if len(yaml_files)>1:
            file_with_path.append({root:yaml_files})
    return file_with_path

def escape_special_characters(content):
    # Replace problematic special characters with an escaped version
    return re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F\xAD\u0378\u0379\u0380-\u0383\u038B\u038D\u03A2\u0530\u0560\u0588\u058B\u058C\u058E\u058F\u0590\u05C8\u05C9\u05EC\u05ED\u05F5\u05F6\u05F8\u05F9\u0600\u0604\u0605\u061C\u061D\u070E\u070F\u074B\u074C\u07B2-\u07BF\u07FB\u07FC\u082E\u082F\u083F\u085C\u085D\u085F-\u089F\u08A1\u08AD\u08E4\u08E5\u08E8-\u08EF\u08F2-\u08FF\u0978\u0980\u0984\u098D\u098E\u0991\u0992\u09A9\u09B1\u09B3\u09B5\u09BA\u09BB\u09C5\u09C6\u09C9\u09CA\u09CF\u09D0\u09D8\u09DB\u09DE\u09E4\u09E5\u09FC-\u0A00\u0A04\u0A0B-\u0A0E\u0A11\u0A12\u0A29\u0A31\u0A34\u0A37\u0A3A\u0A3B\u0A3D\u0A43-\u0A46\u0A49\u0A4A\u0A4E\u0A50\u0A52-\u0A58\u0A5D\u0A5F-\u0A65\u0A76-\u0A80\u0A84\u0A8E\u0A92\u0AA9\u0AB1\u0AB4\u0ABA\u0ABB\u0AC6\u0ACA\u0ACE\u0ACF\u0AD1-\u0ADF\u0AE4\u0AE5\u0AF2\u0AF4-\u0B00\u0B04\u0B0D\u0B0E\u0B11\u0B12\u0B29\u0B31\u0B34\u0B3A\u0B3B\u0B45\u0B46\u0B49\u0B4A\u0B4E\u0B55\u0B58\u0B5B\u0B5E\u0B64\u0B65\u0B78-\u0B81\u0B84\u0B8B\u0B8D\u0B91\u0B96-\u0B98\u0B9B\u0B9D\u0BA0\u0BA2\u0BA5\u0BA7\u0BAB\u0BAC\u0BB6\u0BBA-\u0BBD\u0BC3\u0BC5\u0BC9\u0BCE\u0BCF\u0BD1-\u0BD6\u0BD8-\u0BE5\u0BFB-\u0C00\u0C04\u0C0D\u0C11\u0C29\u0C34\u0C3A\u0C3B\u0C45\u0C49\u0C4E\u0C54\u0C57\u0C5B\u0C5E\u0C64\u0C65\u0C70\u0C71\u0C75\u0C80\u0C81\u0C84\u0C8D\u0C91\u0CA9\u0CB4\u0CBA\u0CBB\u0CC5\u0CC9\u0CCE\u0CD4\u0CD7-\u0CDD\u0CDF\u0CE4\u0CE5\u0CF0\u0CF3\u0D04\u0D0D\u0D11\u0D3B\u0D3C\u0D45\u0D49\u0D4F\u0D56\u0D58-\u0D5F\u0D64\u0D65\u0D76-\u0D78\u0D80\u0D81\u0D84\u0D97-\u0D99\u0DB2\u0DBC\u0DBE\u0DBF\u0DC7-\u0DC9\u0DCB-\u0DCE\u0DD5\u0DD7\u0DE0-\u0DF1\u0DF5-\u0E00\u0E3B\u0E3C\u0E45\u0E4F\u0E5A\u0E5B\u0E83\u0E85\u0E86\u0E89\u0E8B\u0E8C\u0E8E-\u0E93\u0E98\u0EA0\u0EA4\u0EA6\u0EA8\u0EA9\u0EAC\u0EBA\u0EBE\u0EBF\u0EC5\u0EC7\u0ECE\u0ECF\u0EDA\u0EDB\u0EE0-\u0EFF\u0F48\u0F6D-\u0F70\u0F98\u0FBD\u0FCD\u0FDB-\u0FFF\u10C6\u10C8\u10C9\u10CC\u10CE\u10CF\u1249\u124E\u124F\u1257\u1259\u125E\u125F\u1289\u128E\u128F\u12B1\u12B6\u12B7\u12BF\u12C1\u12C6\u12C7\u12D7\u1311\u1316\u1317\u135B\u135C\u137D\u139A-\u139F\u13F5-\u13FF\u169D-\u169F\u16F1-\u16FF\u170D\u1715-\u171F\u1737-\u173F\u1754-\u175F\u176D\u1771\u1774-\u177F\u17DE\u17DF\u17EA-\u17EF\u17FA-\u17FF\u180F\u181A-\u181F\u1878-\u187F\u18AB-\u18AF\u18F6-\u18FF\u191D-\u191F\u192C-\u192F\u193C-\u193F\u1941-\u1943\u196E\u196F\u1975-\u197F\u19AC-\u19AF\u19CA-\u19CF\u19DB-\u19DD\u1A1C\u1A1D\u1A5F\u1A7D\u1A7E\u1A8A-\u1A8F\u1A9A-\u1A9F\u1AAE-\u1AFF\u1B4C-\u1B4F\u1B7D-\u1B7F\u1BF4-\u1BFB\u1C38-\u1C3A\u1C4A-\u1C4C\u1C80-\u1CBF\u1CC8-\u1CCF\u1CF7-\u1CFF\u1DE7-\u1DFB\u1E9C-\u1E9F\u1EFA-\u1EFF\u1F16\u1F17\u1F1E\u1F1F\u1F46\u1F47\u1F4E\u1F4F\u1F58\u1F5A\u1F5C\u1F5E\u1F7E\u1F7F\u1FB5\u1FC5\u1FD4\u1FD5\u1FDC\u1FF0\u1FF1\u1FF5\u1FFF\u200B-\u200F\u202A-\u202E\u2060-\u206F\u2072\u2073\u208F\u209D-\u209F\u20BB-\u20CF\u20F1-\u20FF\u218A\u218B\u23F4-\u23FF\u2427-\u243F\u244B-\u245F\u2B74-\u2B75\u2B96-\u2B97\u2BBA-\u2BBC\u2BC9-\u2BCF\u2BD2\u2BD3\u2BFE-\u2BFF\u2C2F\u2C5F\u2CF4-\u2CF8\u2D26\u2D28-\u2D2C\u2D2E\u2D2F\u2D68-\u2D6E\u2D71-\u2D7E\u2D97\u2D9F\u2DA7\u2DAF\u2DB7\u2DBF\u2DC7\u2DCF\u2DD7\u2DDF\u2E3C-\u2E7F\u2E9A\u2EF4-\u2EFF\u2FD6-\u2FEF\u2FFC-\u2FFF\u3040\u3097\u3098\u3100-\u3104\u312E\u3130\u318F\u31BB-\u31BF\u31E4-\u31EF\u321F\u32FF\u4DB6-\u4DBF\u9FCD-\u9FFF\uA48D-\uA48F\uA4C7-\uA4CF\uA62C-\uA63F\uA698-\uA69E\uA6F8-\uA6FF\uA78F\uA794-\uA79F\uA7AB-\uA7F7\uA82C-\uA82F\uA83A-\uA83F\uA878-\uA87F\uA8C5-\uA8CD\uA8DA-\uA8DF\uA954-\uA95E\uA97D-\uA97F\uA9CE\uA9DA-\uA9DD\uA9E0-\uA9FF\uAA37-\uAA3F\uAA4E-\uAA4F\uAA5A\uAA5B\uAA7C-\uAA7F\uAAC3-\uAADA\uAAF7\uAB07\uAB08\uAB0F\uAB10\uAB17\uAB1F\uAB27\uAB2F\uAB6C-\uAB6F\uABEE\uABEF\uABFA-\uABFF\uD7A4-\uD7AF\uD7C7-\uD7CA\uD7FC-\uD7FF\uFA6E\uFA6F\uFADA-\uFAFF\uFB07\uFB12\uFB18-\uFB1C\uFB37\uFB3D\uFB3F\uFB42\uFB45\uFBC3\uFBC4\uFBCB-\uFBCC\uFBEA-\uFBFB\uFE10\uFE16\uFE17\uFE1A-\uFE1F\uFE27-\uFE2F\uFE53\uFE67\uFE6C-\uFE6F\uFE75\uFEFD\uFF00\uFFBF-\uFFC1\uFFC8\uFFC9\uFFD0\uFFD1\uFFD8\uFFD9\uFFDD\uFFDE\uFFE7\uFFEF-\uFFFB]', '', content)

def read_yaml_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            content = escape_special_characters(content)
            yaml_data = yaml.safe_load(content)
            return yaml_data
    except yaml.YAMLError as e:
        print(f"YAML error in file {file_path}: {e}")
    except Exception as e:
        print(f"Error reading YAML file {file_path}: {e}")
    return None



def generate_all_references(data:dict) -> List[dict]:
    return [
        {"source_name": "sigma-rule", "external_id": "reference", "description": reference}
        for reference in data.get("references", [])
    ]


def clean_filesystem(path):
    try:
        if os.path.isfile(path) or os.path.islink(path):
            os.unlink(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
    except Exception as e:
        print(e)
        pass

def append_data():
    results = []
    for root, _, files in os.walk(config.file_system_path):
        if ".git" in root:
            continue
        for filename in files:
            if filename.endswith(".json"):
                file_path = os.path.join(root, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        stix_object = json.load(file)
                        results.append(stix_object)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON in file {file_path}: {e}")
                except UnicodeDecodeError as e:
                    print(f"Encoding error in file {file_path}: {e}")
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")
    return results

def generate_md5_from_list(stix_objects: list) -> str:
    json_str = json.dumps(stix_objects, sort_keys=True).encode('utf-8')
    return hashlib.md5(json_str).hexdigest()


def store_in_bundle(stix_objects):
    bundle_id = "bundle--" + str(uuid.uuid5(
        config.namespace, generate_md5_from_list(stix_objects))
    )
    bundle_of_all_objects = Bundle(id=bundle_id, objects=stix_objects)
    stix_bundle_file = f"{config.file_system_path}/sigma-rule-bundle.json"
    with open(stix_bundle_file, "w") as f:
        f.write(json.dumps(json.loads(bundle_of_all_objects.serialize()), indent=4))


def load_file_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error loading JSON from {url}: {e}")
        return None


def get_data_from_fs(query:str):
    query = [Filter("type", "=", query)]
    return config.fs.query(query)
