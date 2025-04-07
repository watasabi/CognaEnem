import pandas as pd
import numpy as np
import re
from collections import Counter


def process_essay_with_conclusion(essay_array):
    """_summary_

    Args:
        essay_array (_type_): _description_

    Returns:
        _type_: _description_
    """
    cleaned_paragraphs = [str(p).strip() for p in essay_array if str(p).strip()]
    if not cleaned_paragraphs:
        return "", ""

    full_text = "\n".join(cleaned_paragraphs)
    conclusion = cleaned_paragraphs[-1] if cleaned_paragraphs else ""

    return full_text, conclusion


def add_processed_essay_columns(df: pd.DataFrame, essay_col: str = "essay"):
    """_summary_

    Args:
        df (pd.DataFrame): _description_
        essay_col (str, optional): _description_. Defaults to "essay".

    Returns:
        _type_: _description_
    """
    processed = df[essay_col].apply(process_essay_with_conclusion)

    df["essay_full"] = processed.apply(lambda x: x[0])
    df["essay_conclusion"] = processed.apply(lambda x: x[1])

    return df


def extract_domain_features(df):
    # NOTE A Multi-aspect Analysis of Automatic Essay Scoring for Brazilian Portuguese papper - 2.2 Features
    # primeira pessoa (pronomes e verbos comuns)
    first_person_pronouns = [
        "eu",
        "meu",
        "minha",
        "me",
        "comigo",
        "nós",
        "nosso",
        "nossa",
    ]
    first_person_verbs = [
        "acho",
        "penso",
        "acredito",
        "creio",
        "considero",
        "entendo",
        "percebo",
        "sinto",
        "imagino",
        "pretendo",
        "desejo",
        "quero",
    ]

    df["first_person_total"] = df["essay_full"].apply(
        lambda x: sum(
            1
            for w in re.findall(r"\b\w+\b", x.lower())
            if w in first_person_pronouns + first_person_verbs
        )
    )

    # enclise (ex: "xxxx-lhe")
    df["enclisis_count"] = df["essay_full"].str.count(
        r"\b\w+-(lhe|la|lo|nos|vos|las|los)\b"
    )

    # pronomes demonstrativos
    demonstrative_pronouns = [
        "este",
        "esta",
        "isto",
        "esse",
        "essa",
        "isso",
        "aquele",
        "aquela",
        "aquilo",
    ]
    df["demonstrative_pronouns"] = df["essay_full"].apply(
        lambda x: sum(
            1 for w in re.findall(r"\b\w+\b", x.lower()) if w in demonstrative_pronouns
        )
    )

    df["tokens_count"] = df["essay_full"].apply(
        lambda x: len(re.findall(r"\b\w+\b", x))
    )

    # Features normalizadas
    df["first_person_per_token"] = df["first_person_total"] / df[
        "tokens_count"
    ].replace(0, 1)
    df["enclisis_per_token"] = df["enclisis_count"] / df["tokens_count"].replace(0, 1)
    df["demonstrative_per_token"] = df["demonstrative_pronouns"] / df[
        "tokens_count"
    ].replace(0, 1)

    return df
