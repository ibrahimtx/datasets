# Copyright 2020 The HuggingFace Datasets Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Lint as: python3
""" List and inspect datasets and metrics."""

from typing import Dict, List, Mapping, Optional, Sequence, Union

import huggingface_hub

from .download.download_config import DownloadConfig
from .download.download_manager import DownloadMode
from .download.streaming_download_manager import StreamingDownloadManager
from .info import DatasetInfo
from .load import (
    dataset_module_factory,
    extend_dataset_builder_for_streaming,
    import_main_class,
    load_dataset_builder,
    metric_module_factory,
)
from .utils.logging import get_logger
from .utils.version import Version


logger = get_logger(__name__)


class SplitsNotFoundError(ValueError):
    pass


def list_datasets(with_community_datasets=True, with_details=False):
    """List all the datasets scripts available on the Hugging Face Hub.

    Args:
        with_community_datasets (:obj:`bool`, optional, default ``True``): Include the community provided datasets.
        with_details (:obj:`bool`, optional, default ``False``): Return the full details on the datasets instead of only the short name.

    Example:

    ```py
    >>> from datasets import list_datasets
    >>> list_datasets()
    ['acronym_identification',
     'ade_corpus_v2',
     'adversarial_qa',
     'aeslc',
     'afrikaans_ner_corpus',
     'ag_news',
     ...
    ]
    ```
    """
    datasets = huggingface_hub.list_datasets(full=with_details)
    if not with_community_datasets:
        datasets = [dataset for dataset in datasets if "/" not in dataset.id]
    if not with_details:
        datasets = [dataset.id for dataset in datasets]
    return datasets


def list_metrics(with_community_metrics=True, with_details=False):
    """List all the metrics script available on the Hugging Face Hub.

    Args:
        with_community_metrics (:obj:`bool`, optional, default ``True``): Include the community provided metrics.
        with_details (:obj:`bool`, optional, default ``False``): Return the full details on the metrics instead of only the short name.

    Example:

    ```py
    >>> from datasets import list_metrics
    >>> list_metrics()
    ['accuracy',
     'bertscore',
     'bleu',
     'bleurt',
     'cer',
     'chrf',
     ...
    ]
    ```
    """
    metrics = huggingface_hub.list_metrics()
    if not with_community_metrics:
        metrics = [metric for metric in metrics if "/" not in metric.id]
    if not with_details:
        metrics = [metric.id for metric in metrics]
    return metrics


def inspect_dataset(path: str, local_path: str, download_config: Optional[DownloadConfig] = None, **download_kwargs):
    """
    Allow inspection/modification of a dataset script by copying on local drive at local_path.

    Args:
        path (`str`): Path to the dataset processing script with the dataset builder. Can be either:

            - a local path to processing script or the directory containing the script (if the script has the same name
                as the directory),
                e.g. ``'./dataset/squad'`` or ``'./dataset/squad/squad.py'``.
            - a dataset identifier on the Hugging Face Hub (list all available datasets and ids with [`list_datasets`])
                e.g. ``'squad'``, ``'glue'`` or ``'openai/webtext'``.
        local_path (`str`): Path to the local folder to copy the dataset script to.
        download_config ([`DownloadConfig`], *optional*): Specific download configuration parameters.
        **download_kwargs (additional keyword arguments): Optional arguments for [`DownloadConfig`] which will override
            the attributes of `download_config` if supplied.
    """
    dataset_module = dataset_module_factory(
        path, download_config=download_config, force_local_path=local_path, **download_kwargs
    )
    print(
        f"The processing script for dataset {path} can be inspected at {local_path}. "
        f"The main class is in {dataset_module.module_path}. "
        f"You can modify this processing script and use it with `datasets.load_dataset({local_path})`."
    )


def inspect_metric(path: str, local_path: str, download_config: Optional[DownloadConfig] = None, **download_kwargs):
    r"""
    Allow inspection/modification of a metric script by copying it on local drive at local_path.

    Args:
        path (``str``): path to the dataset processing script with the dataset builder. Can be either:

            - a local path to processing script or the directory containing the script (if the script has the same name as the directory),
                e.g. ``'./dataset/squad'`` or ``'./dataset/squad/squad.py'``
            - a dataset identifier on the Hugging Face Hub (list all available datasets and ids with ``datasets.list_datasets()``)
                e.g. ``'squad'``, ``'glue'`` or ``'openai/webtext'``
        local_path (``str``): path to the local folder to copy the datset script to.
        download_config (Optional ``datasets.DownloadConfig``): specific download configuration parameters.
        **download_kwargs (additional keyword arguments): optional attributes for DownloadConfig() which will override the attributes in download_config if supplied.
    """
    metric_module = metric_module_factory(
        path, download_config=download_config, force_local_path=local_path, **download_kwargs
    )
    print(
        f"The processing scripts for metric {path} can be inspected at {local_path}. "
        f"The main class is in {metric_module.module_path}. "
        f"You can modify this processing scripts and use it with `datasets.load_metric({local_path})`."
    )


def get_dataset_infos(
    path: str,
    data_files: Optional[Union[Dict, List, str]] = None,
    download_config: Optional[DownloadConfig] = None,
    download_mode: Optional[DownloadMode] = None,
    revision: Optional[Union[str, Version]] = None,
    use_auth_token: Optional[Union[bool, str]] = None,
    **config_kwargs,
):
    """Get the meta information about a dataset, returned as a dict mapping config name to DatasetInfoDict.

    Args:
        path (``str``): path to the dataset processing script with the dataset builder. Can be either:

            - a local path to processing script or the directory containing the script (if the script has the same name as the directory),
                e.g. ``'./dataset/squad'`` or ``'./dataset/squad/squad.py'``
            - a dataset identifier on the Hugging Face Hub (list all available datasets and ids with ``datasets.list_datasets()``)
                e.g. ``'squad'``, ``'glue'`` or ``'openai/webtext'``
        revision (Optional ``Union[str, datasets.Version]``):
            If specified, the dataset module will be loaded from the datasets repository at this version.
            By default:
            - it is set to the local version of the lib.
            - it will also try to load it from the master branch if it's not available at the local version of the lib.
            Specifying a version that is different from your local version of the lib might cause compatibility issues.
        download_config (:class:`DownloadConfig`, optional): Specific download configuration parameters.
        download_mode (:class:`DownloadMode`, default ``REUSE_DATASET_IF_EXISTS``): Download/generate mode.
        data_files (:obj:`Union[Dict, List, str]`, optional): Defining the data_files of the dataset configuration.
        use_auth_token (``str`` or :obj:`bool`, optional): Optional string or boolean to use as Bearer token for remote files on the Datasets Hub.
            If True, will get token from `"~/.huggingface"`.
        **config_kwargs (additional keyword arguments): optional attributes for builder class which will override the attributes if supplied.

    Example:

    ```py
    >>> from datasets import get_dataset_infos
    >>> get_dataset_infos('rotten_tomatoes')
    {'default': DatasetInfo(description="Movie Review Dataset.\nThis is a dataset of containing 5,331 positive and 5,331 negative processed\nsentences from Rotten Tomatoes movie reviews...), ...}
    ```
    """
    config_names = get_dataset_config_names(
        path=path,
        revision=revision,
        download_config=download_config,
        download_mode=download_mode,
        data_files=data_files,
    )
    return {
        config_name: get_dataset_config_info(
            path=path,
            config_name=config_name,
            data_files=data_files,
            download_config=download_config,
            download_mode=download_mode,
            revision=revision,
            use_auth_token=use_auth_token,
            **config_kwargs,
        )
        for config_name in config_names
    }


def get_dataset_config_names(
    path: str,
    revision: Optional[Union[str, Version]] = None,
    download_config: Optional[DownloadConfig] = None,
    download_mode: Optional[DownloadMode] = None,
    force_local_path: Optional[str] = None,
    dynamic_modules_path: Optional[str] = None,
    data_files: Optional[Union[Dict, List, str]] = None,
    **download_kwargs,
):
    """Get the list of available config names for a particular dataset.

    Args:
        path (``str``): path to the dataset processing script with the dataset builder. Can be either:

            - a local path to processing script or the directory containing the script (if the script has the same name as the directory),
                e.g. ``'./dataset/squad'`` or ``'./dataset/squad/squad.py'``
            - a dataset identifier on the Hugging Face Hub (list all available datasets and ids with ``datasets.list_datasets()``)
                e.g. ``'squad'``, ``'glue'`` or ``'openai/webtext'``
        revision (Optional ``Union[str, datasets.Version]``):
            If specified, the dataset module will be loaded from the datasets repository at this version.
            By default:
            - it is set to the local version of the lib.
            - it will also try to load it from the master branch if it's not available at the local version of the lib.
            Specifying a version that is different from your local version of the lib might cause compatibility issues.
        download_config (:class:`DownloadConfig`, optional): Specific download configuration parameters.
        download_mode (:class:`DownloadMode`, default ``REUSE_DATASET_IF_EXISTS``): Download/generate mode.
        force_local_path (Optional str): Optional path to a local path to download and prepare the script to.
            Used to inspect or modify the script folder.
        dynamic_modules_path (Optional str, defaults to HF_MODULES_CACHE / "datasets_modules", i.e. ~/.cache/huggingface/modules/datasets_modules):
            Optional path to the directory in which the dynamic modules are saved. It must have been initialized with :obj:`init_dynamic_modules`.
            By default the datasets and metrics are stored inside the `datasets_modules` module.
        data_files (:obj:`Union[Dict, List, str]`, optional): Defining the data_files of the dataset configuration.
        **download_kwargs (additional keyword arguments): optional attributes for DownloadConfig() which will override the attributes in download_config if supplied,
            for example ``use_auth_token``

    Example:

    ```py
    >>> from datasets import get_dataset_config_names
    >>> get_dataset_config_names("glue")
    ['cola',
     'sst2',
     'mrpc',
     'qqp',
     'stsb',
     'mnli',
     'mnli_mismatched',
     'mnli_matched',
     'qnli',
     'rte',
     'wnli',
     'ax']
    ```
    """
    dataset_module = dataset_module_factory(
        path,
        revision=revision,
        download_config=download_config,
        download_mode=download_mode,
        force_local_path=force_local_path,
        dynamic_modules_path=dynamic_modules_path,
        data_files=data_files,
        **download_kwargs,
    )
    builder_cls = import_main_class(dataset_module.module_path)
    return list(builder_cls.builder_configs.keys()) or [dataset_module.builder_kwargs.get("config_name", "default")]


def get_dataset_config_info(
    path: str,
    config_name: Optional[str] = None,
    data_files: Optional[Union[str, Sequence[str], Mapping[str, Union[str, Sequence[str]]]]] = None,
    download_config: Optional[DownloadConfig] = None,
    download_mode: Optional[DownloadMode] = None,
    revision: Optional[Union[str, Version]] = None,
    use_auth_token: Optional[Union[bool, str]] = None,
    **config_kwargs,
) -> DatasetInfo:
    """Get the meta information (DatasetInfo) about a dataset for a particular config

    Args:
        path (``str``): path to the dataset processing script with the dataset builder. Can be either:

            - a local path to processing script or the directory containing the script (if the script has the same name as the directory),
                e.g. ``'./dataset/squad'`` or ``'./dataset/squad/squad.py'``
            - a dataset identifier on the Hugging Face Hub (list all available datasets and ids with ``datasets.list_datasets()``)
                e.g. ``'squad'``, ``'glue'`` or ``'openai/webtext'``
        config_name (:obj:`str`, optional): Defining the name of the dataset configuration.
        data_files (:obj:`str` or :obj:`Sequence` or :obj:`Mapping`, optional): Path(s) to source data file(s).
        download_config (:class:`~download.DownloadConfig`, optional): Specific download configuration parameters.
        download_mode (:class:`DownloadMode`, default ``REUSE_DATASET_IF_EXISTS``): Download/generate mode.
        revision (:class:`~utils.Version` or :obj:`str`, optional): Version of the dataset script to load:

            - For datasets in the `huggingface/datasets` library on GitHub like "squad", the default version of the module is the local version of the lib.
              You can specify a different version from your local version of the lib (e.g. "master" or "1.2.0") but it might cause compatibility issues.
            - For community datasets like "lhoestq/squad" that have their own git repository on the Datasets Hub, the default version "main" corresponds to the "main" branch.
              You can specify a different version that the default "main" by using a commit sha or a git tag of the dataset repository.
        use_auth_token (``str`` or :obj:`bool`, optional): Optional string or boolean to use as Bearer token for remote files on the Datasets Hub.
            If True, will get token from `"~/.huggingface"`.
        **config_kwargs (additional keyword arguments): optional attributes for builder class which will override the attributes if supplied.

    """
    builder = load_dataset_builder(
        path,
        name=config_name,
        data_files=data_files,
        download_config=download_config,
        download_mode=download_mode,
        revision=revision,
        use_auth_token=use_auth_token,
        **config_kwargs,
    )
    extend_dataset_builder_for_streaming(builder, use_auth_token=use_auth_token)
    info = builder.info
    if info.splits is None:
        try:
            download_config = download_config.copy() if download_config else DownloadConfig()
            if use_auth_token is not None:
                download_config.use_auth_token = use_auth_token
            info.splits = {
                split_generator.name: {"name": split_generator.name, "dataset_name": path}
                for split_generator in builder._split_generators(
                    StreamingDownloadManager(base_path=builder.base_path, download_config=download_config)
                )
            }
        except Exception as err:
            raise SplitsNotFoundError("The split names could not be parsed from the dataset config.") from err
    return info


def get_dataset_split_names(
    path: str,
    config_name: Optional[str] = None,
    data_files: Optional[Union[str, Sequence[str], Mapping[str, Union[str, Sequence[str]]]]] = None,
    download_config: Optional[DownloadConfig] = None,
    download_mode: Optional[DownloadMode] = None,
    revision: Optional[Union[str, Version]] = None,
    use_auth_token: Optional[Union[bool, str]] = None,
    **config_kwargs,
):
    """Get the list of available splits for a particular config and dataset.

    Args:
        path (``str``): path to the dataset processing script with the dataset builder. Can be either:

            - a local path to processing script or the directory containing the script (if the script has the same name as the directory),
                e.g. ``'./dataset/squad'`` or ``'./dataset/squad/squad.py'``
            - a dataset identifier on the Hugging Face Hub (list all available datasets and ids with ``datasets.list_datasets()``)
                e.g. ``'squad'``, ``'glue'`` or ``'openai/webtext'``
        config_name (:obj:`str`, optional): Defining the name of the dataset configuration.
        data_files (:obj:`str` or :obj:`Sequence` or :obj:`Mapping`, optional): Path(s) to source data file(s).
        download_config (:class:`~download.DownloadConfig`, optional): Specific download configuration parameters.
        download_mode (:class:`DownloadMode`, default ``REUSE_DATASET_IF_EXISTS``): Download/generate mode.
        revision (:class:`~utils.Version` or :obj:`str`, optional): Version of the dataset script to load:

            - For datasets in the `huggingface/datasets` library on GitHub like "squad", the default version of the module is the local version of the lib.
              You can specify a different version from your local version of the lib (e.g. "master" or "1.2.0") but it might cause compatibility issues.
            - For community datasets like "lhoestq/squad" that have their own git repository on the Datasets Hub, the default version "main" corresponds to the "main" branch.
              You can specify a different version that the default "main" by using a commit sha or a git tag of the dataset repository.
        use_auth_token (``str`` or :obj:`bool`, optional): Optional string or boolean to use as Bearer token for remote files on the Datasets Hub.
            If True, will get token from `"~/.huggingface"`.
        **config_kwargs (additional keyword arguments): optional attributes for builder class which will override the attributes if supplied.

    Example:

    ```py
    >>> from datasets import get_dataset_split_names
    >>> get_dataset_split_names('rotten_tomatoes')
    ['train', 'validation', 'test']
    ```
    """
    info = get_dataset_config_info(
        path,
        config_name=config_name,
        data_files=data_files,
        download_config=download_config,
        download_mode=download_mode,
        revision=revision,
        use_auth_token=use_auth_token,
        **config_kwargs,
    )
    return list(info.splits.keys())
