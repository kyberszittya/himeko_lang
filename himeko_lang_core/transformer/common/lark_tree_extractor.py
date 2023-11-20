from lang.himeko_meta_parser import Tree


class LarkElementMetaHimekoExtractor(object):

    @staticmethod
    def get_element_name(t: Tree):
        if "hi_element_signature" in set(map(lambda x: x.data, t.children)):
            return next(next(filter(
                lambda x: x.data == "hi_element_signature", t.children)).find_data("element_name")).children[0]
        return next(t.find_data("element_name")).children[0]

    @staticmethod
    def search_for_string_element(t: Tree) -> str:
        r = next(t.find_data("string"))
        return str(r.children[0]).replace("\"","")

