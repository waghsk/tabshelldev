class Ont():
    def __init__(self, path_list=[]):
        self.path_list=path_list

    def get_concepts(self,query_path):
        return [x.split('/')[-1] for x in self.path_list if query_path in x]
    
    def get_level(self,level=1):
        return list(set(['/'.join(x.split('/')[0:level+1]) for x in self.path_list]))