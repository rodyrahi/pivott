with open(self.projectpath, 'r') as file:
            jsonfile = json.load(file)

        
        jsonfile["data_path"] = file_path
        with open(self.projectpath, 'w') as file:
            json.dump(jsonfile, file, indent=4) 