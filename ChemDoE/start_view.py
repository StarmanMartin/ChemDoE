from chemotion_api import Instance

from ChemDoE.element_tree_page import ElementTreePage
from ChemDoE.new_reaction import NewReaction


class StartPage(ElementTreePage):
    def __init__(self):
        super().__init__('Reaction')
        self._new_reaction = None


    def create_new(self, collection):
        self._new_reaction = NewReaction(collection)
        self.page_manager.set_page(self._new_reaction)


    def select_element(self, collection, reaction):
        self._new_reaction = NewReaction(collection, reaction)
        self.page_manager.set_page(self._new_reaction)