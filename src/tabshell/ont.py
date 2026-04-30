class Ont():
    def __init__(self, path_list=[]):
        self.path_list=path_list

    def get_concepts(self,query_path):
        return [x.split('/')[-1] for x in self.path_list if query_path in x]