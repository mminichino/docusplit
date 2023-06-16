##

import json
import xmltodict
import logging
import pandas as pd
from typing import Union

logger = logging.getLogger('docusplit')
logger.addHandler(logging.NullHandler())


class DocuSplit(object):

    def __init__(self, data: bytes, start_depth: int = 0):
        logger.debug(f"DocuSplit Initialize {len(data)} data bytes start depth {start_depth}")
        self.data = data
        self.depth = start_depth

    def dump_stats(self, verbose: bool = False):
        data_dict = xmltodict.parse(self.data)
        p_data = self.get_depth(data_dict, self.depth)
        self.analyze(p_data, verbose)

    def dump_to_json(self, indent: bool = False):
        data_dict = xmltodict.parse(self.data)
        p_data = self.get_depth(data_dict, self.depth)
        if indent:
            print(json.dumps(p_data, indent=2))
        else:
            print(json.dumps(p_data))

    def dump_flattened_json(self):
        data_dict = xmltodict.parse(self.data)
        p_data = self.get_depth(data_dict, self.depth)
        df = pd.json_normalize(p_data)
        print(df.to_json())

    def split_path(self, data: dict, keys: list):
        for k, v in data.items():
            if k == keys[-1]:
                return data
            else:
                return self.split_path(data[keys[0]], keys[1:])

    def omit_path(self, data: dict, keys: list):
        d = data.copy()
        for k in d.keys():
            if k in keys:
                del data[k]
            if type(d[k]) == dict:
                self.omit_path(data[k], keys)
            if type(d[k]) == list:
                for e in d[k]:
                    self.omit_path(e, keys)
        return data

    def split_path_list(self, data: Union[dict, list], keys: list, index: int):
        if type(data) == list and keys[0] == "[]":
            return self.split_path_list(data[index], keys[1:], index)
        else:
            for k, v in data.items():
                if k == keys[-1]:
                    return data
                else:
                    return self.split_path_list(data[keys[0]], keys[1:], index)

    def get_data_sets(self, data: dict, keys: list):
        if type(data) == list and keys[0] == "[]":
            return len(data)
        elif len(keys) == 1:
            return 1
        else:
            return self.get_data_sets(data[keys[0]], keys[1:])

    def split_sub_doc_list(self, base: str, directory: str, key: str):
        main = {}
        superset = []
        keys = key.split('.')
        data_dict = xmltodict.parse(self.data)
        p_data = self.get_depth(data_dict, self.depth)
        for k, v in p_data.items():
            print(f"Analyzing key {k}")
            if k == keys[0]:
                max_len = self.get_data_sets({k: v}, keys)
                for c in range(max_len):
                    extract_list = []
                    extract = self.split_path_list({k: v}, keys, c)
                    for item in extract[keys[-1]]:
                        extract_list.append(item)
                    superset.append(extract_list)
                main.update(self.omit_path({k: v}, [keys[-1]]))
            else:
                main.update({k: v})

        filename = f"{directory}/{base}-main.json"
        with open(filename, mode="w") as output_file:
            json.dump(main, output_file)
            output_file.write("\n")

        for x, extract_list in enumerate(superset):
            for n, item in enumerate(extract_list):
                filename = f"{directory}/{base}-ext-{x}-{n}.json"
                with open(filename, mode="w") as output_file:
                    json.dump(item, output_file)
                    output_file.write("\n")

    def split_sub_doc(self, base: str, directory: str, key: str):
        main = {}
        extract = {}
        keys = key.split('.')
        data_dict = xmltodict.parse(self.data)
        p_data = self.get_depth(data_dict, self.depth)
        for k, v in p_data.items():
            print(f"Analyzing key {k}")
            if k == keys[0]:
                extract.update(self.split_path({k: v}, keys))
                main.update(self.omit_path({k: v}, [keys[-1]]))
            else:
                main.update({k: v})

        filename = f"{directory}/{base}-main.json"
        with open(filename, mode="w") as output_file:
            json.dump(main, output_file)
            output_file.write("\n")

        filename = f"{directory}/{base}-ext.json"
        with open(filename, mode="w") as output_file:
            json.dump(extract, output_file)
            output_file.write("\n")

    def split_json(self, base: str, directory: str):
        n = 4
        c = 1
        data_dict = xmltodict.parse(self.data)
        p_data = self.get_depth(data_dict, self.depth)
        df = pd.DataFrame.from_dict(p_data)
        # list_df = [df[i:i + n] for i in range(0, len(df), n)]
        k, m = divmod(len(df), n)
        list_df = list(df[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))
        for e in list_df:
            filename = f"{directory}/{base}-{c}.json"
            c += 1
            with open(filename, mode="w") as output_file:
                output_file.write(e.to_json())
                output_file.write("\n")

    def analyze(self, data: dict, verbose: bool = False):
        # print(json.dumps(data))
        size = 0
        for element in data:
            e_size = self.get_size(data[element])
            print(f"Key: {element} Type: {type(data[element])} Size: {e_size}")
            size += e_size
        print(f"Total size: {size}")

        self.walk_layout(data, verbose=verbose)

    def walk_layout(self, data: dict, prefix: list = None, verbose: bool = False):
        path = prefix if prefix else []
        for k, v in data.items():
            path.append(k)
            if type(v) == dict:
                self.walk_layout(v, path, verbose)
            elif verbose and type(v) == list:
                for n, item in enumerate(v):
                    path.append(f"[{n}]")
                    self.walk_layout(item, path, verbose)
                    path.pop()
            else:
                if type(v) == str:
                    suffix = f"String[{len(v)}] Size: {self.get_size(v)}"
                elif type(v) == list:
                    suffix = f"List[{len(v)}] Size: {self.get_size(v)}"
                else:
                    suffix = f"Data[{len(v)}] Size: {self.get_size(v)}"
                print(f"{'.'.join(path)} {suffix}")
            path.pop()

    def get_size(self, data):
        size = 0
        if type(data) == dict:
            for item in data:
                size += self.get_size(data[item]) + len(item)
        elif type(data) == list:
            for item in data:
                size += self.get_size(item)
        elif data is not None:
            size += len(data)
        return size

    def get_depth(self, data: dict, depth: int) -> dict:
        if depth == 0:
            return data
        else:
            for key in data:
                if type(data[key]) == dict:
                    return self.get_depth(data[key], depth - 1)
