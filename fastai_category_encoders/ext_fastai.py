import pandas as pd

from fastai.tabular.data import TabularProc, TabularPandas

from .base import CategoryEncoder
from .ext_autoembedder import AutoEmbedderCategoryEncoder
from .ext_fasttext import FastTextCategoryEncoder
from .ext_category_encoders import LibraryCategoryEncoder


class CategoryEncode(TabularProc):
    """
    Wraps a `CategoryEncoder` with a Fastai `TabularProc` to perform
    categorical feature encoding seamlessly.
    """

    def __init__(self, strategy: str, **kwargs):
        self.strategy = strategy
        self._kwargs = kwargs
        self.encoder: CategoryEncoder = None

    def setups(self, to: TabularPandas) -> None:
        """Saves training set categories and trains the embedding model."""
        if self.strategy == "fasttext":
            self.encoder = FastTextCategoryEncoder(
                to.cat_names, to.cont_names, **self._kwargs
            )
        elif self.strategy == "autoembedder":
            self.encoder = AutoEmbedderCategoryEncoder(to.cat_names, to.cont_names)
        else:
            self.encoder = LibraryCategoryEncoder(
                to.cat_names, to.cont_names, self.strategy
            )
        self.to = to
        self.encoder.fit_transform(self.__to_dataframe(to))

    def encodes(self, to: TabularPandas) -> TabularPandas:
        encoded_cats = self.encoder.transform(self.__to_dataframe(to))
        encoded_features = self.encoder.get_feature_names()
        to[encoded_features] = encoded_cats
        to.cat_names = []

    def decodes(self, to: TabularPandas) -> TabularPandas:
        encoded_features = self.encoder.get_feature_names()
        decoded_cats = self.encoder.inverse_transform(to[encoded_features])
        to[self.encoder.cat_names] = decoded_cats.copy()
        to.cont_names = self.encoder.cont_names.copy()
        return to

    def __to_dataframe(self, to: TabularPandas) -> pd.DataFrame:
        return pd.concat([to.conts, to.cats], axis=1)
